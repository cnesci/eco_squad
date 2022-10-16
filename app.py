from flask import Flask, render_template, redirect, request, make_response, session, url_for
import sqlite3
import os
import boto3

app = Flask(__name__)
projects=[]
tasks=[]
delete_projects=[]
delete_tasks=[]
modify_projects=[]
modify_tasks=[]
students=[]
student_list=[]
names = []
the_user_name=''
student_list2=[]
modify_students=[]
fertiliser_list=[]
global total_fertiliser
total_fertiliser = 0

#Connect database
con = sqlite3.connect('projects.db', check_same_thread=False)

#If the tables already exists, delete 
con.execute("DROP TABLE IF EXISTS Project_table;")
con.execute("DROP TABLE IF EXISTS Maint_table;")
con.execute("DROP TABLE IF EXISTS Student_table;")

#Create tables
con.execute('''CREATE TABLE Project_table(id INTEGER PRIMARY KEY, project TEXT, description TEXT, frequency TEXT, start_date INTEGER, end_date INTEGER, people TEXT)''')
con.execute('''CREATE TABLE Maint_table(id INTEGER PRIMARY KEY, task TEXT, description TEXT, start_date INTEGER, frequency TEXT, fertiliser INTEGER, people INTEGER)''')
con.execute('''CREATE TABLE Student_table(id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, year INTEGER, project_id INTEGER)''')

#Dummy data
#con.execute('''INSERT INTO Project_table(project,description,frequency,start_date,end_date,people) VALUES(?,?,?,?,?,?)''', ("Plant peas", "yesyesm", "Daily", "start_date", "end_date", "Tom, Jerry"))

#Login page
@app.route('/login', methods=['POST'])
def do_admin_login():
    the_user_name = request.form['username']
    session['logged_in'] = True
    #Set cookie
    resp = make_response(redirect('/'))
    resp.set_cookie('Name',the_user_name)
    return resp

#Home page
@app.route("/")
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        name = request.cookies.get('Name')
        projects = con.execute("SELECT * FROM Project_table").fetchall()
        tasks = con.execute("SELECT * FROM Maint_table").fetchall()
        return render_template('index.html',name=name,projects=projects,tasks=tasks)

#Projects Page
@app.route("/projects")
def projects():
    projects = con.execute("SELECT * FROM Project_table").fetchall()
    return render_template("projects.html",projects=projects)

#Sort By Button
@app.route("/sort_by_dsc")
def sort_by_dsc():
    projects = con.execute('''SELECT * FROM Project_table ORDER BY end_date ASC''').fetchall()
    return render_template("projects.html",projects=projects)

#New Project
@app.route("/new_project")
def new_project():
    return render_template("add_project.html")

@app.route("/add_project", methods=["POST"])
def add_project():
    projects = {
    "project" : request.form["m_project"],
    "description" : request.form["m_description"],
    "frequency" : request.form["m_frequency"],
    "start_date" : request.form["m_start_date"],
    "end_date" : request.form["m_end_date"],
    "people" : request.form["m_people"]
    }

    student_list = projects["people"].split()
    for y in student_list:
        y.split(",")
        print(y)
        names.append(y)

    for x in names:
        if x == ("and"):
            break
        con.execute('''INSERT INTO Student_table(first_name) VALUES(?)''', (x,))
    con.execute('''INSERT INTO Project_table(project,description,frequency,start_date,end_date,people) VALUES(?,?,?,?,?,?)''', (projects["project"], projects["description"], projects["frequency"], projects["start_date"], projects["end_date"], projects["people"]))
    return redirect("/projects")

#Remove Project
@app.route("/remove_project")
def remove_project():
    return render_template("delete_project.html")

@app.route("/delete_project", methods=["POST"])
def delete_project():
    delete_projects = {
    "id" : request.form["m_id"]
    }
    con.execute('''DELETE FROM Project_table WHERE id=(?)''',
(delete_projects["id"]))
    return redirect("/projects")

#Update project
@app.route("/update_project")
def update_project():
    return render_template("modify_project.html")

@app.route("/modify_project", methods=["POST"])
def modify_project():
    modify_projects = {
    "id" : request.form["m_id"],
    "project" : request.form["m_project"],
    "description" : request.form["m_description"],
    "start_date" : request.form["m_start_date"],
    "end_date" : request.form["m_end_date"],
    "people" : request.form["m_people"]
    }
    con.execute('''UPDATE Project_table SET project=(?), description=(?), start_date=(?), end_date=(?), people=(?) WHERE id=(?)''',
    (modify_projects["project"], modify_projects["description"], modify_projects["start_date"], modify_projects["end_date"], modify_projects["people"], modify_projects["id"]))
    return redirect("/projects")

#Maintenance page
@app.route("/maintenance")
def maintenance():
    tasks = con.execute("SELECT * FROM Maint_table").fetchall()
    return render_template("maintenance.html",tasks=tasks,total_fertiliser=total_fertiliser)

#New maintenance task
@app.route("/new_task")
def new_task():
    return render_template("add_task.html")

@app.route("/add_task", methods=["POST"])
def add_task():
    tasks = {
    "task" : request.form["m_task"],
    "description" : request.form["m_description"],
    "start_date" : request.form["m_start_date"],
    "frequency" : request.form["m_frequency"],
    "fertiliser" : int(request.form["m_fertiliser"]),
    "people" : request.form["m_people"]
    }
    
    #calculate fertiliser required for the week
    if (tasks["frequency"]) == "Daily":
        fertiliser_calc = (tasks["fertiliser"]) * 7
    elif (tasks["frequency"]) == "Fortnightly":
        fertiliser_calc = (tasks["fertiliser"]) / 2
    elif (tasks["frequency"]) == "Monthly":
        fertiliser_calc = (tasks["fertiliser"]) / 4
    elif (tasks["frequency"]) == "Yearly":
        fertiliser_calc = (tasks["fertiliser"]) / 52
    else:
        fertiliser_calc = (tasks["fertiliser"])

    global total_fertiliser
    total_fertiliser = fertiliser_calc + total_fertiliser

    con.execute('''INSERT INTO Maint_table(task,description,start_date,frequency,fertiliser,people) VALUES(?,?,?,?,?,?)''', (tasks["task"], tasks["description"], tasks["start_date"], tasks["frequency"], tasks["fertiliser"], tasks["people"]))
    return redirect("/maintenance")

#Remove task
@app.route("/remove_task")
def remove_task():
    return render_template("delete_task.html")

@app.route("/delete_task", methods=["POST"])
def delete_task():
    delete_tasks = {
    "id" : request.form["m_id"]
    }
    con.execute('''DELETE FROM Maint_table WHERE id=(?)''',
(delete_tasks["id"]))
    return redirect("/maintenance")

#Update task
@app.route("/update_task")
def update_task():
    return render_template("modify_task.html")

@app.route("/modify_task", methods=["POST"])
def modify_task():
    modify_tasks = {
    "id" : request.form["m_id"],
    "task" : request.form["m_task"],
    "description" : request.form["m_description"],
    "start_date" : request.form["m_start_date"],
    "frequency" : request.form["m_frequency"],
    "people" : request.form["m_people"]
    }
    con.execute('''UPDATE Maint_table SET task=(?), description=(?), start_date=(?), frequency=(?), people=(?) WHERE id=(?)''',
    (modify_tasks["task"], modify_tasks["description"], modify_tasks["start_date"], modify_tasks["frequency"], modify_tasks["people"], modify_tasks["id"]))
    return redirect("/maintenance")

#Calendar
@app.route("/calendar")
def calendar():
    return render_template("calendar.html")

#New student
@app.route("/new_student")
def new_student():
    return render_template("add_student.html")

@app.route("/add_student", methods=["POST"])
def add_student():
    students = {
    "first_name" : request.form["m_first_name"],
    "last_name" : request.form["m_last_name"],
    "year" : request.form["m_year"],
    }
    con.execute('''INSERT INTO Student_table(first_name,last_name,year) VALUES(?,?,?)''', (students["first_name"], students["last_name"], students["year"]))
    return redirect("/projects")

#Show project details
@app.route("/details")
def details():
    students = con.execute('''SELECT * FROM Student_table''').fetchall()
    project = con.execute('''SELECT project FROM Project_table WHERE id=(1)''').fetchall()
    return render_template("details.html", students=students, project=project)

#Modify Student
@app.route("/update_student")
def update_student():
    return render_template("modify_student.html")

@app.route("/modify_student", methods=["POST"])
def modify_student():
    modify_students = {
    "id" : request.form["m_id"],
    "first_name" : request.form["m_first_name"],
    "last_name" : request.form["m_last_name"],
    "year" : request.form["m_year"],
    }
    con.execute('''UPDATE Student_table SET first_name=(?), last_name=(?), year=(?) WHERE id=(?)''', (modify_students["first_name"], modify_students["last_name"], modify_students["year"], modify_students["id"]))
    return redirect("/details")

#Send email
@app.route("/send_email")
def send_email():
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "Eco Squad <cnesci01@icloud.com>"

    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = "nescic@smc.sa.edu.au"

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "ap-southeast-2"

    # The subject line for the email.
    SUBJECT = "Weekly Fertiliser Order"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("You will need to order" + str(total_fertiliser) + "of fertiliser this week.")
                
    # The HTML body of the email.
    BODY_HTML = render_template("email.html", total_fertiliser=str(total_fertiliser),name=request.cookies.get('Name'))

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    #Provide the contents of the email.
    response = client.send_email(
        Destination={
            'ToAddresses': [
                RECIPIENT,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': BODY_HTML,
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': BODY_TEXT,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            },
        },
        Source=SENDER,
        # If you are not using a configuration set, comment or delete the
        # following line
        #ConfigurationSetName=CONFIGURATION_SET,
    )
    return redirect ("/")

app.secret_key = os.urandom(12)
app.run(debug=True)