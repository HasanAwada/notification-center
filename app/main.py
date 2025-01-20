from fastapi import FastAPI
from app.routers import notifications

app = FastAPI()

app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
