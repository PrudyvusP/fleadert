from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login


@login.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


def calculate_boss_rank(count):
    if count <= 10:
        strq = 'ученик начальника'
    elif 10 < count <= 50:
        strq = 'наставник ★'
    elif 50 < count <= 100:
        strq = 'менеджер ★★'
    elif 100 < count <= 250:
        strq = 'управленец ★★★'
    else:
        strq = 'гуру ♠'
    return strq


def calculate_user_rank(count):
    if count <= 10:
        strq = 'проходимец'
    elif 10 < count <= 50:
        strq = 'зеленый ★'
    elif 50 < count <= 100:
        strq = 'новичок ★★'
    elif 100 < count <= 250:
        strq = 'cпециалист ★★★'
    else:
        strq = 'эксперт ♠'
    return strq


user_task_association = db.Table('user_task',
                                 db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete="CASCADE")),
                                 db.Column('task_id', db.Integer, db.ForeignKey('tasks.id', ondelete="CASCADE")),
                                 )


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    username = db.Column(db.String(60), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(130), nullable=False)
    created_on = db.Column(db.DateTime(50), default=datetime.utcnow())
    is_boss = db.Column(db.Boolean(), default=False)
    phone = db.Column(db.String(12))
    avatar = db.Column(db.String(50), nullable=True, default='5.jpg')
    last_seen = db.Column(db.DateTime(50), default=datetime.utcnow())
    tasks = db.relationship('Task', secondary=user_task_association, back_populates='users', cascade="all, delete")
    requests = db.relationship('Request', back_populates='user')
    non_executed_tasks = db.relationship('Task', secondary="user_task",
                                         primaryjoin="User.id==user_task.c.user_id",
                                         secondaryjoin="and_(Task.id==user_task.c.task_id, "
                                                       "Task.status=='в работе')",
                                         order_by="Task.deadline")

    def get_tasks_on_consider(self):
        return db.session.query(Task).filter(Task.status == 'на рассмотрении').order_by(
            Task.deadline).all() if self.is_boss else None

    def count_statistics(self):
        if self.is_boss:
            return len(self.closership)
        else:
            return len(self.executionship)

    def get_rank(self):
        if self.is_boss:
            return calculate_boss_rank(self.count_statistics())
        else:
            return calculate_user_rank(self.count_statistics())

    def __repr__(self):
        return f'{self.id}#{self.username}'

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

    tasks = db.relationship('Task', order_by='Task.deadline', back_populates='project', cascade='all, delete',
                            passive_deletes=True)
    tasks_at_work = db.relationship('Task', order_by='Task.deadline', primaryjoin="and_(Task.project_id == Project.id, "
                                                                                  "Task.status=='в работе')")
    tasks_on_consider = db.relationship('Task', order_by='Task.deadline',
                                        primaryjoin="and_(Task.project_id == Project.id, "
                                                    "Task.status=='на рассмотрении')")
    tasks_executed = db.relationship('Task', order_by='desc(Task.completed_on)',
                                     primaryjoin="and_(Task.project_id == Project.id, "
                                                 "Task.status=='выполнена')")

    def __repr__(self):
        return f'{self.id}#{self.name} by {self.author}'


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow(), nullable=False)
    deadline = db.Column(db.DateTime(), nullable=False)
    status = db.Column(db.String(20), default='в работе', nullable=False)
    priority = db.Column(db.String(12), nullable=False)
    edited_on = db.Column(db.DateTime(), nullable=True)
    completed_on = db.Column(db.DateTime(), nullable=True)
    executed_number = db.Column(db.String(30), nullable=True)
    executed_date = db.Column(db.DateTime(), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'))
    project = db.relationship('Project', back_populates='tasks')
    requests = db.relationship('Request', back_populates='task', cascade='all, delete', passive_deletes=True)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    closer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    author = db.relationship('User', foreign_keys=[author_id, ], backref='authorship')
    executor = db.relationship('User', foreign_keys=[executor_id, ], backref='executionship')
    closer = db.relationship('User', foreign_keys=[closer_id, ], backref='closership')
    users = db.relationship('User', secondary=user_task_association, back_populates='tasks', cascade="all, delete",
                            passive_deletes=True)

    def __repr__(self):
        return f'#{self.id}#{self.name} till {self.deadline.date()}'


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    executed_comment = db.Column(db.String(300), nullable=False)
    executed_on = db.Column(db.DateTime(50), default=datetime.utcnow(), nullable=False)
    executed_number = db.Column(db.String(30), nullable=True)
    date_of_execution = db.Column(db.DateTime, nullable=True)
    boss_comment = db.Column(db.String(300), nullable=True)
    is_considered = db.Column(db.Boolean(), default=False)
    considered_on = db.Column(db.DateTime(50), nullable=True)
    denied_on = db.Column(db.DateTime(20), nullable=True)

    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'))
    task = db.relationship('Task', back_populates='requests')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    user = db.relationship('User', back_populates='requests')

    def __repr__(self):
        return f'Заявка № {self.id} пользователя {self.user}'
