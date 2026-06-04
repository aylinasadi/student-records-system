from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_teacher
import models, schemas

router = APIRouter(prefix="/students", tags=["students"])



@router.post("/", response_model=schemas.StudentOut)
def add_student(student: schemas.StudentCreate, db: Session=Depends(get_db), teacher=Depends(get_current_teacher)):
    existing = db.query(models.Student).filter(models.Student.student_id == student.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    
    if not (len(student.student_id) == 11 and student.student_id.isdigit()):
        raise HTTPException(status_code=400, detail="student ID must be exactly 11 digits")
    
    if not (0 <= student.coursework_mark <= 50):
        raise HTTPException(status_code=400, detail="coursework mark must be between 0 and 50")
    
    if not (0 <= student.final_exam_mark <= 50):
        raise HTTPException(status_code=400, detail="final exam mark must be between 0 and 50")
    
    total = student.coursework_mark + student.final_exam_mark
    
    new_student = models.Student(
        student_id=student.student_id,
        name=student.name,
        coursework_mark=student.coursework_mark,
        final_exam_mark=student.final_exam_mark,
        total_mark=total,
        teacher_id=teacher.id
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


@router.get("/", response_model=list[schemas.StudentOut])
def get_students(sort_by: str="name", db: Session=Depends(get_db), teacher=Depends(get_current_teacher)):
    students = db.query(models.Student).filter(models.Student.teacher_id == teacher.id).all()
    
    if sort_by == "name":
        students = insertion_sort_by_name(students)
    elif sort_by == "id":
        students = selection_sort_by_id(students)
    elif sort_by == "total":
        students = bubble_sort_by_total(students)

    return students


@router.get("/search", response_model=schemas.StudentOut)
def search_students(target_id: str, method: str="linear", db: Session=Depends(get_db), teacher=Depends(get_current_teacher)):
    students = db.query(models.Student).filter(models.Student.teacher_id == teacher.id).all()
    
    if method == "linear":
        result, comparisons = linear_search(students, target_id)
    elif method == "binary":
        students = selection_sort_by_id(students)
        result, comparisons = binary_search(students, target_id)
    else:
        raise HTTPException(status_code=400, detail="method must be 'linear' or 'binary'")
    
    if result is None:
        raise HTTPException(status_code=404, detail=f"Student with ID {target_id} not found after {comparisons} comparisons")
    
    return result


@router.delete("/{student_id}")
def delete_student(student_id: str, db: Session=Depends(get_db), teacher=Depends(get_current_teacher)):
    student = db.query(models.Student).filter(models.Student.student_id == student_id, models.Student.teacher_id == teacher.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    return {"detail": "Student deleted successfully"}



def bubble_sort_by_total(students):
    students = students.copy()
    n = len(students)
    for i in range(n - 1):
        swapped = False
        for j in range(0, n - i - 1):
            if students[j].total_mark > students[j + 1].total_mark:
                students[j], students[j + 1] = students[j + 1], students[j]
                swapped = True
        if not swapped:
            break
    return students

def insertion_sort_by_name(students):
    students = students.copy()
    for i in range(1, len(students)):
        item = students[i]
        j = i - 1
        while j >= 0 and students[j].name > item.name:
            students[j + 1] = students[j]
            j -= 1
        students[j + 1] = item
    return students

def selection_sort_by_id(students):
    students = students.copy()
    n = len(students)
    for i in range(n):
        minn = i
        for j in range(i + 1, n):
            if students[j].student_id < students[minn].student_id:
                minn = j
        students[i], students[minn] = students[minn], students[i]
    return students


def linear_search(students, target_id):
    comparisons = 0
    for student in students:
        comparisons += 1
        if student.student_id == target_id:
            return student, comparisons
    return None, comparisons

def binary_search(students, target_id):
    low, high = 0, len(students) - 1
    comparisons = 0
    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        if students[mid].student_id == target_id:
            return students[mid], comparisons
        elif students[mid].student_id < target_id:
            low = mid + 1
        else:
            high = mid - 1
    return None, comparisons