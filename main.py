from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from config import config
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

class UserCreate(BaseModel):
    name: str
    password: str
    email: str
    phone: str
    sex: str|bool
    age: int


@app.get("/count")
async def count():
    return {"msg" : f"There are {users.count_documents({})} users"}

@app.delete("/delete-all")
async def delete_all():
    users.delete_many({})
    return {"status_code": True}

@app.post("/add-one")
async def add_one():
    users.insert_one({"username": "aitnyaoytwufwyuw"})
    return {"status_code": True}

# 創建帳號 API
@app.post("/api/create-account")
async def create_account(user: UserCreate):
    if users.find_one({"name": user.name}):
        raise HTTPException(status_code=400, detail="使用者名稱已存在")
    if type(user.sex) != bool:
        if user.sex.lower() == "male":
            user.sex = False
        elif user.sex.lower() == "female":
            user.sex = True
        else:
            raise HTTPException(status_code=401, detail="不合理性別")
    users.insert_one(user.model_dump())
    return {"status_code": True}
