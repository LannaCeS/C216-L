from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.home import router as books_router
from app.api.routes.login import router as login_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books_router)
app.include_router(login_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
