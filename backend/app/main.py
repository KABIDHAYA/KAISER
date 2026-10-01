from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth_router, analysis, history, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ReviewSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(analysis.router)
app.include_router(history.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {"message": "ReviewSense API is running"}
