from flask import Flask, render_template, request, redirect, url_for, session
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
from db import db
from models import User, Student, ClassModel, AttendanceRecord
from node import Node

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = SECRET_KEY

db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first(): # короче предустановки чтоб если в бд ничего не было, то автоматом созадлось
        db.session.add(User(username="admin", password_hash="admin", role="admin"))
        db.session.add(User(username="teacher", password_hash="teacher", role="teacher"))
        db.session.add(User(username="student1", password_hash="student1", role="student"))
        db.session.add(User(username="student2", password_hash="student2", role="student"))
        db.session.commit()

    node = Node()

@app.route('/')
def index():
    if 'username' in session:
        user = session['username']
        u = User.query.filter_by(username=user).first()
        if u and u.role == "admin":
            return redirect(url_for('admin_dashboard'))
        elif u and u.role == "teacher":
            return redirect(url_for('teacher_dashboard'))
        elif u and u.role == "student":
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        u = User.query.filter_by(username=username).first()
        if u and u.password_hash == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template("login.html", error="Неверный логин или пароль")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    u = User.query.filter_by(username=session['username']).first()
    if u.role != 'admin':
        return redirect(url_for('login'))

    students = Student.query.all()
    classes = ClassModel.query.all()

    blockchain_chain = node.blockchain.chain

    return render_template('dashboard_admin.html',
                           students=students,
                           classes=classes,
                           blockchain=blockchain_chain)

@app.route('/teacher')
def teacher_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    u = User.query.filter_by(username=session['username']).first()
    if u.role != 'teacher':
        return redirect(url_for('login'))

    students = Student.query.all()
    classes = ClassModel.query.all()
    blockchain_chain = node.blockchain.chain

    return render_template('dashboard_teacher.html',
                           students=students,
                           classes=classes,
                           blockchain=blockchain_chain)

@app.route('/student')
def student_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    u = User.query.filter_by(username=session['username']).first()
    if u.role != 'student':
        return redirect(url_for('login'))
    return render_template('dashboard_student.html')

@app.route('/admin/add_student', methods=["GET","POST"])
def add_student():
    if 'username' not in session:
        return redirect(url_for('login'))
    u = User.query.filter_by(username=session['username']).first()
    if u.role != 'admin':
        return redirect(url_for('login'))

    if request.method=="POST":
        student_id = request.form.get("student_id")
        student_name = request.form.get("student_name")
        if student_id and student_name:
            # добавляем в бд (чтоб сохранилось)
            new_student = Student(student_id=student_id, name=student_name)
            db.session.add(new_student)
            db.session.commit()

            # а потмо добовлеям это как транзакцию в нашу ноду, так надо
            tx = {
                "action": "add_student",
                "student_id": student_id,
                "name": student_name
            }
            node.create_transaction(tx)

            return redirect(url_for('admin_dashboard'))
    return render_template('add_student.html')

@app.route('/admin/add_class', methods=["GET","POST"])
def add_class():
    if 'username' not in session:
        return redirect(url_for('login'))
    u = User.query.filter_by(username=session['username']).first()
    if u.role != 'admin':
        return redirect(url_for('login'))

    if request.method=="POST":
        class_id = request.form.get("class_id")
        course = request.form.get("course")
        datetime_str = request.form.get("datetime")
        if class_id and course and datetime_str:
            new_class = ClassModel(class_id=class_id, course=course, datetime=datetime_str)
            db.session.add(new_class)
            db.session.commit()

            tx = {
                "action": "add_class",
                "class_id": class_id,
                "course": course,
                "datetime": datetime_str
            }
            node.create_transaction(tx)

            return redirect(url_for('admin_dashboard'))
    return render_template('add_class.html')

@app.route('/teacher/mark_attendance', methods=["GET","POST"])
def mark_attendance():
    if 'username' not in session:
        return redirect(url_for('login'))
    u = User.query.filter_by(username=session['username']).first()
    if u.role != 'teacher':
        return redirect(url_for('login'))

    classes = ClassModel.query.all()
    students = Student.query.all()

    if request.method=="POST":
        class_id = request.form.get("class_id")
        student_id = request.form.get("student_id")
        status = request.form.get("status")

        cls = ClassModel.query.filter_by(class_id=class_id).first()
        std = Student.query.filter_by(student_id=student_id).first()

        if cls and std and status in ["present","absent"]:
            attendance = AttendanceRecord(class_id=class_id, student_id=student_id, status=status)
            db.session.add(attendance)
            db.session.commit()

            tx = {
                "action": "mark_attendance",
                "class_id": class_id,
                "student_id": student_id,
                "status": status
            }
            node.create_transaction(tx)

            return redirect(url_for('teacher_dashboard'))

    return render_template('mark_attendance.html', classes=classes, students=students)

@app.route('/student/view_attendance')
def view_attendance():
    if 'username' not in session:
        return redirect(url_for('login'))
    u = User.query.filter_by(username=session['username']).first()
    if u.role != 'student':
        return redirect(url_for('login'))

    attendance = AttendanceRecord.query.filter_by(student_id=session['username']).order_by(AttendanceRecord.timestamp).all()
    class_dict = {c.class_id: c for c in ClassModel.query.all()}

    return render_template('view_attendance.html', attendance=attendance, classes=class_dict)

@app.route('/mine')
def mine():
    mined_block = node.mine_block()
    if mined_block:
        msg = f"Block mined! Hash: {mined_block.hash}"
    else:
        msg = "No transactions to mine."
    return msg

@app.context_processor
def inject_user():
    from models import User
    user = None
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
    return dict(current_user=user, User=User)


if __name__ == '__main__':
    app.run(debug=True)
