from sqlalchemy.orm import Session
from models import Student, Teacher
import bcrypt

DEMO_STUDENTS = [
    {"student_id": "20250007799", "name": "Aylin Asadi",   "coursework_mark": 48, "final_exam_mark": 49},
    {"student_id": "20250004388", "name": "Bob Smith",       "coursework_mark": 32, "final_exam_mark": 28},
    {"student_id": "20250007089", "name": "Clara Davis",     "coursework_mark": 50, "final_exam_mark": 47},
    {"student_id": "20250003395", "name": "Daniel Brown",    "coursework_mark": 20, "final_exam_mark": 18},
    {"student_id": "20240007451", "name": "Emma Wilson",     "coursework_mark": 38, "final_exam_mark": 41},
    {"student_id": "20240007392", "name": "Frank Miller",    "coursework_mark": 15, "final_exam_mark": 22},
    {"student_id": "20230005625", "name": "Grace Lee",       "coursework_mark": 44, "final_exam_mark": 46},
    {"student_id": "20230004622", "name": "Henry Taylor",    "coursework_mark": 29, "final_exam_mark": 35},
    {"student_id": "20240005633", "name": "Isla Martinez",   "coursework_mark": 42, "final_exam_mark": 39},
    {"student_id": "20240005733", "name": "Jack Anderson",   "coursework_mark": 10, "final_exam_mark": 14},
]

DEMO_EMAIL = "demo@school.com"
DEMO_PASSWORD = "demo1234"

def seed_demo_data(db: Session):
    try:
        teacher = db.query(Teacher).filter(
            Teacher.email == DEMO_EMAIL
        ).first()

        if not teacher:
            hashed = bcrypt.hashpw(
                DEMO_PASSWORD.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            teacher = Teacher(
                name="Demo Teacher",
                email=DEMO_EMAIL,
                hashed_password=hashed
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)

        for s in DEMO_STUDENTS:
            exists = db.query(Student).filter(
                Student.student_id == s["student_id"],
                Student.teacher_id == teacher.id
            ).first()

            if exists:
                continue

            db.add(Student(
                student_id=s["student_id"],
                name=s["name"],
                coursework_mark=s["coursework_mark"],
                final_exam_mark=s["final_exam_mark"],
                total_mark=s["coursework_mark"] + s["final_exam_mark"],
                teacher_id=teacher.id
            ))

        db.commit()
        print("Demo data seeded! Login with demo@school.com / demo1234")

    except Exception as e:
        db.rollback()
        print(f"Seeding skipped: {e}")