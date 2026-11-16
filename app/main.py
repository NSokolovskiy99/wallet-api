from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine
from app.routers.wallets import router as wallets_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="Wallet REST API",
    description="Асинхронный сервис управления балансом кошельков",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(wallets_router)