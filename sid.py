import asyncio
import aiohttp

async def get_sid(email: str, password: str, session: aiohttp.ClientSession):
    login_url = "https://student.bennetterp.camu.in/login/validate"
    payload = {
        "dtype": "M",
        "Email": email,
        "pwd": password
    }

    async with session.post(login_url, json=payload) as response:
        data = await response.json()
        session_id = response.cookies.get("connect.sid").value if "connect.sid" in response.cookies else None
        if "output" in data and "data" in data["output"] and "logindetails" in data["output"]["data"]:
            print("Session found:", session_id)
            return session_id
        else:
            print("No SessionID found / Login Failure")
            return None

def get_sid_sync(email: str, password: str):
    async def run():
        async with aiohttp.ClientSession() as session:
            return await get_sid(email, password, session)
    return asyncio.run(run())