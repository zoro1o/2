from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "aei_secret_2024"  # Required for session management

# ─────────────────────────────────────────────
#  ALL DATA STORED IN PYTHON DICTIONARIES/LISTS
# ─────────────────────────────────────────────

# User credentials: username -> {password, role}
USERS = {
    "S_1": {"password": "STUDENT", "role": "student"},
    "S_2": {"password": "STUDENT", "role": "student"},
    "S_3": {"password": "STUDENT", "role": "student"},
    "faculty1": {"password": "FACULTY", "role": "faculty"},
    "admin":    {"password": "ADMIN",   "role": "admin"},
}

# Student data: username -> {name, attendance, marks}
STUDENTS = {
    "S_1": {"name": "Aarav Sharma",   "attendance": 85, "marks": {"Math": 88, "Physics": 76, "CS": 91}},
    "S_2": {"name": "Priya Gogoi",    "attendance": 72, "marks": {"Math": 65, "Physics": 80, "CS": 70}},
    "S_3": {"name": "Rohan Das",      "attendance": 90, "marks": {"Math": 92, "Physics": 88, "CS": 95}},
}

# Notes uploaded by faculty: list of {title, content, uploaded_by}
NOTES = [
    {"title": "Unit 1 - Algebra Notes", "content": "Review chapters 1-3 before the exam.", "uploaded_by": "faculty1"},
]

# Notices from admin: list of {title, content}
NOTICES = [
    {"title": "Mid-Semester Exam Schedule", "content": "Exams start from 20th July. Check timetable on the board."},
    {"title": "College Fest Registration",  "content": "Register for TechFest 2024 by 10th July at the admin office."},
]

# ─────────────────────────────────────────────
#  HELPER: Check if user is logged in
# ─────────────────────────────────────────────
def is_logged_in():
    return "username" in session

# ─────────────────────────────────────────────
#  ROUTE: Home → redirect to login
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return redirect(url_for("login"))

# ─────────────────────────────────────────────
#  ROUTE: Login page (one page for all roles)
# ─────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if username exists and password matches
        if username in USERS and USERS[username]["password"] == password:
            session["username"] = username
            session["role"]     = USERS[username]["role"]

            # Redirect based on role
            role = USERS[username]["role"]
            if role == "student":
                return redirect(url_for("student_dashboard"))
            elif role == "faculty":
                return redirect(url_for("faculty_dashboard"))
            elif role == "admin":
                return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)

# ─────────────────────────────────────────────
#  ROUTE: Logout
# ─────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ─────────────────────────────────────────────
#  STUDENT ROUTES
# ─────────────────────────────────────────────
@app.route("/student")
def student_dashboard():
    if not is_logged_in() or session["role"] != "student":
        return redirect(url_for("login"))
    username = session["username"]
    student  = STUDENTS[username]
    return render_template("student.html", student=student, notices=NOTICES, notes=NOTES)

# ─────────────────────────────────────────────
#  FACULTY ROUTES
# ─────────────────────────────────────────────
@app.route("/faculty")
def faculty_dashboard():
    if not is_logged_in() or session["role"] != "faculty":
        return redirect(url_for("login"))
    return render_template("faculty.html", students=STUDENTS, notes=NOTES, notices=NOTICES)

@app.route("/faculty/upload_marks", methods=["POST"])
def upload_marks():
    if not is_logged_in() or session["role"] != "faculty":
        return redirect(url_for("login"))
    student_id = request.form["student_id"]
    subject    = request.form["subject"]
    marks      = request.form["marks"]
    # Update marks in the dictionary
    if student_id in STUDENTS:
        STUDENTS[student_id]["marks"][subject] = int(marks)
    return redirect(url_for("faculty_dashboard"))

@app.route("/faculty/upload_notes", methods=["POST"])
def upload_notes():
    if not is_logged_in() or session["role"] != "faculty":
        return redirect(url_for("login"))
    title   = request.form["title"]
    content = request.form["content"]
    NOTES.append({"title": title, "content": content, "uploaded_by": session["username"]})
    return redirect(url_for("faculty_dashboard"))

# ─────────────────────────────────────────────
#  ADMIN ROUTES
# ─────────────────────────────────────────────
@app.route("/admin")
def admin_dashboard():
    if not is_logged_in() or session["role"] != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html", students=STUDENTS, users=USERS, notices=NOTICES)

@app.route("/admin/add_notice", methods=["POST"])
def add_notice():
    if not is_logged_in() or session["role"] != "admin":
        return redirect(url_for("login"))
    title   = request.form["title"]
    content = request.form["content"]
    NOTICES.append({"title": title, "content": content})
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/update_attendance", methods=["POST"])
def update_attendance():
    if not is_logged_in() or session["role"] != "admin":
        return redirect(url_for("login"))
    student_id = request.form["student_id"]
    attendance = request.form["attendance"]
    if student_id in STUDENTS:
        STUDENTS[student_id]["attendance"] = int(attendance)
    return redirect(url_for("admin_dashboard"))

# ─────────────────────────────────────────────
#  NOTICE BOARD (public - no login needed)
# ─────────────────────────────────────────────
@app.route("/noticeboard")
def noticeboard():
    return render_template("noticeboard.html", notices=NOTICES)

# ─────────────────────────────────────────────
#  RUN THE APP
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
