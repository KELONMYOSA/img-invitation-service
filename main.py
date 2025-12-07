import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import config_editor, invitation

app = FastAPI(
    title="Image generating API",
    contact={"name": "KELONMYOSA", "url": "https://t.me/KELONMYOSA"},
    version="0.0.1",
    root_path="/api",
    docs_url="/docs",
    redoc_url="/docs/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(invitation.router)
app.include_router(config_editor.router)

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 80
    uvicorn.run(app, host=host, port=port)
