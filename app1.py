import bcrypt
import streamlit as st
import psycopg2
import random
import string
from datetime import datetime
import os

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="Library Management System", page_icon="📚")
st.title("📚 Library Management System")

# ---------------- PASSWORD UTILS ---------------- #
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# ---------------- DB CONNECTION ---------------- #
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    st.error("❌ DATABASE_URL not found. Add it in Streamlit Secrets.")
    st.stop()

try:
    conn = psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
        connect_timeout=10
    )
    cursor = conn.cursor()
except Exception as e:
    st.error(f"❌ Database connection error: {e}")
    st.stop()

# ---------------- TABLE ---------------- #
cursor.execute("""
CREATE TABLE IF NOT EXISTS library (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(32) UNIQUE,
    name VARCHAR(200),
    roll_no VARCHAR(50),
    age INTEGER,
    gmail VARCHAR(200),
    phone_no VARCHAR(20),
    year INTEGER,
    branch VARCHAR(100),
    password VARCHAR(255),
    dues INTEGER DEFAULT 0,
    issu_book INTEGER DEFAULT 0,
    last_issu_time TIMESTAMP,
    last_submit_time TIMESTAMP
)
""")
conn.commit()

# ---------------- BACKEND CLASS ---------------- #
class Library:

    @staticmethod
    def id_generate():
        return "LIB" + "".join(random.choices(string.ascii_uppercase, k=2)) + \
               "".join(random.choices(string.digits, k=4))

    @staticmethod
    def create_user(data):
        cursor.execute("""
        INSERT INTO library
        (student_id,name,roll_no,age,gmail,phone_no,year,branch,password,issu_book)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,0)
        """, data)
        conn.commit()

    @staticmethod
    def find_user(sid, pwd):
        cursor.execute("SELECT * FROM library WHERE student_id=%s", (sid,))
        user = cursor.fetchone()
        if user and verify_password(pwd, user[9]):
            return user
        return None

    @staticmethod
    def issue_book(sid, count):
        cursor.execute("""
        UPDATE library
        SET issu_book = issu_book + %s,
            last_issu_time = %s
        WHERE student_id=%s
        """, (count, datetime.now(), sid))
        conn.commit()

    @staticmethod
    def submit_book(sid, count):
        cursor.execute("""
        UPDATE library
        SET issu_book = issu_book - %s,
            last_submit_time = %s
        WHERE student_id=%s
        """, (count, datetime.now(), sid))
        conn.commit()

    @staticmethod
    def update_user(data):
        cursor.execute("""
        UPDATE library
        SET name=%s, gmail=%s, phone_no=%s, year=%s, branch=%s, password=%s
        WHERE student_id=%s
        """, data)
        conn.commit()

    @staticmethod
    def delete_user(sid):
        cursor.execute("DELETE FROM library WHERE student_id=%s", (sid,))
        conn.commit()

# ---------------- MENU ---------------- #
menu = [
    "Create Account",
    "Issue Book",
    "Submit Book",
    "Show Details",
    "Update Details",
    "Delete Account"
]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- CREATE ACCOUNT ---------------- #
if choice == "Create Account":
    st.header("📝 Create New Library Account")

    name = st.text_input("Name")
    roll = st.text_input("Roll Number")
    age = st.number_input("Age", min_value=1)
    gmail = st.text_input("Email")
    phone = st.text_input("Phone Number")
    year = st.number_input("Year", min_value=1)
    branch = st.text_input("Branch")
    pwd = st.text_input("Password (4 digits)", type="password")

    if st.button("Create Account"):
        if len(phone) != 10:
            st.error("Phone number must be 10 digits")
        elif len(pwd) != 4:
            st.error("Password must be 4 digits")
        else:
            sid = Library.id_generate()
            Library.create_user(
                (sid, name, roll, age, gmail, phone, year, branch, hash_password(pwd))
            )
            st.success("✅ Account Created Successfully")
            st.info(f"Your Library ID: {sid}")

# ---------------- ISSUE BOOK ---------------- #
elif choice == "Issue Book":
    st.header("📖 Issue Book")

    sid = st.text_input("Student ID")
    pwd = st.text_input("Password", type="password")
    book = st.number_input("Books to issue", 1, 5)

    if st.button("Issue"):
        user = Library.find_user(sid, pwd)
        if not user:
            st.error("Invalid Student ID or Password")
        elif user[11] + book > 5:
            st.error("Book limit exceeded (Max 5)")
        else:
            Library.issue_book(sid, book)
            st.success("Books Issued Successfully")

# ---------------- SUBMIT BOOK ---------------- #
elif choice == "Submit Book":
    st.header("📘 Submit Book")

    sid = st.text_input("Student ID")
    pwd = st.text_input("Password", type="password")
    book = st.number_input("Books to submit", 1, 5)

    if st.button("Submit"):
        user = Library.find_user(sid, pwd)
        if not user:
            st.error("Invalid Student ID or Password")
        elif user[11] < book:
            st.error("You cannot submit more books than issued")
        else:
            Library.submit_book(sid, book)
            st.success("Books Submitted Successfully")

# ---------------- SHOW DETAILS ---------------- #
elif choice == "Show Details":
    st.header("👤 Student Details")

    sid = st.text_input("Student ID")
    pwd = st.text_input("Password", type="password")

    if st.button("Show"):
        user = Library.find_user(sid, pwd)
        if user:
            st.json({
                "Student ID": user[1],
                "Name": user[2],
                "Roll No": user[3],
                "Age": user[4],
                "Email": user[5],
                "Phone": user[6],
                "Year": user[7],
                "Branch": user[8],
                "Issued Books": user[11],
                "Last Issue": user[12],
                "Last Submit": user[13]
            })
        else:
            st.error("Student not found")

# ---------------- UPDATE DETAILS ---------------- #
elif choice == "Update Details":
    st.header("✏ Update Student Details")

    sid = st.text_input("Student ID")
    pwd = st.text_input("Password", type="password")

    if st.button("Load"):
        user = Library.find_user(sid, pwd)
        if user:
            st.session_state.edit = user
        else:
            st.error("Invalid credentials")

    if "edit" in st.session_state:
        u = st.session_state.edit
        name = st.text_input("Name", u[2])
        gmail = st.text_input("Email", u[5])
        phone = st.text_input("Phone", u[6])
        year = st.number_input("Year", value=u[7])
        branch = st.text_input("Branch", u[8])
        pwd2 = st.text_input("New Password (4 digits)", type="password")

        if st.button("Update"):
            Library.update_user(
                (name, gmail, phone, year, branch, hash_password(pwd2), u[1])
            )
            st.success("Details Updated Successfully")

# ---------------- DELETE ACCOUNT ---------------- #
elif choice == "Delete Account":
    st.header("🗑 Delete Account")

    sid = st.text_input("Student ID")
    pwd = st.text_input("Password", type="password")

    if st.button("Delete"):
        user = Library.find_user(sid, pwd)
        if user:
            Library.delete_user(sid)
            st.success("Account Deleted Successfully")
        else:
            st.error("Invalid Student ID or Password")
