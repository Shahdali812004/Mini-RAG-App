from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import settings
app = FastAPI()

@app.lifespan("startup")
async def startup_event():
    settings = settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URL)
    app.db_client = app.mongo_conn[settings.MONGODBDB_DATABASE]

@app.lifespan("shutdown")
async def shutdown_event():
    app.mongo_conn.close()

app.include_router(base.base_router)
app.include_router(data.data_router)
