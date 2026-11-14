from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import users
from app.core.config import CORS_ORIGINS

app = FastAPI()
app.include_router(users.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=[ "GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],

)
