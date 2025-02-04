import httpx
import asyncio
import sqlite3
from qr import *
from sid import *
from database import *

async def mark_attendance(session_id: str, attendance_id: str, student_id: str):
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
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response_json = response.json()
            if response_json.get("output", {}).get("data") is not None:
                code = response_json["output"]["data"].get("code", "")
                return code in ["ATTENDANCE_ALREADY_MARKED", "SUCCESS"]
            return False
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return False

async def process_attendance(email, attendance_id):
    sid = get_sid(email, get_pass(email))
    student_id = get_stu(email)
    return await mark_attendance(sid, attendance_id, student_id)

async def start_mark(qr_id: str):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT email FROM users')
    attendance_id = qr_id
    ems = [em[0] for em in c.fetchall()]
    conn.close()
    
    tasks = [process_attendance(email, attendance_id) for email in ems]
    results = await asyncio.gather(*tasks)
    return results
