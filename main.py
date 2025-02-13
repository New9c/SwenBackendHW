from fastapi import FastAPI
from pymongo import MongoClient

dc_name = "ericgwhuang"
uri = f"mongodb+srv://{dc_name}:{dc_name}@gdg-mongodb.chih-hao.xyz/{dc_name}?authMechanism=SCRAM-SHA-256&tls=true"
tls_ca_file = "mongodb-bundle.pem"
client = MongoClient(uri, tlsCAFile=tls_ca_file)
db = client[dc_name]
users = db["users"]
app = FastAPI()


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
