from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = "simple_secret_key"  # Для хранения сессии

# Псевдо-база данных пользователей:
# username -> {"password": "xxx", "role": "admin"/"teacher"/"student"}
users = {
    "admin": {"password": "admin", "role": "admin"},
    "teacher": {"password": "teacher", "role": "teacher"},
    "student1": {"password": "student1", "role": "student"},
    "student2": {"password": "student2", "role": "student"}
}

# Псевдо-база данных студентов (id -> имя):
# Добавлять может администратор. Для упрощения: student_id = имя пользователя
registered_students = {
    "student1": "Иванов Иван",
    "student2": "Петров Петр"
}

# Псевдо-база данных занятий (class_id -> {"course": str, "datetime": str})
classes = {}

# Псевдоблокчейн - список блоков. Каждый блок - словарь с транзакцией.
# Пример блока: {"timestamp": "...", "action": "add_student"|"add_class"|"mark_attendance", "data": {...}, "prev_hash": "...", "hash": "..."}
blockchain = []

def create_block(action, data):
    """Создать блок с транзакцией"""
    timestamp = datetime.utcnow().isoformat()
    prev_hash = blockchain[-1]["hash"] if len(blockchain) > 0 else "0"
    block_str = f"{timestamp}{action}{data}{prev_hash}"
    block_hash = hashlib.sha256(block_str.encode()).hexdigest()
    block = {
        "timestamp": timestamp,
        "action": action,
        "data": data,
        "prev_hash": prev_hash,
        "hash": block_hash
    }
    blockchain.append(block)
    return block


@app.route('/')
def index():
    if 'username' in session:
        user = session['username']
        role = users[user]["role"]
        if role == "admin":
            return redirect(url_for('admin_dashboard'))
        elif role == "teacher":
            return redirect(url_for('teacher_dashboard'))
        elif role == "student":
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Неверный логин или пароль")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/admin')
def admin_dashboard():
    if 'username' not in session or users[session['username']]['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('dashboard_admin.html', students=registered_students, classes=classes, blockchain=blockchain)


@app.route('/teacher')
def teacher_dashboard():
    if 'username' not in session or users[session['username']]['role'] != 'teacher':
        return redirect(url_for('login'))
    return render_template('dashboard_teacher.html', classes=classes, students=registered_students, blockchain=blockchain)


@app.route('/student')
def student_dashboard():
    if 'username' not in session or users[session['username']]['role'] != 'student':
        return redirect(url_for('login'))
    return render_template('dashboard_student.html', username=session['username'], classes=classes, blockchain=blockchain)


@app.route('/admin/add_student', methods=["GET", "POST"])
def add_student():
    if 'username' not in session or users[session['username']]['role'] != 'admin':
        return redirect(url_for('login'))
    if request.method == "POST":
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        if student_id and student_name:
            registered_students[student_id] = student_name
            # Добавляем запись в блокчейн
            create_block("add_student", {"student_id": student_id, "name": student_name})
            return redirect(url_for('admin_dashboard'))
    return render_template('add_student.html')


@app.route('/admin/add_class', methods=["GET", "POST"])
def add_class():
    if 'username' not in session or users[session['username']]['role'] != 'admin':
        return redirect(url_for('login'))
    if request.method == "POST":
        class_id = request.form.get('class_id')
        course = request.form.get('course')
        datetime_str = request.form.get('datetime')
        if class_id and course and datetime_str:
            classes[class_id] = {"course": course, "datetime": datetime_str}
            create_block("add_class", {"class_id": class_id, "course": course, "datetime": datetime_str})
            return redirect(url_for('admin_dashboard'))
    return render_template('add_class.html')


@app.route('/teacher/mark_attendance', methods=["GET", "POST"])
def mark_attendance():
    if 'username' not in session or users[session['username']]['role'] != 'teacher':
        return redirect(url_for('login'))
    if request.method == "POST":
        class_id = request.form.get('class_id')
        student_id = request.form.get('student_id')
        status = request.form.get('status')
        if class_id in classes and student_id in registered_students and status in ["present", "absent"]:
            # Записываем отметку о посещаемости в блокчейн
            create_block("mark_attendance", {"class_id": class_id, "student_id": student_id, "status": status})
            return redirect(url_for('teacher_dashboard'))
    return render_template('mark_attendance.html', classes=classes, students=registered_students)


@app.route('/student/view_attendance')
def view_attendance():
    if 'username' not in session or users[session['username']]['role'] != 'student':
        return redirect(url_for('login'))
    current_student = session['username']
    # Из блокчейна отберём все записи mark_attendance для этого студента
    attendance_records = []
    for block in blockchain:
        if block["action"] == "mark_attendance":
            if block["data"]["student_id"] == current_student:
                attendance_records.append({
                    "class_id": block["data"]["class_id"],
                    "status": block["data"]["status"],
                    "timestamp": block["timestamp"]
                })
    return render_template('view_attendance.html', attendance=attendance_records, classes=classes)


if __name__ == '__main__':
    app.run(debug=True)
