from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/users_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    users = db.relationship('User', backref='role', lazy=True)


class Participate(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    training_id = db.Column(db.Integer, db.ForeignKey('training.id'), nullable=False)


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
    """
class Controller(ModelView):
    def is_accessible(self):
        if current_user.admin == True:
            return current_user.is_authenticated
        else:
            return abort(401, description="The server can't process the request due the unauthorized user")

    def not_auth(self):
        return "you are not authorized to use the admin dashboard
        
        
        @app.route('/admin/add_participant_training_session<training>', methods=['GET', 'POST'])
def add_participant_training_session(training):
    if current_user.role_id == 1:
        participants = User.query.filter(User.role_id == 3, User.is_banned == False).all()
        return render_template('/admin/participate.html', data=participants, training=training, title="Participant List")
    else:
        return abort(400)
        """

    # @app.route('/trainer/participant')
# def display():

#    all_data = Training.query.with_entities(
#        Training.id).filter_by(trainer_id=current_user.id).all()
#    data = [item[0] for item in all_data]

#    all_data = Participant.query.filter(
#        Participant.training_id.in_(data)).all()
#    return render_template('participants/list.html', data=all_data, title='Participants List')
