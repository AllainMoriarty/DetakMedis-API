from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routers import auth, chat, poli, disease, doctor, medical_image, diagnosis
from app.core.database import engine, Base
import app.models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Detak Medis API",
    description="API for Detak Medis application",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; you can specify specific domains like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(poli.router)
app.include_router(disease.router)
app.include_router(doctor.router)
app.include_router(medical_image.router)
app.include_router(diagnosis.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Detak Medis API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)