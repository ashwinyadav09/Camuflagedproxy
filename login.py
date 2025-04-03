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

    try:
        async with session.post(login_url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status != 200:
                print(f"Login failed: HTTP {response.status}")
                return False
            resp_data = await response.json()
            session_id = response.cookies.get("connect.sid").value if "connect.sid" in response.cookies else None

        if not resp_data or "output" not in resp_data or "data" not in resp_data["output"]:
            print("Login failed: Invalid response structure.")
            return False

        data = resp_data["output"]["data"]
        if "logindetails" not in data:
            print(f"Login failed: No logindetails in response. Code: {data.get('code')}")
            return False

        delete_existing_user(email)
        email_prefix = email.split("@")[0].upper()
        email_end = email.split("@")[1]
        email = email_prefix + "@" + email_end
        delete_existing_user(email)
        
        new_user(name=data["logindetails"]["Name"], reg_no=email_prefix, email=email, password=password)
        store_js(resp_data, email)
        if session_id:
            try:
                update_session_id(email, session_id)
                print(f"Session ID updated for {email}.")
            except Exception as e:
                print(f"Failed to update session_id for {email}: {e}")
                # Continue despite failure since user is registered
        print(f"User {email} registered successfully.")
        return True

    except aiohttp.ClientError as e:
        print(f"Network error during login: {e}")
        return False
    except KeyError as e:
        print(f"Response parsing error: Missing key {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during login: {e}")
        return False

def login_and_save_data(email: str, password: str):
    async def run():
        async with aiohttp.ClientSession() as session:
            return await login_and_save_data_async(email, password, session)
    try:
        return asyncio.run(run())
    except Exception as e:
        print(f"Error in login_and_save_data: {e}")
        return False

async def login_check_async(email: str, password: str, session: aiohttp.ClientSession):
    login_url = "https://student.bennetterp.camu.in/login/validate"
    payload = {"dtype": "M", "Email": email, "pwd": password}

    try:
        async with session.post(login_url, json=payload) as response:
            resp_data = await response.json()
            return "logindetails" in resp_data.get("output", {}).get("data", {})
    except Exception as e:
        print(f"Error in login_check_async: {e}")
        return False

def login_check(email: str, password: str):
    async def run():
        async with aiohttp.ClientSession() as session:
            return await login_check_async(email, password, session)
    return asyncio.run(run())