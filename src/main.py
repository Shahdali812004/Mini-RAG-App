from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv() # to load environment variables from .env file in the system
from src.routes.base import base_router
app = FastAPI()

app.include_router(base_router)