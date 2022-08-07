from flask import Flask, render_template, redirect, request, make_response, session
import sqlite3
import os

app = Flask(__name__)
projects=[]
tasks=[]
delete_projects=[]
modify_projects=[]
the_user_name=''

#Connect database
con = sqlite3.connect('projects.db', check_same_thread=False)

#If the tables already exists, delete 
con.execute("DROP TABLE IF EXISTS Project_table;")
con.execute("DROP TABLE IF EXISTS Maint_table;")

#Create tables
con.execute('''CREATE TABLE Project_table(id INTEGER PRIMARY KEY, project TEXT, description TEXT, start_date INTEGER, end_date INTEGER, people TEXT)''')
con.execute('''CREATE TABLE Maint_table(id INTEGER PRIMARY KEY, task TEXT, description TEXT, start_date INTEGER, frequency TEXT, people INTEGER)''')

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
        return render_template('index.html',name=name,projects=projects)

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
    "start_date" : request.form["m_start_date"],
    "end_date" : request.form["m_end_date"],
    "people" : request.form["m_people"]
    }
    con.execute('''INSERT INTO Project_table(project,description,start_date,end_date,people) VALUES(?,?,?,?,?)''', (projects["project"], projects["description"], projects["start_date"], projects["end_date"], projects["people"]))
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
    print(delete_project)
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
    return render_template("maintenance.html",tasks=tasks)

app.secret_key = os.urandom(12)
app.run(debug=True)