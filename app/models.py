from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


user_task_association = db.Table('user_task',
                                 db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                                 db.Column('task_id', db.Integer, db.ForeignKey('tasks.id')),
                                 )

user_project_association = db.Table('user_project',
                                    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                                    db.Column('project_id', db.Integer, db.ForeignKey('projects.id')),
                                    )


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(130), nullable=False)
    created_on = db.Column(db.DateTime(50), default=datetime.utcnow())
    is_boss = db.Column(db.Boolean(), default=False)
    rating = db.Column(db.Float(50), default=0.0)
    phone = db.Column(db.String(12))
    avatar = db.Column(db.String(50), nullable=True, default='default.png')
    last_seen = db.Column(db.DateTime(50), default=datetime.utcnow())


    tasks = db.relationship('Task', secondary=user_task_association, back_populates='users')


    requests = db.relationship('Request', back_populates='user')
    projects = db.relationship('Project', secondary=user_project_association, back_populates='users')
    executed_tasks = db.relationship('Task', back_populates='executor')

    def __repr__(self):
        return '<{}:{}>'.format(self.id, self.username)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow(), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    is_relevant = db.Column(db.Boolean(), nullable=False, default=True)
    completed_at = db.Column(db.DateTime(), nullable=True)
    tasks = db.relationship('Task', back_populates='project')
    users = db.relationship('User', secondary=user_project_association, back_populates='projects')

    def __repr__(self):
        return '<{}:{}>'.format(self.id, self.name)


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow())
    deadline = db.Column(db.DateTime(), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='в работе', nullable=False)
    priority = db.Column(db.String(12), nullable=False)
    completed_on = db.Column(db.DateTime(), nullable=True)
    executed_number = db.Column(db.String(30), nullable=True)
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    executor = db.relationship('User', back_populates='executed_tasks')

    users = db.relationship('User', secondary=user_task_association, back_populates='tasks')


    requests = db.relationship('Request', back_populates='task')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    project = db.relationship('Project', back_populates='tasks')

    def __repr__(self):
        return '<{}:{}>'.format(self.id, self.name)


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    executed_comment = db.Column(db.String(300), nullable=False)
    executed_on = db.Column(db.DateTime(50), default=datetime.utcnow())
    executed_number = db.Column(db.String(30))
    boss_comment = db.Column(db.String(300))
    is_considered = db.Column(db.Boolean(), default=False)
    considered_on = db.Column(db.DateTime(50))
    denied_on = db.Column(db.DateTime(20), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='requests')
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    task = db.relationship('Task', back_populates='requests')

    def __repr__(self):
        return 'Заявка № {} пользователя {}'.format(self.id, self.user)
