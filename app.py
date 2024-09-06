from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
import pymongo
import bcrypt
from werkzeug.utils import secure_filename
import os
from bson.objectid import ObjectId


app = Flask(__name__)
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb://localhost:27017/total_record")
db = client.get_database('total_record')
records = db.register
todos = db.todos


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route("/", methods=['POST', 'GET'])
def index():
    message = ''
    if "email" in session:
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        avatar = request.files['avatar']

        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)

        if avatar :
            filename = secure_filename(avatar.filename)
            avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            avatar_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            avatar_url = None

        hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
        user_input = {'name': user, 'email': email, 'password': hashed, 'avatar': avatar_url}
        records.insert_one(user_input)
        flash('Registration successful! Please login to continue.', 'success')
        return redirect(url_for("login"))

    return render_template('index.html')




@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = records.find_one({"email": email})
        if email_found:
            passwordcheck = email_found['password']
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email
                return redirect(url_for('dashboard'))
            else:
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    
    return render_template('login.html', message=message)

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
    return redirect(url_for("login"))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if "email" in session:
        email = session["email"]
        user_data = records.find_one({"email": email})
        todos_list = todos.find({"user_email": email})
        return render_template('dashboard.html', user=user_data, todos=todos_list)
    else:
        return redirect(url_for("login"))
    
@app.route("/add_todo", methods=["POST"])
def add_todo():
    if "email" in session:
        task = request.form.get("task")
        if task:
            todos.insert_one({"task": task, "user_email": session["email"]})
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("login"))

@app.route("/edit_todo/<todo_id>", methods=["GET", "POST"])
def edit_todo(todo_id):
    todo = todos.find_one({"_id": ObjectId(todo_id)})
    if request.method == "POST":
        task = request.form.get("task")
        todos.update_one({"_id": ObjectId(todo_id)}, {"$set": {"task": task}})
        return redirect(url_for("dashboard"))
    return render_template("edit_todo.html", todo=todo)

@app.route("/delete_todo/<todo_id>")
def delete_todo(todo_id):
    todos.delete_one({"_id": ObjectId(todo_id)})
    return redirect(url_for("dashboard"))




    
if __name__ == "__main__":
    app.run(debug=True)