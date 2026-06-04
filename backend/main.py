import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from database import engine, SessionLocal
import models
from routes import auth_routes, student_routes
from seed import seed_demo_data

models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="Student Records API (upgraded final project for BCS102)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(student_routes.router)


@app.on_event("startup")
def startup():
    retries = 5
    while retries > 0:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            models.Base.metadata.create_all(bind=engine)
            print("Database connected and tables created!")

            # seed demo data
            db = SessionLocal()
            try:
                seed_demo_data(db)
            finally:
                db.close()

            break

        except Exception as e:
            retries -= 1
            print(f"Database not ready, retrying... ({retries} retries left)")
            time.sleep(3)
    if retries == 0:
        raise Exception("Could not connect to database after multiple retries")


@app.get("/")
def root():
    return {"message": "Student Records API is running"}