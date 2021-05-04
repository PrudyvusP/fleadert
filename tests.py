import random
from app import create_app, db
from faker import Faker
from app.models import User, Project, Task

app = create_app()
fake = Faker(['ru-RU'])
Faker.seed(0)


def fill_base():
    with app.app_context():
        for _ in range(9):
            fake_guy = fake.simple_profile()
            new_user = User(username=fake_guy['username'],
                            name=fake_guy['name'],
                            email=fake_guy['mail'],
                            is_boss=fake.pybool())
            new_user.set_password(fake.pystr(min_chars=5, max_chars=12))
            db.session.add(new_user)
        boss = User(username='boss', name='Превосходный', email='boss@hugo.boss', is_boss=True)
        worker = User(username='test_worker', name='Эрих-Мария', email='remark@me.io')
        boss.set_password('123')
        worker.set_password('123')
        db.session.add(boss)
        db.session.add(worker)
        for _ in range(6):
            new_project = Project(name=fake.word().title(),
                                  description=fake.sentence(nb_words=10),
                                  author=random.choice([i for i, in db.session.query(User.username).filter(
                                      User.is_boss.is_(True)).all()]))
            db.session.add(new_project)

        for _ in range(100):
            new_task = Task(name=fake.sentence(nb_words=2), description=fake.sentence(nb_words=5),
                            deadline=fake.date_time_this_year(before_now=False, after_now=True),
                            status='в работе',
                            priority=random.choice(['низкий', 'средний', 'высокий']),
                            author=random.choice(db.session.query(User).filter(User.is_boss.is_(True)).all()),
                            project=random.choice(db.session.query(Project).all()),
                            users=random.sample(db.session.query(User).filter(User.is_boss.is_(False)).all(),
                                                random.randint(1, 3)))
            db.session.add(new_task)
        db.session.commit()


if __name__ == '__main__':
    fill_base()
