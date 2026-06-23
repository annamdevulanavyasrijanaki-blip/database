from fastapi import FastAPI, Depends, HTTPException, Header  # 🌟 FIXED: Added Header here
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import DBStudent, get_db
import jwt 

app = FastAPI()

SECRET_KEY = "MySuperSecretPassword123"
ALGORITHM = "HS256"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StudentSchema(BaseModel):
    name: str
    grade: str

class LoginSchema(BaseModel):
    username: str
    password: str

# 1. LOGIN ROUTE
@app.post("/login")
def login(user_data: LoginSchema):
    if user_data.username == "admin" and user_data.password == "secure123":
        payload = {"username": user_data.username, "role": "admin"}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# 2. PROTECTED DELETE ROUTE
@app.delete("/students/{id}")
def delete_student(id: int, db: Session = Depends(get_db), authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token format")
    
    token = authorization.split(" ")[1]
    
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token tampering detected! Invalid Signature.")

    db_student = db.query(DBStudent).filter(DBStudent.id == id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    db.delete(db_student)
    db.commit()
    return {"message": f"Student successfully deleted by {decoded_payload['username']}"}

# 3. GET ALL STUDENTS
@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    return db.query(DBStudent).all()

# 4. CREATE STUDENT
@app.post("/students")
def create_student(student: StudentSchema, db: Session = Depends(get_db)):
    db_student = DBStudent(name=student.name, grade=student.grade)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

# 5. UPDATE STUDENT
@app.put("/students/{id}")
def update_student(id: int, student_data: StudentSchema, db: Session = Depends(get_db)):
    db_student = db.query(DBStudent).filter(DBStudent.id == id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db_student.name = student_data.name
    db_student.grade = student_data.grade
    db.commit()
    return {"message": "Student Updated"}

# 6. SERVE FRONTEND
@app.get("/")
def serve_frontend():
    return FileResponse("templates/index.html")