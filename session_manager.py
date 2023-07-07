import config

import json
import time
import requests

cst = ""
security_token = ""

def login():
    global cst
    global security_token
    print("Attempting IG login")
    data = {"identifier": config.igUname(), "password": config.igPword()}
    r = requests.post(config.igEnpoint()+"/session", data=json.dumps(data), headers=getHeaders())
    if r.status_code == 200:
        print("Logged into IG account")
        headers_json = dict(r.headers)
        cst = headers_json["CST"]
        print("CST : " + cst)
        security_token = headers_json["X-SECURITY-TOKEN"]
        print("X-SECURITY-TOKEN : " + security_token)
    else:
        print("Failed to login with error code: "+str(r.status_code))
        raise Exception(r.text)

def selectAccount():
    print("Switching to account: "+config.igAccount())
    data = {"accountId": config.igAccount(), "defaultAccount": "True"}

    r = requests.put(
        config.igEnpoint()+"/session",
        data=json.dumps(data),
        headers=getHeaders(1))

    if r.status_code == 200:
        pass
    elif r.status_code == 412:
        print("Already logged into given account")
    else:
        print("Account switch error code: "+str(r.status_code))
        raise Exception(r.text)

def logout():
    global cst
    global security_token
    print("Logging out")
    r = requests.delete(
        config.igEnpoint()+"/session",
        data=json.dumps({}),
        headers=getHeaders(1))
    if r.status_code == 204:
        print("Logged out successfully")
        cst = ""
        security_token = ""
    else:
        print("Failed to logout with code: "+str(r.status_code))
        raise Exception(r.text)

def getHeaders(version = 2):
    time.sleep(2.5)
    headers = {'Content-Type': 'application/json; charset=utf-8',
       'Accept': 'application/json; charset=utf-8',
       'X-IG-API-KEY': config.igKey(),
       'Version': str(version),
       'CST': cst,
       'X-SECURITY-TOKEN': security_token}
    return headers

if __name__ == "__main__":
    login()
    selectAccount()
    logout()