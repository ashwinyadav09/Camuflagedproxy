import asyncio
import aiohttp
from database import get_session_id, get_stu, get_pass

async def mark_attendance_async(session, session_id: str, attendance_id: str, student_id: str):
    url = "https://student.bennetterp.camu.in/api/Attendance/record-online-attendance"
    headers = {
        "Cookie": f"connect.sid={session_id}",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://student.bennetterp.camu.in",
        "Referer": "https://student.bennetterp.camu.in/v2/timetable",
    }
    payload = {
        "attendanceId": attendance_id,
        "isMeetingStarted": True,
        "StuID": student_id,
        "offQrCdEnbld": True
    }

    try:
        async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as response:
            data = await response.json()
            if data["output"]["data"] and data["output"]["data"]["code"] in ["ATTENDANCE_ALREADY_MARKED", "SUCCESS"]:
                return True
            return False
    except Exception as e:
        print(f"Error for {student_id}: {e}")
        return False

async def refresh_session_id(session, email, password):
    login_url = "https://student.bennetterp.camu.in/login/validate"
    payload = {"dtype": "M", "Email": email, "pwd": password}
    async with session.post(login_url, json=payload) as response:
        session_id = response.cookies.get("connect.sid").value if "connect.sid" in response.cookies else None
        if session_id:
            from database import update_session_id
            update_session_id(email, session_id)
        return session_id

async def start_mark(qr_id: str):
    import sqlite3
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT email, password FROM users')
    users = c.fetchall()
    conn.close()

    async with aiohttp.ClientSession() as session:
        tasks = []
        for email, password in users[:200]:  # Limit to 200 users
            sid = get_session_id(email)
            if not sid:
                sid = await refresh_session_id(session, email, password)
            student_id = get_stu(email)
            if sid and student_id:
                tasks.append(mark_attendance_async(session, sid, qr_id, student_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

def run_start_mark(qr_id: str):
    return asyncio.run(start_mark(qr_id))