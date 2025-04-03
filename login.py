import os
import json
import sqlite3
import asyncio
import aiohttp
from database import *

def delete_existing_user(email):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
    conn.close()

async def login_and_save_data_async(email: str, password: str, session: aiohttp.ClientSession):
    login_url = "https://student.bennetterp.camu.in/login/validate"
    payload = {"dtype": "M", "Email": email, "pwd": password}

    async with session.post(login_url, json=payload) as response:
        resp_data = await response.json()
        session_id = response.cookies.get("connect.sid").value if "connect.sid" in response.cookies else None

    if resp_data and "output" in resp_data and "data" in resp_data["output"]:
        data = resp_data["output"]["data"]
        if "logindetails" in data:
            delete_existing_user(email)
            email_prefix = email.split("@")[0].upper()
            email_end = email.split("@")[1]
            email = email_prefix + "@" + email_end
            delete_existing_user(email)
            new_user(name=data["logindetails"]["Name"], reg_no=email_prefix, email=email, password=password)
            store_js(resp_data, email)
            if session_id:
                update_session_id(email, session_id)  # Store session ID
            return True
        elif data.get("code") == "INVALID_CRED":
            print("Login failed: Invalid credentials.")
            return False
    print("Login failed: Unexpected response structure.")
    return False

def login_and_save_data(email: str, password: str):
    async def run():
        async with aiohttp.ClientSession() as session:
            return await login_and_save_data_async(email, password, session)
    return asyncio.run(run())

async def login_check_async(email: str, password: str, session: aiohttp.ClientSession):
    login_url = "https://student.bennetterp.camu.in/login/validate"
    payload = {"dtype": "M", "Email": email, "pwd": password}

    async with session.post(login_url, json=payload) as response:
        resp_data = await response.json()

    if resp_data and "output" in resp_data and "data" in resp_data["output"]:
        data = resp_data["output"]["data"]
        if "logindetails" in data:
            return True
        elif data.get("code") == "INVALID_CRED":
            print("Login failed: Invalid credentials.")
            return False
    return False

def login_check(email: str, password: str):
    async def run():
        async with aiohttp.ClientSession() as session:
            return await login_check_async(email, password, session)
    return asyncio.run(run())