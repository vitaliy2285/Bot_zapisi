from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.booking import router as booking_router
from app.api.v1.webhooks import router as webhooks_router
from app.core.config import settings

app = FastAPI(title=settings.project_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(booking_router, prefix=settings.api_v1_prefix)
app.include_router(webhooks_router, prefix=settings.api_v1_prefix)
