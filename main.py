# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from api.db.database import Base, engine
from api.v1.routes.auth import router as auth_router
from api.v1.routes.dashboard import router as dashboard_router
from api.v1.routes.course import router as course_router
from api.v1.routes.log import router as log_router

load_dotenv()

# Base.metadata.drop_all(bind=engine)
# print("All tables dropped")

# Recreate tables from models
Base.metadata.create_all(bind=engine)
print("All tables created")

app = FastAPI(title="Trak API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["health"])
def health_check():
    return {"message": f"Server is running and healthy"}

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
app.include_router(course_router, prefix="/courses", tags=["courses"])
app.include_router(log_router, prefix="/logs", tags=["logs"])