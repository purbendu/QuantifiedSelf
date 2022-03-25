
import os
from flask import Flask, redirect, session
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
import numpy as np
import matplotlib

matplotlib.use('Agg')
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

plt.style.use('seaborn-whitegrid')
current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(
    current_dir, "database.sqlite3")
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

loggedIn = []


class authentication(db.Model):
    __tablename__ = 'authentication'
    username = db.Column(db.String,
                         primary_key=True,
                         nullable=False,
                         unique=True)
    password = db.Column(db.String, nullable=False)


class trackers(db.Model):
    __tablename__ = 'trackers'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String,
                         db.ForeignKey('authentication.username'),
                         nullable=False)
    trackerType = db.Column(db.Integer, nullable=False)
    trackerName = db.Column(db.String, nullable=False)
    lastTracked = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)


class multiSettings(db.Model):
    __tablename__ = 'multiSettings'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String,
                         db.ForeignKey('authentication.username'),
                         nullable=False)
    trackerName = db.Column(db.String,
                            db.ForeignKey('trackers.trackerName'),
                            nullable=False)
    settings = db.Column(db.String, nullable=True)


class multiple(db.Model):
    __tablename__ = 'multiple'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String,
                         db.ForeignKey('authentication.username'),
                         nullable=False)
    value = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)
    trackerName = db.Column(db.String, nullable=False)
    notes = db.Column(db.String, nullable=True)


class numerical(db.Model):
    __tablename__ = 'numerical'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String,
                         db.ForeignKey('authentication.username'),
                         nullable=False)
    value = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)
    trackerName = db.Column(db.String, nullable=False)
    notes = db.Column(db.String, nullable=True)


class boolean(db.Model):
    __tablename__ = 'boolean'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String,
                         db.ForeignKey('authentication.username'),
                         nullable=False)
    value = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)
    trackerName = db.Column(db.String, nullable=False)
    notes = db.Column(db.String, nullable=True)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        id = db.session.query(authentication).filter(
            authentication.username == username).first()
        if id.password == password:
            loggedIn.append(username)
            return redirect("/" + username + "/trackers")

        elif id == None:
            return render_template("login.html", n=1)
        else:
            return render_template("login.html", n=2)
    else:
        return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        entry = db.session.query(authentication).filter(
            authentication.username == username).all()
        if entry != []:
            return render_template("duplicateUserName.html")

        entry = authentication(username=username, password=password)
        db.session.add(entry)
        db.session.commit()
        db.session.close_all()

        return redirect("/" + username + "/trackers")
    else:
        return render_template("signup.html")


@app.route("/<string:username>/trackers", methods=["GET", "POST"])
def tracker(username):
    if len(loggedIn) == 0 or username != loggedIn[0]:
        return redirect("/")
    names = db.session.query(trackers).filter(
        trackers.username == username).all()
    if names == []:
        return render_template("noTracker.html", username=username)
    return render_template("trackers.html", username=username, names=names)


@app.route("/<string:username>/logout", methods=["GET", "POST"])
def logout(username):
    loggedIn.remove(username)
    return redirect("/")


@app.route("/<string:username>/trackers/<string:trackerName>/show",
           methods=["GET", "POST"])
def showData(username, trackerName):
    if len(loggedIn) == 0 or username != loggedIn[0]:
        return redirect("/")

    dataType = db.session.query(trackers).filter(
        trackers.username == username,
        trackers.trackerName == trackerName).first()

    if dataType.trackerType == 1:  # Numerical
        entry = db.session.query(numerical).filter(
            numerical.username == username,
            numerical.trackerName == trackerName).all()
        if entry == []:
            return render_template("noRecords.html",
                                   username=username,
                                   trackerName=trackerName)
        y, x = [], []
        for data in entry:
            y.append(data.value)
            x.append(data.date)

        f = plt.figure()
        f.set_figwidth(18)
        f.set_figheight(8)
        plt.plot(x, y, marker="o")
        plt.xlabel("Dates")
        plt.ylabel("Result")
        plt.savefig("static/trendline.png")

        return render_template("showData.html",
                               entry=entry,
                               trackerName=trackerName,
                               username=username,
                               image="/static/trendline.png")

    elif dataType.trackerType == 2:  # boolean
        entry = db.session.query(boolean).filter(
            boolean.username == username,
            boolean.trackerName == trackerName).all()
        if entry == []:
            return render_template("noRecords.html",
                                   username=username,
                                   trackerName=trackerName)
        y, x = [], []
        for data in entry:
            y.append(data.value)
            x.append(data.date)

        f = plt.figure()
        f.set_figwidth(18)
        f.set_figheight(8)
        plt.plot(x, y, marker="o")
        plt.xlabel("Dates")
        plt.ylabel("Value")
        my_yticks = []
        for pt in y:
            if int(pt) == 1:
                my_yticks.append("Completed")
            else:
                my_yticks.append("NOT Completed")

        plt.yticks(y, my_yticks)
        plt.savefig("static/trendline.png")

        return render_template("showData.html",
                               entry=entry,
                               trackerName=trackerName,
                               username=username,
                               image="/static/trendline.png",
                               b=1)

    elif dataType.trackerType == 3:  # multiple
        entry = db.session.query(multiple).filter(
            multiple.username == username,
            multiple.trackerName == trackerName).all()
        if entry == []:
            return render_template("noRecords.html",
                                   username=username,
                                   trackerName=trackerName)
        return render_template("showData.html",
                               entry=entry,
                               trackerName=trackerName,
                               username=username,
                               b=3)


@app.route("/<string:username>/trackers/add", methods=["GET", "POST"])
def addTracker(username):
    if len(loggedIn) == 0 or username != loggedIn[0]:
        return redirect("/")

    if request.method == "POST":

        name = request.form.get("name")
        description = request.form.get("description")
        type = request.form.get("type")

        dataType = db.session.query(trackers).filter(
            trackers.username == username, trackers.trackerName == name).all()
        if dataType != []:
            return render_template("duplicateTracker.html")

        entry = trackers(username=username,
                         trackerName=name,
                         description=description,
                         trackerType=type)
        db.session.add(entry)
        db.session.commit()
        db.session.close_all()

        if type == '3':
            settings = request.form.get("settings")
            settings = settings.split(",")

            for s in settings:
                entry2 = multiSettings(username=username,
                                       trackerName=name,
                                       settings=s)
                db.session.add(entry2)
                db.session.commit()
                db.session.close_all()

        return redirect("/" + username + "/trackers")

    elif request.method == "GET":
        return render_template("addTracker.html", username=username)


@app.route("/<string:username>/trackers/<string:trackerName>/edit",
           methods=["GET", "POST"])
def editTracker(username, trackerName):
    if len(loggedIn) == 0 or username != loggedIn[0]:
        return redirect("/")

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        dataType = db.session.query(trackers).filter(
            trackers.username == username,
            trackers.trackerName == trackerName).first()
        dataType.description = description
        dataType.trackerName = name

        if dataType.trackerType == 1:
            entry = db.session.query(numerical).filter(
                numerical.username == username,
                numerical.trackerName == trackerName).all()

            for data in entry:
                data.trackerName = name

            db.session.commit()
            db.session.close_all()
        elif dataType.trackerType == 2:
            entry = db.session.query(boolean).filter(
                boolean.username == username,
                boolean.trackerName == trackerName).all()

            for data in entry:
                data.trackerName = name

            db.session.commit()
            db.session.close_all()
        elif dataType.trackerType == 3:
            entry = db.session.query(multiple).filter(
                multiple.username == username,
                multiple.trackerName == trackerName).all()

            for data in entry:
                data.trackerName = name

            entry = db.session.query(multiSettings).filter(
                multiSettings.username == username,
                multiSettings.trackerName == trackerName).all()
            for data in entry:
                data.trackerName = name

            db.session.commit()
            db.session.close_all()

        return redirect("/" + username + "/trackers")

    elif request.method == "GET":
        dataType = db.session.query(trackers).filter(
            trackers.username == username,
            trackers.trackerName == trackerName).first()
        return render_template("updateTracker.html",
                               trackerName=trackerName,
                               username=username,
                               data=dataType)


@app.route("/<string:username>/trackers/<string:trackerName>/add",
           methods=["GET", "POST"])
def addData(username, trackerName):
    if len(loggedIn) == 0 or username != loggedIn[0]:
        return redirect("/")

    if request.method == "POST":
        date = datetime.now()

        entry = db.session.query(trackers).filter(
            trackers.username == username,
            trackers.trackerName == trackerName).first()
        entry.lastTracked = date

        db.session.commit()
        db.session.close_all()

        dataType = db.session.query(trackers).filter(
            trackers.username == username,
            trackers.trackerName == trackerName).first()

        if dataType.trackerType == 1:
            value = request.form.get("value")
            notes = request.form.get("notes")

            entry = numerical(username=username,
                              value=value,
                              notes=notes,
                              date=date,
                              trackerName=trackerName)
            db.session.add(entry)
            db.session.commit()
            db.session.close_all()

        elif dataType.trackerType == 2:
            value = request.form.get("value")
            if value == "No":
                value = int(0)
            elif value == "Yes":
                value = int(1)
            notes = request.form.get("notes")

            entry = boolean(username=username,
                            value=value,
                            notes=notes,
                            date=date,
                            trackerName=trackerName)
            db.session.add(entry)
            db.session.commit()
            db.session.close_all()

        elif dataType.trackerType == 3:
            values = request.form.getlist("value")
            notes = request.form.get("notes")
            for value in values:
                entry = multiple(username=username,
                                 value=value,
                                 notes=notes,
                                 date=date,
                                 trackerName=trackerName)
                db.session.add(entry)
                db.session.commit()
                db.session.close_all()

        return redirect("/" + username + "/trackers/" + trackerName + "/show")

    elif request.method == "GET":
        dataType = db.session.query(trackers).filter(
            trackers.username == username,
            trackers.trackerName == trackerName).first()
        if dataType.trackerType == 1:
            return render_template("addData.html",
                                   trackerName=trackerName,
                                   username=username,
                                   flag=1)
        elif dataType.trackerType == 2:
            return render_template("addData.html",
                                   trackerName=trackerName,
                                   username=username,
                                   flag=2)
        elif dataType.trackerType == 3:
            settings = db.session.query(multiSettings).filter(
                multiSettings.username == username,
                multiSettings.trackerName == trackerName).all()
            return render_template("addData.html",
                                   trackerName=trackerName,
                                   username=username,
                                   flag=3,
                                   settings=settings)


@app.route("/<string:username>/trackers/<string:trackerName>/<int:id>/edit",
           methods=["GET", "POST"])
def editData(username, trackerName, id):
    if len(loggedIn) == 0 or username != loggedIn[0]:
        return redirect("/")

    if request.method == "POST":
        value = request.form.get("value")
        if value == "No":
            value = int(0)
        elif value == "Yes":
            value = int(1)
        notes = request.form.get("notes")

        dataType = db.session.query(trackers).filter(
            trackers.username == username,
            trackers.trackerName == trackerName).first()

        if dataType.trackerType == 1:
            entry = db.session.query(numerical).filter(
                numerical.id == id).first()
            entry.value = value
            entry.notes = notes
            db.session.commit()
            db.session.close_all()
        elif dataType.trackerType == 2:
            entry = db.session.query(boolean).filter(boolean.id == id).first()
            entry.value = value
            entry.notes = notes
            db.session.commit()
            db.session.close_all()

        elif dataType.trackerType == 3:
            entry = db.session.query(multiple).filter(multiple.id == id).first()
            entry.value = value
            entry.notes = notes
            db.session.commit()
            db.session.close_all()

        return redirect("/" + username + "/trackers/" + trackerName + "/show")

    elif request.method == "GET":

        dataType = db.session.query(trackers).filter(
            trackers.username == username,
            trackers.trackerName == trackerName).first()
        if dataType.trackerType == 1:
            entry = db.session.query(numerical).filter(
                numerical.id == id).first()
            return render_template("updateData.html",
                                   trackerName=trackerName,
                                   username=username,
                                   flag=1,
                                   entry=entry,
                                   id=id)

        elif dataType.trackerType == 2:
            entry = db.session.query(boolean).filter(boolean.id == id).first()
            return render_template("updateData.html",
                                   trackerName=trackerName,
                                   username=username,
                                   flag=2,
                                   entry=entry,
                                   id=id)

        elif dataType.trackerType == 3:  # multiple
            entry = db.session.query(multiple).filter(
                multiple.id == id).first()
            settings = db.session.query(multiSettings).filter(
                multiSettings.username == username,
                multiSettings.trackerName == trackerName).all()
            return render_template("updateData.html",
                                   trackerName=trackerName,
                                   username=username,
                                   flag=3,
                                   entry=entry,
                                   id=id,
                                   settings=settings)


@app.route("/<string:username>/trackers/<string:trackerName>/<int:id>/delete",
           methods=["GET", "POST"])
def deleteData(username, trackerName, id):
    if len(loggedIn) == 0 or username != loggedIn[0]:
        return redirect("/")

    if request.method == "GET":
        dataType = db.session.query(trackers).filter(
            trackers.username == username,
            trackers.trackerName == trackerName).first()

        if dataType.trackerType == 1:
            entry = db.session.query(numerical).filter(
                numerical.id == id).first()
            db.session.delete(entry)
            db.session.commit()

        elif dataType.trackerType == 2:
            entry = db.session.query(boolean).filter(boolean.id == id).first()
            db.session.delete(entry)
            db.session.commit()

        elif dataType.trackerType == 3:
            entry = db.session.query(multiple).filter(multiple.id == id).first()
            db.session.delete(entry)
            db.session.commit()

        return redirect("/" + username + "/trackers/" + trackerName + "/show")

@app.route("/<string:username>/trackers/<string:trackerName>/delete",
           methods=["GET", "POST"])
def deleteTracker(username, trackerName):
    if len(loggedIn) == 0 or username != loggedIn[0]:
        return redirect("/")

    if request.method == "GET":
        dataType = db.session.query(trackers).filter(
            trackers.username == username,
            trackers.trackerName == trackerName).first()

        if dataType.trackerType == 1:
            entry = db.session.query(numerical).filter(numerical.username == username,
            numerical.trackerName == trackerName).all()
            for data in entry:
                db.session.delete(data)
                db.session.commit()

            db.session.delete(dataType)
            db.session.commit()


        elif dataType.trackerType == 2:
            entry = db.session.query(boolean).filter(boolean.username == username,
                                                       boolean.trackerName == trackerName).all()
            for data in entry:
                db.session.delete(data)
                db.session.commit()

            db.session.delete(dataType)
            db.session.commit()


        elif dataType.trackerType == 3:
            entry = db.session.query(multiple).filter(multiple.username == username,
                                                     multiple.trackerName == trackerName).all()
            for data in entry:
                db.session.delete(data)
                db.session.commit()

            db.session.delete(dataType)
            db.session.commit()

        return redirect("/" + username + "/trackers")


if __name__ == '__main__':
    app.run()
