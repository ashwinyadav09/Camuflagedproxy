import requests
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from sid import *
from database import *

def mark_attendance(session_id: str, attendance_id: str, student_id: str):
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

    response = requests.post(url, headers=headers, json=payload)
    try:
        response = response.json()  # Return the response as JSON
        if response.get("output", {}).get("data") is not None:
            code = response["output"]["data"].get("code")
            if code == "ATTENDANCE_ALREADY_MARKED" or code == "SUCCESS":
                return True
            else:
                return False
        return False
    except ValueError:
        print("Failed to parse response as JSON.")
        return False

def start_mark(qr_id: str):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT email FROM users')
    attendance_id = qr_id
    ems = c.fetchall()

    def mark_for_user(em):
        sid = get_sid(em, get_pass(em))
        student_id = get_stu(em)
        return mark_attendance(sid, attendance_id, student_id)

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(mark_for_user, [em[0] for em in ems]))

    return results
