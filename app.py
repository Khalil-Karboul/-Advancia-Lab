import os
import requests
from logging import log
from flask import Flask,  render_template, url_for, request, session, redirect, flash, abort, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import select
from flask_admin import Admin, expose, BaseView, form
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from urllib.parse import urlparse, urljoin
from flask_mail import Mail, Message
from flask_admin.base import AdminIndexView, BaseView
from wtforms import StringField
from datetime import datetime, date
import select
import threading
import uuid
import flask
import paramiko
import logging
from flask_sse import sse

# ----------------------- Configuration -----------------------
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.register_blueprint(sse, url_prefix='/stream')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/users_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecret'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

# ----------------------- Models -----------------------


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    users = db.relationship('User', backref='role', lazy=True)


class Participate(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    participant_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    training_id = db.Column(db.Integer, db.ForeignKey(
        'training.id'), nullable=False)


class Training(db.Model):
    __tablename__ = 'training'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey(
        'course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    information = db.Column(db.String(1000))
    users = db.relationship('Participate', backref='training', lazy=True)


class Course(db.Model):
    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    trainings = db.relationship("Training", backref='ticket', lazy=True)

    def __repr__(self):
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    tel = db.Column(db.Integer, unique=True, nullable=True)
    password = db.Column(db.String(20), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    is_banned = db.Column(db.Boolean, default=False, nullable=False)
    participate = db.Column(db.Boolean, default=False, nullable=False)
    trainings = db.relationship("Training", backref='training', lazy=True)
    tickets = db.relationship('Ticket', backref='ticket', lazy=True)
    participants = db.relationship('Participate', backref='user', lazy=True)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1200), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    trainer_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    msgs = db.relationship('Comment', backref='comment', lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    msg = db.Column(db.String(1000), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey(
        'ticket.id'), nullable=False)


app.run()

# -----------------------Functions-----------------------

if __name__ == '__main__':
    app.run(debug=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login')
def index():
    return redirect(url_for('login'))


@app.route('/', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']
    e = User.query.filter_by(email=email).first()
    p = User.query.filter_by(password=password).first()

    if (not e and not p) or (not e and p) or (e and not p):
        flash(f"Email OR PASSWORD DOES NOT EXIST!")
        return redirect(url_for('login'))
    else:
        login_user(e)
        if current_user.role_id == 1:
            return redirect(url_for('home_admin'))
        if current_user.role_id == 2:
            return redirect(url_for('display'))
        if current_user.role_id == 3:
            all_data = db.session.query(User, Participate, Training).filter(
            current_user.id == Participate.participant_id, Training.id== Participate.training_id).first()        
            if (date.today() > all_data.Training.start_date) and (date.today() < all_data.Training.end_date):
                return redirect(url_for('home'))
            else:
                flash(f"YOU HAVE NO ACCESS TO YOUR ACCOUNT!")
                return redirect(url_for('login'))
 


@app.route('/')
# @login_required
def logout():
    logout_user()
    return render_template('login.html')


@app.route('/home')
@login_required
def home():
    if current_user.role_id == 3:
        return render_template('/participant/home.html')
    else:
        return abort(400)


@app.route('/vm_1')
@login_required
def vm1():
    if current_user.role_id == 3:
        return render_template('/participant/vm1.html')
    else:
        return abort(400)


@app.route('/vm_2')
@login_required
def vm2():
    if current_user.role_id == 3:
        return render_template('/participant/vm2.html')
    else:
        return abort(400)


@app.route('/trainer/vm_1')
@login_required
def vm1t():
    if current_user.role_id == 2:
        return render_template('/trainer/vm1.html')
    else:
        return abort(400)


@app.route('/trainer/vm_2')
@login_required
def vm2t():
    if current_user.role_id == 2:
        return render_template('/trainer/vm2.html')
    else:
        return abort(400)


@app.route('/trainer/participants')
@login_required
def display():
    if current_user.role_id == 2:
        all_data = db.session.query(Training, Course).filter(
            Training.course_id == Course.id).all()
        participate = db.session.query(Participate, User).filter(
            User.id == Participate.participant_id).all()
        return render_template('/trainer/participantlist.html', data=all_data, participate=participate, title="My Participants")
    else:
        return abort(400)


@app.route('/admin')
@login_required
def home_admin():
    if current_user.role_id == 1:
        all_data = all_data = db.session.query(Training, User, Course).filter(
            Training.user_id == User.id, Training.course_id == Course.id).all()
        participants = db.session.query(User, Participate).filter(
            User.id == Participate.participant_id)

        return render_template('/admin/training_session.html',  participants=participants, data=all_data, title="Home")
    else:
        return abort(400)

# ____________________________________________TRAINER CRUD____________________________________________


@app.route('/admin/trainer_list')
# @login_required
def trainerlist():
    if current_user.role_id == 1:
        all_data = User.query.filter(User.role_id == 2).all()
        return render_template('/admin/trainerlist.html', data=all_data, title="Trainer List")
    else:
        return abort(400)


@app.route('/admin/trainer_list/create', methods=['POST'])
def insert_trainer():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        tel = request.form['tel']
        password = request.form['password']
        create_trainer = User(firstname=firstname, lastname=lastname,
                              email=email, tel=tel, password=password, role_id=2)
        db.session.add(create_trainer)
        db.session.commit()
        flash("Trainer Added Successfully")
        return redirect('/admin/trainer_list')


@app.route('/admin/trainer_list/update<id>', methods=['POST'])
def update_trainer(id):
    if request.method == 'POST':
        my_data = User.query.get(id)
        my_data.firstname = request.form['firstnameEdit']
        my_data.lastname = request.form['lastnameEdit']
        my_data.email = request.form['emailEdit']
        my_data.tel = request.form['telEdit']
        my_data.password = request.form['passwordEdit']
        db.session.commit()
        flash("Trainer Updated Successfully")
        return redirect('/admin/trainer_list')


@app.route('/admin/trainer_list/<id>/', methods=['GET', 'POST'])
def delete_trainer(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash("Trainer Deleted Successfully")
    return redirect('/admin/trainer_list')


# ____________________________________________Participant CRUD____________________________________________

@app.route('/admin/participant_list')
# @login_required
def participantlist():
    if current_user.role_id == 1:
        all_data = User.query.filter(User.role_id == 3).all()
        return render_template('/admin/participantlist.html', data=all_data, title="Participant List")
    else:
        return abort(400)


@app.route('/admin/participant_list/create', methods=['POST'])
def insert_participant():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        tel = request.form['tel']
        password = request.form['password']
        create_trainer = User(firstname=firstname, lastname=lastname,
                              email=email, tel=tel, password=password, role_id=3)
        db.session.add(create_trainer)
        db.session.commit()
        flash("Participant Added Successfully")
        return redirect('/admin/participant_list')


@app.route('/admin/participant_list/update<id>', methods=['POST'])
def update_participant(id):
    if request.method == 'POST':
        my_data = User.query.get(id)
        my_data.firstname = request.form['firstname']
        my_data.lastname = request.form['lastname']
        my_data.email = request.form['email']
        my_data.tel = request.form['tel']
        my_data.password = request.form['password']
        db.session.commit()
        flash("Participant Updated Successfully")
        return redirect('/admin/participant_list')


@app.route('/admin/participant_list/<id>/', methods=['GET', 'POST'])
def delete_participant(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash("Participant Deleted Successfully")
    return redirect('/admin/participant_list')

# ____________________________________________TICKET____________________________________________


@app.route('/admin/all_tickets')
@login_required
def alltickets():
    if current_user.role_id == 1:
        all_data = db.session.query(Ticket, User).filter(
            User.id == Ticket.trainer_id).order_by(Ticket.datetime.desc()).all()
        return render_template('admin/ticketlist.html', data=all_data, title="Ticket List")
    else:
        return abort(400)


@app.route('/admin/reply_ticket<id>', methods=['POST', 'GET'])
@login_required
def ticket_management(id):
    if current_user.role_id == 1:
        ticket = Ticket.query.filter(Ticket.id == id).first()
        all_replies = Comment.query.filter(
            Comment.ticket_id == id).order_by(Comment.datetime.desc()).all()
        return render_template('admin/replyticket.html', data=all_replies, ticket=ticket, title="Ticket Tracking")
    else:
        return abort(400)


@app.route('/admin/close_ticket<id>', methods=['POST', 'GET'])
def close_ticket(id):
    if request.method == 'POST':
        ticket = Ticket.query.get(id)
        ticket.status = 'Resolved'
        db.session.commit()
        flash("Ticket Closed Successfully")
        return redirect('/admin/all_tickets')


@app.route('/admin/<id>reply_ticket', methods=['POST', 'GET'])
def reply_ticket(id):
    if request.method == 'POST':
        reply = request.form['reply']
        reply = 'Admin: '+reply
        re_ticket = Comment(msg=reply, datetime=datetime.now(), ticket_id=id)
        db.session.add(re_ticket)
        db.session.commit()
        flash("Ticket Replied Successfully")
        return redirect('/admin/all_tickets')


@app.route('/trainer/my_tickets')
@login_required
def ticket():
    if current_user.role_id == 2:
        all_data = Ticket.query.order_by(Ticket.datetime.desc()).filter(
            Ticket.trainer_id == current_user.id).all()
        return render_template('trainer/ticketlist.html', data=all_data, title="Ticket List")
    else:
        return abort(400)


@app.route('/trainer/submit_ticket', methods=['POST'])
def insert():
    if request.method == 'POST':
        category = request.form['category']
        subject = request.form['subject']
        description = request.form['description']
        create_post = Ticket(category=category, subject=subject, description=description,
                             status='In Progress', datetime=datetime.now(), trainer_id=current_user.id)
        db.session.add(create_post)
        db.session.commit()
        return redirect('/trainer/my_tickets')


@app.route('/trainer/ticket_history<id>', methods=['POST', 'GET'])
@login_required
def display_ticket_trainer(id):
    if current_user.role_id == 2:
        ticket = Ticket.query.filter(Ticket.id == id).first()
        all_replies = Comment.query.filter(
            Comment.ticket_id == id).order_by(Comment.datetime.desc()).all()
        return render_template('trainer/replyticket.html', data=all_replies, ticket=ticket, title="Ticket Tracking")
    else:
        return abort(400)


@app.route('/trainer/add_ticket', methods=['POST', 'GET'])
@login_required
def submit_ticket():
    if current_user.role_id == 2:
        return render_template('trainer/ticket.html')
    else:
        return abort(400)


@app.route('/trainer/<id>reply_ticket', methods=['POST', 'GET'])
def reply_ticket_trainer(id):
    if request.method == 'POST':
        reply = request.form['reply']
        reply = str(current_user.firstname)+' ' + \
            str(current_user.lastname)+': '+reply
        re_ticket = Comment(msg=reply, datetime=datetime.now(), ticket_id=id)
        db.session.add(re_ticket)
        db.session.commit()
        flash("Ticket Replied Successfully")
        return redirect('/trainer/my_tickets')

# ____________________________________________TRAINING____________________________________________


@app.route('/admin/training')
@login_required
def traininglist():
    if current_user.role_id == 1:
        all_data = db.session.query(Training, User, Course).filter(
            User.id == Training.user_id, Training.course_id == Course.id).all()
        all_data2 = db.session.query(Training, User).filter(
            User.id == Training.user_id).all()
        trainers = User.query.filter(User.role_id == 2).all()
        participants = User.query.filter(
            User.role_id == 3, User.participate == False).all()
        courses = Course.query.all()
        participants2 = db.session.query(User, Participate).filter(
            User.id == Participate.participant_id).all()
        return render_template('/admin/traininglist.html', participants2=participants2, courses=courses, data=all_data, trainers=trainers, data2=all_data2, participants=participants, title="Training Session")
    else:
        return abort(400)


@app.route('/admin/create_training_session', methods=['POST', 'GET'])
def create_training_session():
    if request.method == 'POST':
        course_id = request.form['course_id']
        trainers = request.form['trainer_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        information = request.form['information']
        create_course = Training(course_id=course_id, user_id=trainers,
                                 start_date=start_date, end_date=end_date, information=information)
        db.session.add(create_course)
        db.session.commit()
        flash("Training Session Added Successfully")
        return redirect('/admin/training')


@app.route('/admin/update_training_session<id>', methods=['POST'])
def update_training_session(id):
    if request.method == 'POST':
        data = Training.query.filter(Training.id == id).first()
        data.course_id = request.form['course_id']
        data.user_id = request.form['trainer_id']
        data.start_date = request.form['start_date']
        data.end_date = request.form['end_date']
        data.information = request.form['information']
        db.session.commit()
        flash("Training Session Updated Successfully")
        return redirect('/admin/training')


@app.route('/admin/delete_training_session/<id>/', methods=['GET', 'POST'])
def delete_training_session(id):
    training = Training.query.filter(Training.id == id).first()
    db.session.delete(training)
    db.session.commit()
    flash("Training Session Deleted Successfully")
    return redirect('/admin/training')


@app.route('/admin/<id>add_participant_training_session<idt>', methods=['GET', 'POST'])
def add_participant_training_session(id, idt):
    participant = Participate(participant_id=id, training_id=idt)
    db.session.add(participant)
    db.session.commit()
    user = User.query.filter(User.id == id).first()
    user.participate = True
    db.session.commit()
    flash("Participant Added to Training Session Successfully")
    return redirect('/admin/training')


@app.route('/admin/<id>exclude_participant_training_session<idt>', methods=['GET', 'POST'])
def exclude_participant_training_session(id, idt):
    user = User.query.filter(User.id == id).first()
    user.participate = False
    db.session.commit()
    participant = Participate.query.filter(Training.id == idt).first()
    db.session.delete(participant)
    db.session.commit()
    flash("Participant Excluded from Training Session Successfully")
    return redirect('/admin/training')


# ____________________________________________Course____________________________________________


@app.route('/admin/course')
@login_required
def courselist():
    if current_user.role_id == 1:
        all_data = Course.query.all()
        return render_template('/admin/courselist.html', data=all_data, title="Course List")
    else:
        return abort(400)


@app.route('/admin/create_course', methods=['POST', 'GET'])
def create_course():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        create_course = Course(name=name, description=description)
        db.session.add(create_course)
        db.session.commit()
        flash("Course Added Successfully")
        return redirect('/admin/course')


@app.route('/admin/update_course<id>', methods=['POST'])
def update_course(id):
    if request.method == 'POST':
        my_data = Course.query.get(id)
        my_data.name = request.form['name']
        my_data.description = request.form['description']
        db.session.commit()
        flash("Course Updated Successfully")
        return redirect('/admin/course')


@app.route('/admin/delete_course/<id>/', methods=['GET', 'POST'])
def delete_course(id):
    course = Course.query.get(id)
    db.session.delete(course)
    db.session.commit()
    flash("Course Deleted Successfully")
    return redirect('/admin/course')


# ___________________________________VM___________________________


@app.route('/trainer/vm_1', methods=['POST'])
def vmon():
    url = "http://127.0.0.1:8697/api/vms/6JLR93IRAG6C7QGQFG0AT4FV5VPOCKDI/power"
    payload = "on"
    headers = {
        'Accept': 'application/vnd.vmware.vmw.rest-v1+json',
        'Content-Type': 'application/vnd.vmware.vmw.rest-v1+json',
        'Authorization': 'Basic YWRtaW46MjUxNDEwMDZMb2xA'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    flash(f"State: ON")
    return redirect(url_for('vmon'))


@app.route('/trainer/vm_1#off', methods=['POST'])
def vmoff():
    url = "http://127.0.0.1:8697/api/vms/6JLR93IRAG6C7QGQFG0AT4FV5VPOCKDI/power"
    payload = "off"
    headers = {
        'Accept': 'application/vnd.vmware.vmw.rest-v1+json',
        'Content-Type': 'application/vnd.vmware.vmw.rest-v1+json',
        'Authorization': 'Basic YWRtaW46MjUxNDEwMDZMb2xA'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    flash(f"State: OFF")
    return render_template('/trainer/vm1.html')


@app.route('/trainer/vm_1#state', methods=['POST'])
def vmstate():
    url = "http://127.0.0.1:8697/api/vms/6JLR93IRAG6C7QGQFG0AT4FV5VPOCKDI/power"
    payload = {}
    files = {}
    headers = {
        'Authorization': 'Basic YWRtaW46MjUxNDEwMDZMb2xA'
    }
    response = requests.request(
        "GET", url, headers=headers, data=payload, files=files)
    msg = response.text[20:30]
    flash(msg)
    return render_template('/trainer/vm1.html')


# ___________________________________PARTICIPANT VM_________________________________

@app.route('/participant/vm_1', methods=['POST'])
def vmonp():
    url = "http://127.0.0.1:8697/api/vms/0VR97SS0G2LEFHS6JQLKJ2DUR0SIGCEK/power"
    payload = "on"
    headers = {
        'Accept': 'application/vnd.vmware.vmw.rest-v1+json',
        'Content-Type': 'application/vnd.vmware.vmw.rest-v1+json',
        'Authorization': 'Basic YWRtaW46YW5hczNTKio='
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    flash(f"State: ON")
    return render_template('/participant/vm1.html')


@app.route('/participant/vm_1#off', methods=['POST'])
def vmoffp():
    url = "http://127.0.0.1:8697/api/vms/0VR97SS0G2LEFHS6JQLKJ2DUR0SIGCEK/power"
    payload = "off"
    headers = {
        'Accept': 'application/vnd.vmware.vmw.rest-v1+json',
        'Content-Type': 'application/vnd.vmware.vmw.rest-v1+json',
        'Authorization': 'Basic YWRtaW46YW5hczNTKio='
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    flash(f"State: OFF")
    return render_template('/participant/vm1.html')


@app.route('/participant/vm_1#state', methods=['POST'])
def vmstatep():
    url = "http://127.0.0.1:8697/api/vms/0VR97SS0G2LEFHS6JQLKJ2DUR0SIGCEK/power"
    payload = {}
    files = {}
    headers = {
        'Authorization': 'Basic YWRtaW46YW5hczNTKio='
    }
    response = requests.request(
        "GET", url, headers=headers, data=payload, files=files)
    msg = response.text[20:30]
    flash(msg)
    return render_template('/participant/vm1.html')


@app.route('/run', methods=['POST'])
def run_command():
    form = flask.request.form
    host = form['host']
    username = form['username']
    password = form['password']
    command = form['command']
    uid = uuid.uuid4().hex
    th = threading.Thread(
        target=flask.copy_current_request_context(do_run_command),
        args=(host, username, password, command, uid))
    th.start()
    return {'uid': uid}


def do_run_command(host, username, password, command, key):
    client = paramiko.SSHClient()
    hostname, port = host.split(':')
    client.load_system_host_keys()
    try:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port, username, password)
        stdin, stdout, stderr = client.exec_command(command)
        channel = stdout.channel
        pending = err_pending = None
        while not channel.closed or channel.recv_ready() or channel.recv_stderr_ready():
            readq, _, _ = select.select([channel], [], [], 1)
            for c in readq:
                if c.recv_ready():
                    chunk = c.recv(len(c.in_buffer))
                    if pending is not None:
                        chunk = pending + chunk
                    lines = chunk.splitlines()
                    if lines and lines[-1] and lines[-1][-1] == chunk[-1]:
                        pending = lines.pop()
                    else:
                        pending = None
                    [push_log(line.decode(), key) for line in lines]
                if c.recv_stderr_ready():
                    chunk = c.recv_stderr(len(c.in_stderr_buffer))
                    if err_pending is not None:
                        chunk = err_pending + chunk
                    lines = chunk.splitlines()
                    if lines and lines[-1] and lines[-1][-1] == chunk[-1]:
                        err_pending = lines.pop()
                    else:
                        err_pending = None
                    [push_log(line.decode(), key) for line in lines]
    finally:
        client.close()


def push_log(message, channel):
    sse.publish({'message': message}, 'message', channel=channel)
