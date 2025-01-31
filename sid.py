import requests
def get_sid(email:str,password:str):
    login_url = "https://student.bennetterp.camu.in/login/validate"
    payload = {
        "dtype": "M",
        "Email": email,
        "pwd": password
    }

    s = requests.Session()
    response = s.post(login_url, json=payload)
    data = response.json()["output"]["data"]

    #Getting sid
    session_id = s.cookies.get("connect.sid")
    if "logindetails" in data:
        print("Session found:",session_id)
        return session_id
    else:
        print("No SessionID found / Login Failure")
        return None