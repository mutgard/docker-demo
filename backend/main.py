from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db, run_migrations
from routes.clients import router as clients_router
from routes.fabrics import router as fabrics_router
from routes.shopping import router as shopping_router
from routes.intake import router as intake_router
from routes.brief import router as brief_router
from routes.appointments import router as appointments_router

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
    run_migrations()
    with Session(engine) as s:
        if not s.exec(select(Client)).first():
            run_seed(s)

app.include_router(clients_router)
app.include_router(fabrics_router)
app.include_router(shopping_router)
app.include_router(intake_router)
app.include_router(brief_router)
app.include_router(appointments_router)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
if os.path.isdir("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        return FileResponse("static/index.html")
