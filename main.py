from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from db.config_db import db_client

# Import both routers
# from api.main import api_router  # Existing API routes
from routes.ocr_routes import router as ocr_router  # New OCR routes

# if db_client:
app = FastAPI()

    # CORS setup (keep existing)
origins = [
        "http://localhost",
        "http://localhost:5173",
    ]
    
app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# app.include_router(api_router, prefix="/api/v1")
app.include_router(ocr_router, prefix="/api/v1/ocr")  # New OCR endpoints

@app.get("/")

def root():
        
        return {"hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5500, reload=True)

