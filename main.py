from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from config import config
from passlib.context import CryptContext
from bson import ObjectId
from typing import Optional
"""
DC_NAME = "ericgwhuang"
URI = f"mongodb+srv://{dc_name}:{dc_name}@gdg-mongodb.chih-hao.xyz/{dc_name}?authMechanism=SCRAM-SHA-256&tls=true"
TLS_CA_FILE = "mongodb-bundle.pem"
client = MongoClient(uri, tlsCAFile=tls_ca_file)
db = client[dc_name]
"""
uri = config.URI
client = MongoClient(uri)
db = client["tricking_db"]
users = db["users"]
app = FastAPI()

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    name: str
    password: str
    email: str
    phone: str
    sex: str|bool
    age: int

class UserUpdate(BaseModel):
    uid: str
    name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    sex: Optional[str|bool] = None
    age: Optional[int] = None

class UserLogin(BaseModel):
    account: str
    password: str

def _hash_pwd(original_pwd: str) -> str:
    return _pwd_context.hash(original_pwd)

def _verify_pwd(checked_pwd: str, hashed_pwd: str)-> bool:
    return _pwd_context.verify(checked_pwd, hashed_pwd)

@app.delete("/delete-all")
async def delete_all():
    users.delete_many({})
    return {"status_code": True}

# 創建帳號 API

@app.post("/api/create-account")
async def create_account(user: UserCreate):
    if users.find_one({"name": user.name}):
        raise HTTPException(status_code=400, detail="使用者已存在")
    if users.find_one({"phone": user.phone}):
        raise HTTPException(status_code=400, detail="使用者已存在")
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="使用者已存在")

    if type(user.sex) != bool:
        if user.sex.lower() == "male":
            user.sex = False
        elif user.sex.lower() == "female":
            user.sex = True
        else:
            raise HTTPException(status_code=401, detail="不合理性別")
    user.password = _hash_pwd(user.password)
    users.insert_one(user.model_dump())
    return {"status_code": True}

@app.get("/api/get-account/{uid}")
async def get_account(uid: str):
    stored_user = users.find_one({"_id": ObjectId(uid)})
    if stored_user:
        stored_user.pop("_id")
        return stored_user
    else:
        raise HTTPException(status_code=404, detail="找不到使用者")

@app.post("/api/update-account")
async def update_account(user: UserUpdate):
    if users.find_one({"name": user.name}):
        raise HTTPException(status_code=400, detail="使用者已存在")
    if users.find_one({"phone": user.phone}):
        raise HTTPException(status_code=400, detail="使用者已存在")
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="使用者已存在")

    if type(user.sex) == str:
        if user.sex.lower() == "male":
            user.sex = False
        elif user.sex.lower() == "female":
            user.sex = True
        else:
            raise HTTPException(status_code=401, detail="不合理性別")

    updated_user = {}
    for key, val in user.model_dump().items():
        if val!=None:
            updated_user[key] = val
    if updated_user:
        result = users.update_one({"_id": ObjectId(user.uid)}, {"$set": updated_user})
        if result.modified_count > 0:
            return {"status_code": True}
        else:
            raise HTTPException(status_code=404, detail="找不到使用者")
    else:
        return {"status_code": False}
        
@app.delete("/api/delete-account/{uid}")
async def delete_account(uid: str):
    users.delete_one({"_id": ObjectId(uid)})
    return {"status_code": True}

@app.post("/api/login")
async def login(user: UserLogin):
    stored_user = users.find_one({"name": user.account})
    if not stored_user:
        stored_user = users.find_one({"phone": user.account})
    if not stored_user:
        stored_user = users.find_one({"email": user.account})
    if stored_user and _verify_pwd(user.password, stored_user["password"]):
        return {"status_code": True, "uid": str(stored_user["_id"])}
    else:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
