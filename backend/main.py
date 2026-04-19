from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db
from routes.clients import router as clients_router
from routes.fabrics import router as fabrics_router
from routes.shopping import router as shopping_router

app = FastAPI(title="Juliette Atelier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://*.railway.app"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    from sqlmodel import Session, select
    from models import Client
    from seed import run_seed
    from database import engine
    create_db()
    with Session(engine) as s:
        if not s.exec(select(Client)).first():
            run_seed(s)

app.include_router(clients_router)
app.include_router(fabrics_router)
app.include_router(shopping_router)

from fastapi.staticfiles import StaticFiles
import os
if os.path.isdir("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
