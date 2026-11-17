from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helper.config import get_settings
from stores.llm.LLMFactory import LLMFactory
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMFactory(settings)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)
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