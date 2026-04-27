from fastapi import FastAPI

from app.db.database import engine
from app.routers import users
from app.telemetry import setup_telemetry

app = FastAPI(title="o11y")

setup_telemetry(app, engine)
app.include_router(users.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
