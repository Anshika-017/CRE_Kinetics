from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = FastAPI(
    title="Reaction Kinetics Analysis API",
    description=(
        "Transparent integral- and differential-method analysis of batch "
        "reactor concentration-time data. No machine learning is used; all "
        "results are derived from explicit regression on physically derived "
        "kinetic transformations."
    ),
    version="1.0.0",
)

allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"service": "reaction-kinetics-backend", "docs": "/docs"}
