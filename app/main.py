import json
import os
import random
from fastapi import FastAPI, Query, Body, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core import create_jwt

app = FastAPI(title="FreeFire JWT Static Factory", version="3.0.0")

ACCOUNTS_FILE = "GuestAccounts.json"

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r") as f:
            return json.load(f)
    return {}

accounts_db = load_accounts()

class TokenRequest(BaseModel):
    uid: Optional[str] = None
    password: Optional[str] = None
    region: Optional[str] = None
    access_token: Optional[str] = None
    open_id: Optional[str] = None

@app.get("/")
async def root():
    return {
        "Status": "JWT Generator Live Static Load Balancer Vercel 💀",
        "Loaded_Regions": list(accounts_db.keys()),
        "Endpoints": "/api/token?region=IND OR /api/token?uid=xxx&password=xxx OR /api/token?access_token=xxx&open_id=yyy"
    }

@app.get("/api/token")
async def get_token(
    region: Optional[str] = Query(None),
    uid: Optional[str] = Query(None), 
    password: Optional[str] = Query(None),
    access_token: Optional[str] = Query(None),
    open_id: Optional[str] = Query(None)
):
    
    # Mode 3 Direct Access Token Bypass Login
    if access_token and open_id:
        target_region = (region or "IND").upper()
        try:
            result = await create_jwt(uid="Bypass", password="None", region=target_region, bypass_token=access_token, bypass_id=open_id)
            response_data = {"Developer": "BITTU__DEV", "Status": "Bypass Mode Active"}
            response_data.update(result)
            return response_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Mode 1 Direct Uid And Password Login
    elif uid and password:
        target_region = (region or "IND").upper()
        try:
            result = await create_jwt(uid, password, target_region)
            response_data = {"Developer": "BITTU__DEV", "Uid": uid, "Password": password}
            response_data.update(result)
            return response_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Mode 2 Random Account From Region Pool
    elif region:
        target_region = region.upper()
        
        if target_region not in accounts_db or not accounts_db[target_region]:
            raise HTTPException(status_code=404, detail=f"No Accounts Available For Region {target_region}")
            
        account_pool = accounts_db[target_region]
        
        max_retries = 2
        last_error = "Unknown Error"
        
        for attempt in range(max_retries):
            active_account = random.choice(account_pool)
            active_uid = active_account.get("uid")
            active_pwd = active_account.get("password")
            
            if not active_uid or not active_pwd:
                continue 
                
            try:
                result = await create_jwt(active_uid, active_pwd, target_region)
                response_data = {
                    "Developer": "BITTU__DEV",
                    "Status": "Active",
                    "Region": target_region,
                    "Attempt": attempt + 1,
                    "Uid": active_uid,
                    "Password": active_pwd
                }
                response_data.update(result)
                return response_data
            except Exception as e:
                last_error = str(e)
                
        raise HTTPException(status_code=500, detail=f"Extraction Failed After {max_retries} Attempts Last Error {last_error}")

    else:
        raise HTTPException(status_code=400, detail="Strictly Require Uid And Password OR Region OR Access Token And Open Id Parameters To Proceed")

@app.post("/api/token")
async def post_token(payload: TokenRequest = Body(...)):
    return await get_token(
        region=payload.region, 
        uid=payload.uid, 
        password=payload.password,
        access_token=payload.access_token,
        open_id=payload.open_id
    )
