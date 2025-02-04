import requests
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
        response=response.json()  # Return the response as JSON
        try:
            if response["output"]["data"]!=None:
                #print("Attendance Response:", response["output"]["data"]["code"])
                if response["output"]["data"]["code"]=="ATTENDANCE_ALREADY_MARKED" or response["output"]["data"]["code"]=="SUCCESS":
                    return True
                else:
                    return False
            else:
                #print("Failed to mark attendance.")
                return False
        except Exception as e:
            print(e)
            return False
    except ValueError:
        print("Failed to parse response as JSON.")
        return False


import sqlite3
from qr import *
def start_mark(qr_id:str):
    conn = sqlite3.connect('database.db')
    c=conn.cursor()
    c.execute('SELECT email FROM users')
    attendance_id=qr_id
    ems=c.fetchall()
    l=[]
    for em in ems:
        em=em[0]
        sid = get_sid(em,get_pass(em))
        student_id = get_stu(em)
        l.append(mark_attendance(sid, attendance_id, student_id))
    return l