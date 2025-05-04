import mysql.connector 
from mysql.connector import Error

# Connect to the MySQL database (update with your connection details)
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='1142004@jap)',  # your MySQL password
        database='students_db'
    )
    if conn.is_connected():
        print("Connected to MySQL database")
except Error as e:
    print(f"Error: {e}")
    exit(1)

cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS Gender (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    gender VARCHAR(50) UNIQUE
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Branch (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    branch_name VARCHAR(255) UNIQUE
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Contact (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255),
                    number VARCHAR(50),
                    address TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Student (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    rollno VARCHAR(255),
                    sname VARCHAR(255),
                    sem INT,
                    gender_id INT,
                    branch_id INT,
                    contact_id INT,
                    FOREIGN KEY (gender_id) REFERENCES Gender(id),
                    FOREIGN KEY (branch_id) REFERENCES Branch(id),
                    FOREIGN KEY (contact_id) REFERENCES Contact(id)
                )''')

# Course table
cursor.execute('''CREATE TABLE IF NOT EXISTS Course (
                    course_id INT AUTO_INCREMENT PRIMARY KEY,
                    course_name VARCHAR(255),
                    credits INT
                )''')

# Enrollment table to connect Students and Courses
cursor.execute('''CREATE TABLE IF NOT EXISTS Enrollment (
                    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT,
                    course_id INT,
                    FOREIGN KEY (student_id) REFERENCES Student (id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES Course (course_id)
                )''')

def add_gender(gender):
    cursor.execute('INSERT IGNORE INTO Gender (gender) VALUES (%s)', (gender,))
    conn.commit()
    print(f"Inserted gender: {gender}")

def add_branch(branch_name):
    cursor.execute('INSERT IGNORE INTO Branch (branch_name) VALUES (%s)', (branch_name,))
    conn.commit()
    print(f"Inserted branch: {branch_name}")
    
def add_contact(email, number, address):
    cursor.execute('''INSERT INTO Contact (email, number, address)
                      VALUES (%s, %s, %s)''', (email, number, address))
    conn.commit()

    # Fetch the last inserted contact_id
    cursor.execute('SELECT LAST_INSERT_ID()')
    contact_id = cursor.fetchone()[0]

    return contact_id



def add_student(rollno, sname, sem, gender, branch, email, number, address):
    add_gender(gender)
    add_branch(branch)
    contact_id = add_contact(email, number, address)

    cursor.execute('SELECT id FROM Gender WHERE gender = %s', (gender,))
    gender_id = cursor.fetchone()[0]

    cursor.execute('SELECT id FROM Branch WHERE branch_name = %s', (branch,))
    branch_id = cursor.fetchone()[0]

    cursor.execute('''INSERT INTO Student (rollno, sname, sem, gender, branch, email, number, address)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s  )''',
                   (rollno, sname, sem, gender_id, branch_id, contact_id, contact_id, contact_id))
    conn.commit()
    print("Student Added Successfully")

def view_students():
    try:
        cursor.execute('''SELECT s.id, s.rollno, s.sname, s.sem, g.gender, b.branch_name, c.email, c.number, c.address
                          FROM Student s
                          JOIN Gender g ON s.gender = g.id
                          JOIN Branch b ON s.branch = b.id
                          JOIN Contact c ON s.contact = c.id''')
        students = cursor.fetchall()
        for student in students:
            print(f"ID: {student[0]}, Roll No: {student[1]}, Name: {student[2]}, Semester: {student[3]}, "
                  f"Gender: {student[4]}, Branch: {student[5]}, Email: {student[6]}, "
                  f"Phone: {student[7]}, Address: {student[8]}")
    except Exception as e:
        print(f"An error occurred: {e}")


def add_course(course_name, credits):
    cursor.execute('''INSERT INTO Course (course_name, credits) VALUES (%s, %s)''', 
                   (course_name, credits))
    conn.commit()
    print("Course Added Successfully")

def view_courses():
    cursor.execute('SELECT * FROM Course')
    courses = cursor.fetchall()
    for course in courses:
        print(course)

def enroll_student(student_id, course_id):
    cursor.execute('SELECT id FROM Student WHERE id = %s', (student_id,))
    if cursor.fetchone() is None:
        print("Error: Student ID does not exist.")
        return

    cursor.execute('SELECT course_id FROM Course WHERE course_id = %s', (course_id,))
    if cursor.fetchone() is None:
        print("Error: Course ID does not exist.")
        return

    cursor.execute('''INSERT INTO Enrollment (student_id, course_id) VALUES (%s, %s)''', 
                   (student_id, course_id))
    conn.commit()
    print("Student Enrolled in Course Successfully")

def view_enrollments():
    cursor.execute('''SELECT e.enrollment_id, s.sname, c.course_name 
                      FROM Enrollment e 
                      JOIN Student s ON e.student_id = s.id 
                      JOIN Course c ON e.course_id = c.course_id''')
    enrollments = cursor.fetchall()
    for enrollment in enrollments:
        print(enrollment)

def delete_student(student_id):
    cursor.execute('DELETE FROM Enrollment WHERE student_id = %s', (student_id,))
    cursor.execute('DELETE FROM Student WHERE id = %s', (student_id,))
    conn.commit()
    print("Student Deleted Successfully")

def delete_course(course_id):
    cursor.execute('DELETE FROM Course WHERE course_id = %s', (course_id,))
    conn.commit()
    print("Course Deleted Successfully")

def main():
    while True:
        print("\nOptions:")
        print("1. Add Student")
        print("2. View Students")
        print("3. Add Course")
        print("4. View Courses")
        print("5. Enroll Student in Course")
        print("6. View Enrollments")
        print("7. Delete Student")
        print("8. Delete Course")
        print("9. Exit")

        choice = input("Choose an option (1-9): ")

        if choice == '1':
            rollno = input("Enter Roll No: ")
            sname = input("Enter Student Name: ")
            sem = int(input("Enter Semester: "))
            gender = input("Enter Gender: ")
            branch = input("Enter Branch: ")
            email = input("Enter Email: ")
            number = input("Enter Phone Number: ")
            address = input("Enter Address: ")
            add_student(rollno, sname, sem, gender, branch, email, number, address)

        elif choice == '2':
            view_students()

        elif choice == '3':
            course_name = input("Enter Course Name: ")
            credits = int(input("Enter Credits: "))
            add_course(course_name, credits)

        elif choice == '4':
            view_courses()

        elif choice == '5':
            student_id = int(input("Enter Student ID to enroll: "))
            course_id = int(input("Enter Course ID to enroll in: "))
            enroll_student(student_id, course_id)

        elif choice == '6':
            view_enrollments()

        elif choice == '7':
            student_id = int(input("Enter Student ID to delete: "))
            delete_student(student_id)

        elif choice == '8':
            course_id = int(input("Enter Course ID to delete: "))
            delete_course(course_id)

        elif choice == '9':
            print("Exiting...")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()

# Close the database connection
cursor.close()
conn.close()
