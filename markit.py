import aiohttp
import asyncio
import sqlite3
from typing import List, Optional
from sid import *
from database import *
from qr import *

async def mark_attendance(session_id: str, attendance_id: str, student_id: str, session: aiohttp.ClientSession) -> bool:
    """Mark attendance for a student."""
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
        async with session.post(url, headers=headers, json=payload) as response:
            response_data = await response.json()
            if response_data.get("output", {}).get("data") is not None:
                code = response_data["output"]["data"].get("code", "")
                return code in ["ATTENDANCE_ALREADY_MARKED", "SUCCESS"]
            return False
    except Exception as e:
        print(f"Error marking attendance for {student_id}: {e}")
        return False

async def process_student(email: str, attendance_id: str, session: aiohttp.ClientSession) -> bool:
    """Process attendance marking for a single student."""
    try:
        sid = get_sid(email, get_pass(email))
        student_id = get_stu(email)
        return await mark_attendance(sid, attendance_id, student_id, session)
    except Exception as e:
        print(f"Error processing student {email}: {e}")
        return False

async def start_mark(qr_id: str) -> List[bool]:
    """Start marking attendance for all students."""
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT email FROM users')
        emails = [em[0] for em in c.fetchall()]
        conn.close()

        async with aiohttp.ClientSession() as session:
            tasks = [process_student(em, qr_id, session) for em in emails]
            results = await asyncio.gather(*tasks)
            return results
    except Exception as e:
        print(f"Error in start_mark: {e}")
        return [False] * len(emails)