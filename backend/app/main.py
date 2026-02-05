from fastapi import FastAPI

from app.api.routes import router
from app.store.db import init_db


app = FastAPI(title="Bot-Likelihood Analyzer", version="0.1")
app.include_router(router)


@app.on_event("startup")
def startup() -> None:
    init_db()
