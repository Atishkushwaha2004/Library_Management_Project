# Library_Management_Project
# 📚 Library Management System (Streamlit + PostgreSQL)

A secure and interactive **Library Management System** built using **Python, Streamlit, PostgreSQL, and bcrypt**.    
This application allows students to create accounts, issue books, submit books, update details, and delete accounts with password authentication.

---

## 🚀 Features

### 👤 Account Management
- Create new student account
- Auto-generated unique Library ID
- Secure password hashing using bcrypt
- Update student details
- Delete student account

### 📖 Book Management
- Issue books (Maximum limit: 5)
- Submit issued books
- Prevent issuing more than allowed
- Prevent submitting more than issued

### ⏱ Activity Tracking
- Last book issue time
- Last book submit time

### 🔐 Security
- Passwords stored using bcrypt hashing
- Environment variables for database credentials

---

## 🧩 Tech Stack

| Component | Technology |
|--------|-----------|
| Frontend | Streamlit |
| Backend | Python (OOP) |
| Database | PostgreSQL |
| Security | bcrypt |
| Config | python-dotenv |

---

## 📂 Project Structure
