from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from db.config_db import db_client

# Import OCR router
from routes.ocr_routes import router as ocr_router  # New OCR routes

app = FastAPI()

# Updated CORS settings to allow requests from the MERN app (http://localhost:5000)
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Register routers
app.include_router(ocr_router, prefix="/api/v1/ocr")  # OCR endpoints

@app.get("/")
def root():
    return {"hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5120, reload=True)
