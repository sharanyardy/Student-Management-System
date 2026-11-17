from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from fastapi.responses import RedirectResponse
import sqlite3

app = FastAPI()

templates = Jinja2Templates(directory="templates")

def get_connection():
    return sqlite3.connect("students.db")

def create_table():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            marks INTEGER,
            course TEXT,
            image TEXT,
            status INTEGER
        )
    """)
    connection.commit()
    connection.close()

create_table()

class Student(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    age: int = Field(ge=10, le=100)
    gender: str
    marks: int = Field(ge=0, le=100)
    course: str
    image: str = ""
    status: int

@app.get("/")
def home(req: Request):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    connection.close()

    return templates.TemplateResponse(
        request=req,
        name="home.html",
        context={"stds": students}
    )

@app.get("/students/{std_id}")
def single_std(req: Request, std_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (std_id,))
    student = cursor.fetchone()
    connection.close()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return templates.TemplateResponse(
        request=req,
        name="single_std.html",
        context={"std": student}
    )

@app.post("/std/delete/{std_id}")
def delete_std(std_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (std_id,))
    connection.commit()
    connection.close()

    return RedirectResponse("/", status_code=303)

@app.get("/student/add")
def send_std_form(req: Request):
    return templates.TemplateResponse(
        request=req,
        name="add_student.html",
        context={}
    )

@app.post("/student/add")
def create_std(
    name: str = Form(),
    age: int = Form(),
    gender: str = Form(),
    marks: int = Form(),
    course: str = Form(),
    image: str = Form(),
    status: int = Form()
):
    std_obj = Student(
        name=name,
        age=age,
        gender=gender,
        marks=marks,
        course=course,
        image=image,
        status=status
    )

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO students (name, age, gender, marks, course, image, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        std_obj.name,
        std_obj.age,
        std_obj.gender,
        std_obj.marks,
        std_obj.course,
        std_obj.image,
        std_obj.status
    ))
    connection.commit()
    connection.close()

    return RedirectResponse("/", status_code=303)

@app.get("/students/edit/{std_id}")
def edit_std(req: Request, std_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (std_id,))
    student = cursor.fetchone()
    connection.close()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return templates.TemplateResponse(
        request=req,
        name="edit_std.html",
        context={
            "std": student,
            "std_id": std_id
        }
    )

@app.post("/students/edit/{std_id}")
def update_std(
    std_id: int,
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    marks: int = Form(...),
    course: str = Form(...),
    image: str = Form(""),
    status: int = Form(...)
):
    std_obj = Student(
        name=name,
        age=age,
        gender=gender,
        marks=marks,
        course=course,
        image=image,
        status=status
    )

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE students
        SET name=?, age=?, gender=?, marks=?, course=?, image=?, status=?
        WHERE id=?
    """, (
        std_obj.name,
        std_obj.age,
        std_obj.gender,
        std_obj.marks,
        std_obj.course,
        std_obj.image,
        std_obj.status,
        std_id
    ))
    connection.commit()
    connection.close()

    return RedirectResponse("/", status_code=303)