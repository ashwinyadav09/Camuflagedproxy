import requests
from sid import *
from database import *

def mark_attendance(session_id: str, attendance_id: str, student_ids: list):
    url = "https://student.bennetterp.camu.in/api/Attendance/record-online-attendance"
    headers = {
        "Cookie": f"connect.sid={session_id}",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://student.bennetterp.camu.in",
        "Referer": "https://student.bennetterp.camu.in/v2/timetable",
    }
    
    # Construct payload for all students at once
    payload = [{
        "attendanceId": attendance_id,
        "isMeetingStarted": True,
        "StuID": student_id,
        "offQrCdEnbld": True
    } for student_id in student_ids]

    response = requests.post(url, headers=headers, json=payload)
    
    try:
        response = response.json()  # Convert response to JSON
        success_list = []
        
        for res in response["output"]["data"]:
            if res.get("code") in ["ATTENDANCE_ALREADY_MARKED", "SUCCESS"]:
                success_list.append(True)
            else:
                success_list.append(False)

        return success_list  # List of success/failure for each student
    except ValueError:
        print("Failed to parse response as JSON.")
        return [False] * len(student_ids)


import sqlite3
from qr import *

def start_mark(qr_id: str):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Fetch all registered students' emails
    c.execute('SELECT email FROM users')
    emails = [em[0] for em in c.fetchall()]
    
    attendance_id = qr_id  # Use the scanned QR ID
    student_ids = [get_stu(em) for em in emails]  # Get all student IDs
    
    if not student_ids:
        return []  # No students found
    
    # Get session ID using any one student's credentials (assuming all share a session)
    sid = get_sid(emails[0], get_pass(emails[0])) if emails else None
    
    if not sid:
        return [False] * len(student_ids)  # Return failure if no session
    
    return mark_attendance(sid, attendance_id, student_ids)
