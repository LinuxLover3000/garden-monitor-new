from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import exifread

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
db = SQLAlchemy(app)

class Todo(db.Model): #setting columns for database
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self): #function to return string
        return "<Task %r>" % self.id


@app.route("/", methods = ["POST", "GET"])
def index():
    if request.method == "POST":
        task_content = request.form["content"] #id from form
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task) #add to database
            db.session.commit()
            return redirect("/")
        except:
            return "Error adding task"
    else:
        tasks = Todo.query.order_by(Todo.date_created).all() #returns all task objects
        return render_template("index.html", tasks=tasks) #checks in \templates\

@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "Error deleting task"

@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form["content"] #set task's content to input from form
        try:
            db.session.commit() #no need to add new entry, only commit changes
            return redirect("/")
        except:
            return "Error updating task"
    else:
        return render_template("update.html", task=task)

@app.route("/webcam/")
def webcam():
    img = open("Olympus_C8080WZ.jpg", "rb")
    tags = exifread.process_file(img)
    dt = tags["Image DateTime"] #process string to make more user-friendly?

    return "a"

if __name__ == "__main__":
    app.run(debug = True)