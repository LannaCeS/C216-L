import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(payload: LoginRequest):
    expected_email = os.getenv("SINGLE_USER_EMAIL")
    expected_password = os.getenv("SINGLE_USER_PASSWORD")

    if not expected_email or not expected_password:
        raise HTTPException(status_code=500, detail="Credentials not configured on the server.")

    if payload.email != expected_email or payload.password != expected_password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return {"authenticated": True}