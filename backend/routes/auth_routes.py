from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/signup", response_model=schemas.TeacherOut)
def signup(teacher: schemas.TeacherSignup, db: Session=Depends(get_db)):
    existing = db.query(models.Teacher).filter(models.Teacher.email == teacher.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_teacher = models.Teacher(name=teacher.name, email=teacher.email, hashed_password=auth.hash_password(teacher.password))
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)

    return new_teacher


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.TeacherLogin, db: Session=Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.email == credentials.email).first()
    if not teacher or not auth.verify_password(credentials.password, teacher.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = auth.create_access_token(data={"sub": teacher.email})
    return {"access_token": token, "token_type": "bearer"}