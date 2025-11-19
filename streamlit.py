import streamlit as st
import json
from pathlib import Path
import random
import string
from datetime import datetime

# ---------------- BACKEND ---------------- #

class Liberary:
    database = 'data.json'
    data = []

    # Load database safely
    try:
        if Path(database).exists():
            with open(database) as fs:
                data = json.loads(fs.read())
        else:
            data = []
    except Exception as err:
        st.error(f"Database error: {err}")

    @classmethod
    def update_db(cls):
        with open(cls.database, "w") as fs:
            fs.write(json.dumps(cls.data, indent=4))

    @classmethod
    def Idgenerate(cls):
        alpha = random.choices(string.ascii_letters, k=2)
        num = random.choices(string.digits, k=2)
        sp = random.choice("!@#$%^&*")
        lst = alpha + num + [sp]
        random.shuffle(lst)
        return "".join(lst)

    @classmethod
    def find_user(cls, sid, pwd):
        return [i for i in cls.data if i["Student_Id"] == sid and i["Password"] == pwd]


lib = Liberary()

# ---------------- UI ---------------- #

st.set_page_config(page_title="Library Management System", page_icon="📚")
st.title("📚 Library Management System")

menu = [
    "Create Account", 
    "Issue Book", 
    "Submit Book", 
    "Show Details", 
    "Update Details", 
    "Delete Account"
]

choice = st.sidebar.selectbox("Menu", menu)

# ---------------- Create Account ---------------- #

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
            st.error("Phone No. must be 10 digits")
        elif len(pwd) != 4:
            st.error("Password must be 4 digits")
        else:
            sid = lib.Idgenerate()
            new_user = {
                "Name": name,
                "Roll_No": roll,
                "Age": age,
                "Gmail": gmail,
                "PhoneNo": phone,
                "Year": year,
                "Branch": branch,
                "Password": pwd,
                "Student_Id": sid,
                "Dues": 0,
                "Issu_Book": 0,
                "Last_Issu_Time": "",
                "Last_Submit_Time": ""
            }

            lib.data.append(new_user)
            lib.update_db()
            st.success("Account Created Successfully!")
            st.info(f"Your Library ID: **{sid}**")

# ---------------- Issue Book ---------------- #

elif choice == "Issue Book":
    st.header("📖 Issue Books")

    sid = st.text_input("Student ID")
    pwd = st.text_input("Password", type="password")
    book = st.number_input("How many books to issue?", min_value=1, max_value=5)

    if st.button("Issue"):
        user = lib.find_user(sid, pwd)

        if not user:
            st.error("Invalid Student ID or Password")
        else:
            if user[0]["Issu_Book"] + book > 5:
                st.error("Book issue limit exceeded! (Max 5)")
            else:
                user[0]["Issu_Book"] += book
                user[0]["Last_Issu_Time"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

                lib.update_db()
                st.success("Books Issued Successfully!")
                st.info(f"Issued on: {user[0]['Last_Issu_Time']}")

# ---------------- Submit Book ---------------- #

elif choice == "Submit Book":
    st.header("📘 Submit Books")

    sid = st.text_input("Student ID")
    pwd = st.text_input("Password", type="password")
    book = st.number_input("How many books to submit?", min_value=1, max_value=5)

    if st.button("Submit"):
        user = lib.find_user(sid, pwd)

        if not user:
            st.error("Invalid Student ID or Password")
        else:
            if user[0]["Issu_Book"] < book:
                st.error("You cannot submit more books than you have.")
            else:
                user[0]["Issu_Book"] -= book
                user[0]["Last_Submit_Time"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

                lib.update_db()
                st.success("Books Submitted Successfully!")
                st.info(f"Submitted on: {user[0]['Last_Submit_Time']}")

# ---------------- Show Details ---------------- #

elif choice == "Show Details":
    st.header("👤 Student Details")

    sid = st.text_input("Student ID")
    pwd = st.text_input("Password", type="password")

    if st.button("Show"):
        user = lib.find_user(sid, pwd)

        if not user:
            st.error("Student not found")
        else:
            st.success("Student Found!")
            st.json(user[0])

# ---------------- Update Details ---------------- #

elif choice == "Update Details":
    st.header("✏ Update Student Details")

    sid = st.text_input("Student ID")
    pwd = st.text_input("Password", type="password")

    if st.button("Load"):
        user = lib.find_user(sid, pwd)
        if not user:
            st.error("Invalid Student ID or Password")
        else:
            st.session_state["edit"] = user[0]
            st.success("Data Loaded! Scroll below to update.")

    if "edit" in st.session_state:
        st.subheader("Update Now")

        user = st.session_state["edit"]

        name = st.text_input("Name", user["Name"])
        gmail = st.text_input("Gmail", user["Gmail"])
        phone = st.text_input("Phone Number", user["PhoneNo"])
        year = st.number_input("Year", min_value=1, value=int(user["Year"]))
        branch = st.text_input("Branch", user["Branch"])
        pwd2 = st.text_input("Password (4 digits)", user["Password"])

        if st.button("Update"):
            if len(phone) != 10:
                st.error("Phone must be 10 digits")
            elif len(pwd2) != 4:
                st.error("Password must be 4 digits")
            else:
                user["Name"] = name
                user["Gmail"] = gmail
                user["PhoneNo"] = phone
                user["Year"] = year
                user["Branch"] = branch
                user["Password"] = pwd2

                lib.update_db()
                st.success("Details Updated Successfully!")

# ---------------- Delete Account ---------------- #

elif choice == "Delete Account":
    st.header("🗑 Delete Library Account")

    sid = st.text_input("Student ID")
    pwd = st.text_input("Password", type="password")

    if st.button("Delete"):
        user = lib.find_user(sid, pwd)

        if not user:
            st.error("Invalid Student ID or Password")
        else:
            lib.data.remove(user[0])
            lib.update_db()
            st.success("Account Deleted Successfully!")
