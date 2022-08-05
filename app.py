from flask import Flask, render_template, redirect, request, make_response, session
import sqlite3
import os

app = Flask(__name__)
projects=[]
delete_projects=[]
user_list=['admin']
pass_list=['password']
the_user_name=''

#Connect database
con = sqlite3.connect('projects-db.db', check_same_thread=False)

#If the tables already exists, delete 
con.execute("DROP TABLE IF EXISTS Project_table;")

#Create tables
con.execute('''CREATE TABLE Project_table(id INTEGER PRIMARY KEY, project TEXT, description TEXT, start_date INTEGER, end_date INTEGER, people INTEGER)''')

#Create account
@app.route("/create_account")
def create_account():
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register():
    user_list.append(request.form['username'])
    pass_list.append(request.form['password'])
    return redirect('/')

#Login page
@app.route('/login', methods=['POST'])
def do_admin_login():
    if (request.form['password'] in pass_list) and (request.form['username'] in user_list):
        the_user_name = request.form['username']
        session['logged_in'] = True
        #Set cookie
        resp = make_response(redirect('/'))
        resp.set_cookie('Name',the_user_name)
        return resp
    else:
        return render_template('login.html',creds='Invalid Credentials')

#Home page
@app.route("/")
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        name = request.cookies.get('Name')
        return render_template('index.html',name=name)

#NEW projects read
@app.route("/projects")
def new_projects():
    new_projects = con.execute("SELECT * FROM Project_table").fetchall()
    return render_template("projects.html",new_projects=new_projects)

#NEW sort by
@app.route("/sort_by_dsc")
def sort_by_dsc():
    new_projects = con.execute('''SELECT * FROM Project_table ORDER BY price ASC''').fetchall()
    return render_template("new_projects.html",new_projects=new_projects)

#NEW add project
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
    
    return redirect("/")

#NEW delete project
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
    return redirect("/")

#NEW update project
@app.route("/update_project")
def update_project():
    return render_template("modify_project.html")

@app.route("/modify_project", methods=["POST"])
def modify_project():
    modify_projects = {
    }

app.secret_key = os.urandom(12)
app.run(debug=True)