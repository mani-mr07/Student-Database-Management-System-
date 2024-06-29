from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host='localhost',
    username='root',
    password='manikandan22072003',
    database='mani')

cursor = db.cursor()
@app.route('/')
def intro():
       return render_template("intro.html")
    
@app.route('/login_student', methods=['GET',"POST"])
def login_student():
    regnum=request.args.get('regNum')
    query="SELECT * from students WHERE reg_number=%s"
    cursor.execute(query,(regnum,))
    student=cursor.fetchall()
    if student:
      return render_template("login_student.html", data=student)
    return render_template("login_student.html",error_msg="no details found")


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['pass']
        check_query="SELECT * FROM staffs WHERE username = %s AND passcode=%s"
        values=(username,password)
        cursor.execute(check_query,values)
        allow = cursor.fetchone()

        if allow:
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error_msg='Invalid username or password')

    return render_template('login.html', error_msg=None)

@app.route('/sign_up', methods=['GET','POST'])
def sign_up():
    error_statement = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        check_query = "SELECT * FROM staffs WHERE username = %s"
        cursor.execute(check_query, (username,))
        exist_student = cursor.fetchone()

        if exist_student:
            error_statement = "Entry with " + username + " username is already Exist"
        else:
            query = "INSERT INTO staffs (username, passcode) VALUES (%s, %s)"
            values = (username, password)
            cursor.execute(query, values)
            db.commit()
    return render_template("sign_up.html", error_msg=error_statement)



@app.route('/home')   
def home():
    return render_template("home.html")

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    error_stmt = None
    
    if request.method == 'POST':
        Name = request.form['name']
        reg_number = request.form['regNum']
        Age = request.form['age']
        dept= request.form['department']

        check_query = "SELECT * FROM students WHERE reg_number = %s"
        cursor.execute(check_query, (reg_number,))
        exist_student = cursor.fetchone()

        if exist_student:
            error_stmt = "Entry with " + reg_number + " register Number is already Exist"
        else:
            query = "INSERT INTO students (name, reg_number, age, depart) VALUES (%s, %s, %s, %s)"
            values = (Name, reg_number, Age, dept)

            cursor.execute(query, values)
            db.commit()
    
    return render_template("add_student.html", error_msg=error_stmt)

@app.route('/delete_student', methods=['GET', 'POST'])
def delete_student():
    error_stmt= None
    if request.method == 'POST':
        delete_ent=request.form['deleteregNum']

        check_query = "SELECT * FROM students WHERE reg_number = %s"
        cursor.execute(check_query, (delete_ent,))
        exist_stu = cursor.fetchone()

        if exist_stu:
            delQuery = "DELETE FROM students WHERE reg_number=%s"
            cursor.execute(delQuery, (delete_ent,))
            db.commit()
        else:
            error_stmt = "The student with "+delete_ent+" does not Exist"

    return render_template("delete_student.html", del_error_msg = error_stmt)


@app.route('/show_detail', methods=['GET'])
def show_detail():
    dept_c= request.args.get('filter')
    sort_column = request.args.get('sort_col')
    sort_order = request.args.get('sort_order')
    query="SELECT * FROM students"
    if dept_c:
        query+=f" WHERE depart = '{dept_c}'"

    if sort_column and sort_order:
        allowed_columns = ['name', 'age', 'reg_number', 'depart']
        allowed_orders = ['ASC', 'DESC']

        if sort_column in allowed_columns and sort_order in allowed_orders:
            query += f" ORDER BY {sort_column} {sort_order}"
        else:
            query += " ORDER BY name ASC"
    cursor.execute(query)
    students = cursor.fetchall()
    return render_template("show_detail.html", data=students)


@app.route('/update_student/<int:student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    error_msg = None

    if request.method == 'POST':
        new_name = request.form.get('name')
        new_reg_number = request.form.get('regNum')
        new_age = request.form.get('age')
        new_department = request.form.get('department')
        
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        existing_student = cursor.fetchone()

        if existing_student:
            cursor.execute("SELECT * FROM students WHERE reg_number = %s AND id != %s", (new_reg_number, student_id))
            existing_reg_num_student = cursor.fetchone()

            if existing_reg_num_student:
                error_msg = "Registration number is already in use by another student."
            else:
                updated_name = new_name if new_name else existing_student[1]
                updated_reg_number = new_reg_number if new_reg_number else existing_student[2]
                updated_age = new_age if new_age else existing_student[3]
                updated_department = new_department if new_department else existing_student[4]

                update_query = "UPDATE students SET name=%s, reg_number=%s, age=%s, depart=%s WHERE id=%s"
                update_values = (updated_name, updated_reg_number, updated_age, updated_department, student_id)
                cursor.execute(update_query, update_values)
                db.commit()

                return redirect(url_for('show_detail'))
        else:
            error_msg = "Student not found."

    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    updated_student = cursor.fetchone()

    return render_template("update_student.html", student=updated_student, error_msg=error_msg)


if __name__=="__main__":

    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            reg_number VARCHAR(20) NOT NULL UNIQUE,
            age INT NOT NULL,
            depart VARCHAR(10) NOT NULL
        )
    ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS staffs (
            username VARCHAR(20) NOT NULL UNIQUE,
            passcode VARCHAR(20) NOT NULL UNIQUE
        )
    ''')


    app.run(debug=True)

