import asyncio
import aiohttp
import json
from database import *
from datetime import datetime

async def fetch_timetable_headerless(sid, json_payload, session: aiohttp.ClientSession):
    api_url = "https://student.bennetterp.camu.in/api/Timetable/get"
    cookies = {
        "connect.sid": sid
    }

    # Fetch today's date in the required format (YYYY-MM-DD)
    today_date = datetime.now().strftime("%Y-%m-%d")

    # Add additional fields to the payload
    json_payload.update({
        "enableV2": True,
        "start": today_date,
        "end": today_date,
        "schdlTyp": "slctdSchdl",
        "isShowCancelledPeriod": True,
        "isFromTt": True
    })
    
    try:
        async with session.post(api_url, cookies=cookies, json=json_payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error: Received status code {response.status}")
                return None
    except aiohttp.ClientError as e:
        print(f"Request failed: {e}")
        return None

def fetch_timetable_headerless_sync(sid, json_payload):
    async def run():
        async with aiohttp.ClientSession() as session:
            return await fetch_timetable_headerless(sid, json_payload, session)
    return asyncio.run(run())