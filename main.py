from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from backend.database.base import engine
from backend.database.models import Base

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"


def _migrate_users(connection) -> None:
    columns = [row[1] for row in connection.execute(text("PRAGMA table_info(users)"))]
    if "delivery_address" not in columns:
        connection.execute(text("ALTER TABLE users ADD COLUMN delivery_address VARCHAR(500)"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_users)
    yield


app = FastAPI(lifespan=lifespan)

import backend.endpoints.restaurants
import backend.endpoints.cart
import backend.endpoints.order
import backend.endpoints.users
import backend.endpoints.auth
import backend.endpoints.root


@app.get("/")
async def home():
    return FileResponse(FRONTEND_DIR / "home.html")


app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="localhost",
        port=9000,
        reload=True,
    )
