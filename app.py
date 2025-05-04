from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key

# SQLite database file
DATABASE = 'students.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Enables dictionary-like access to rows
    return conn

@app.route('/')
def index():
    return render_template('index.html')

# Routes for managing students
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        rollno = request.form['rollno']
        sname = request.form['sname']
        sem = int(request.form['sem'])
        gender = request.form['gender']
        branch = request.form['branch']
        email = request.form['email']
        number = request.form['number']
        address = request.form['address']   

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT OR IGNORE INTO Gender (gender) VALUES (?)', (gender,))
            cursor.execute('INSERT OR IGNORE INTO Branch (branch_name) VALUES (?)', (branch,))
            cursor.execute('INSERT INTO Contact (email, number, address) VALUES (?, ?, ?)', 
                           (email, number, address))
            conn.commit()

            cursor.execute('SELECT id FROM Gender WHERE gender = ?', (gender,))
            gender_id = cursor.fetchone()[0]
            cursor.execute('SELECT id FROM Branch WHERE branch_name = ?', (branch,))
            branch_id = cursor.fetchone()[0]
            cursor.execute('SELECT last_insert_rowid()')
            contact_id = cursor.fetchone()[0]

            cursor.execute('''INSERT INTO Student (rollno, sname, sem, gender_id, branch_id, contact_id)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (rollno, sname, sem, gender_id, branch_id, contact_id))
            conn.commit()
            flash('Student added successfully!')
        except Exception as e:
            flash(f"An error occurred: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/view_students')
def view_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT s.id, s.rollno, s.sname, s.sem, g.gender, b.branch_name, c.email, c.number, c.address
                          FROM Student s
                          JOIN Gender g ON s.gender_id = g.id
                          JOIN Branch b ON s.branch_id = b.id
                          JOIN Contact c ON s.contact_id = c.id''')
        students = cursor.fetchall()
    except Exception as e:
        flash(f"An error occurred: {e}")
        students = []
    finally:
        cursor.close()
        conn.close()

    return render_template('view_students.html', students=students)

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course_name = request.form['course_name']
        credits = int(request.form['credits'])

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO Course (course_name, credits) VALUES (?, ?)', 
                           (course_name, credits))
            conn.commit()
            flash('Course added successfully!')
        except Exception as e:
            flash(f"An error occurred: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('index'))
    return render_template('add_course.html')

@app.route('/view_courses')
def view_courses():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM Course')
        courses = cursor.fetchall()
    except Exception as e:
        flash(f"An error occurred: {e}")
        courses = []
    finally:
        cursor.close()
        conn.close()

    return render_template('view_courses.html', courses=courses)

@app.route('/enroll_student', methods=['GET', 'POST'])
def enroll_student():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        course_id = int(request.form['course_id'])

        try:
            cursor.execute('SELECT id FROM Student WHERE id = ?', (student_id,))
            if cursor.fetchone() is None:
                flash("Error: Student ID does not exist.")
                return redirect(url_for('enroll_student'))

            cursor.execute('SELECT course_id FROM Course WHERE course_id = ?', (course_id,))
            if cursor.fetchone() is None:
                flash("Error: Course ID does not exist.")
                return redirect(url_for('enroll_student'))

            cursor.execute('''INSERT INTO Enrollment (student_id, course_id) VALUES (?, ?)''', 
                           (student_id, course_id))
            conn.commit()
            flash('Student enrolled in course successfully!')
        except Exception as e:
            flash(f"An error occurred: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('index'))
    return render_template('enroll_student.html')

@app.route('/view_enrollments')
def view_enrollments():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT e.enrollment_id, s.sname, c.course_name 
                          FROM Enrollment e 
                          JOIN Student s ON e.student_id = s.id 
                          JOIN Course c ON e.course_id = c.course_id''')
        enrollments = cursor.fetchall()
    except Exception as e:
        flash(f"An error occurred: {e}")
        enrollments = []
    finally:
        cursor.close()
        conn.close()

    return render_template('view_enrollments.html', enrollments=enrollments)

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Enrollment WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM Student WHERE id = ?', (student_id,))
        conn.commit()
        flash('Student deleted successfully!')
    except Exception as e:
        flash(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_students'))

@app.route('/delete_course/<int:course_id>')
def delete_course(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Course WHERE course_id = ?', (course_id,))
        conn.commit()
        flash('Course deleted successfully!')
    except Exception as e:
        flash(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_courses'))


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS Gender (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        gender TEXT UNIQUE
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Branch (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        branch_name TEXT UNIQUE
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Contact (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT,
                        number TEXT,
                        address TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Student (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rollno TEXT,
                        sname TEXT,
                        sem INTEGER,
                        gender_id INTEGER,
                        branch_id INTEGER,
                        contact_id INTEGER,
                        FOREIGN KEY (gender_id) REFERENCES Gender(id),
                        FOREIGN KEY (branch_id) REFERENCES Branch(id),
                        FOREIGN KEY (contact_id) REFERENCES Contact(id)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Course (
                        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        course_name TEXT,
                        credits INTEGER
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Enrollment (
                        enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER,
                        course_id INTEGER,
                        FOREIGN KEY (student_id) REFERENCES Student(id) ON DELETE CASCADE,
                        FOREIGN KEY (course_id) REFERENCES Course(course_id)
                    )''')

    # Insert initial data for testing
    genders = ['Male', 'Female']
    for gender in genders:
        cursor.execute('INSERT OR IGNORE INTO Gender (gender) VALUES (?)', (gender,))

    branches = ['Computer Science', 'Electrical Engineering', 'Mechanical Engineering', 
                'Civil Engineering', 'Information Technology', 'Biotechnology', 
                'Chemical Engineering', 'Physics', 'Mathematics', 'Statistics']
    for branch in branches:
        cursor.execute('INSERT OR IGNORE INTO Branch (branch_name) VALUES (?)', (branch,))

    courses = [
        ('Data Structures', 4),
        ('Database Systems', 3),
        ('Operating Systems', 3),
        ('Computer Networks', 4),
        ('Software Engineering', 3),
        ('Web Development', 3),
        ('Artificial Intelligence', 4),
        ('Machine Learning', 4),
        ('Digital Signal Processing', 3),
        ('Computer Graphics', 3)
    ]
    for course in courses:
        cursor.execute('INSERT INTO Course (course_name, credits) VALUES (?, ?)', course)

    # Insert sample contacts
    contacts = [
        ('john.doe@example.com', '123-456-7890', '123 Elm St'),
        ('jane.smith@example.com', '123-555-7891', '456 Oak St'),
        ('alice.johnson@example.com', '123-555-7892', '789 Pine St'),
        ('bob.brown@example.com', '123-555-7893', '101 Maple St'),
        ('charlie.jones@example.com', '123-555-7894', '202 Birch St'),
        ('dave.wilson@example.com', '123-555-7895', '303 Cedar St'),
        ('eve.davis@example.com', '123-555-7896', '404 Walnut St'),
        ('frank.miller@example.com', '123-555-7897', '505 Chestnut St'),
        ('grace.martin@example.com', '123-555-7898', '606 Spruce St'),
        ('heidi.thompson@example.com', '123-555-7899', '707 Willow St')
    ]
    for contact in contacts:
        cursor.execute('INSERT INTO Contact (email, number, address) VALUES (?, ?, ?)', contact)

    # Retrieve gender and branch IDs for insertion
    gender_map = {row['gender']: row['id'] for row in cursor.execute('SELECT * FROM Gender')}
    branch_map = {row['branch_name']: row['id'] for row in cursor.execute('SELECT * FROM Branch')}
    contact_map = {row['email']: row['id'] for row in cursor.execute('SELECT * FROM Contact')}

    # Create sample students
    students = [
        ('CS101', 'John Doe', 1, 'Male', 'Computer Science', 'john.doe@example.com'),
        ('CS102', 'Jane Smith', 1, 'Female', 'Information Technology', 'jane.smith@example.com'),
        ('EE101', 'Alice Johnson', 2, 'Female', 'Electrical Engineering', 'alice.johnson@example.com'),
        ('ME101', 'Bob Brown', 2, 'Male', 'Mechanical Engineering', 'bob.brown@example.com'),
        ('CE101', 'Charlie Jones', 3, 'Male', 'Civil Engineering', 'charlie.jones@example.com'),
        ('IT101', 'Dave Wilson', 3, 'Male', 'Information Technology', 'dave.wilson@example.com'),
        ('BT101', 'Eve Davis', 1, 'Female', 'Biotechnology', 'eve.davis@example.com'),
        ('CH101', 'Frank Miller', 1, 'Male', 'Chemical Engineering', 'frank.miller@example.com'),
        ('PH101', 'Grace Martin', 2, 'Female', 'Physics', 'grace.martin@example.com'),
        ('MA101', 'Heidi Thompson', 2, 'Female', 'Mathematics', 'heidi.thompson@example.com')
    ]

    for student in students:
        rollno, sname, sem, gender, branch, email = student
        gender_id = gender_map[gender]
        branch_id = branch_map[branch]
        contact_id = contact_map[email]

        cursor.execute('''INSERT INTO Student (rollno, sname, sem, gender_id, branch_id, contact_id) 
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                          (rollno, sname, sem, gender_id, branch_id, contact_id))

    conn.commit()
    cursor.close()
    conn.close()



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
