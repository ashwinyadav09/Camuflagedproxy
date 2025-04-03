import asyncio
import aiohttp

async def logout_async(session_cookie: str, session: aiohttp.ClientSession):
    url = "https://student.bennetterp.camu.in/api/logout"
    headers = {
        "Host": "student.bennetterp.camu.in",
        "Cookie": f"connect.sid={session_cookie}",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Clienttzofst": "330",
        "Origin": "https://student.bennetterp.camu.in",
        "Referer": "https://student.bennetterp.camu.in/v2/timetable",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
        "Te": "trailers"
    }
    payload = {"isSessionDestroy": True}

    try:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("isLogOutStatus") == True:
                    print("Logout successful!")
                    return True
            print("Logout failed! Response:", await response.text())
            return False
    except Exception as e:
        print("Error during logout:", str(e))
        return False

def logout(session_cookie: str):
    async def run():
        async with aiohttp.ClientSession() as session:
            return await logout_async(session_cookie, session)
    return asyncio.run(run())