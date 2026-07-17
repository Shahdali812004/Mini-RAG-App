from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helper.config import get_settings
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

@app.on_event("shutdown")
async def shutdown_event():
    app.mongo_conn.close()

app.include_router(base.base_router)
app.include_router(data.data_router)


"""
i need to make functions insert and retrieve data from the database.
 I will use the motor library to interact with MongoDB. 
 The insert function will take a collection name and a document to insert, 
 while the retrieve function will take a collection name and a query to find documents.
"""