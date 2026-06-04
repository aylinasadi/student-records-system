from pydantic import BaseModel, EmailStr


class TeacherSignup(BaseModel):
    name: str
    email: EmailStr
    password: str


class TeacherLogin(BaseModel):
    email: EmailStr
    password: str


class TeacherOut(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str



class StudentCreate(BaseModel):
    student_id: str
    name: str
    coursework_mark: int
    final_exam_mark: int


class StudentOut(BaseModel):
    id: int
    student_id: str
    name: str
    coursework_mark: int
    final_exam_mark: int
    total_mark: int

    class Config:
        from_attributes = True