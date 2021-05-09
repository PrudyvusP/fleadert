import random
from datetime import timedelta, datetime, date
from app import create_app, db
from faker import Faker
from app.models import User, Project, Task, Request

app = create_app()
fake = Faker(['ru-RU'])
Faker.seed(0)

fake_projects = [{'name': 'Кадровые вопросы', 'description': 'Вопросы рекрутинга и хантинга специалистов, мотивации и '
                                                             'стимулирования штатных работников'},
                 {'name': 'Отчетность', 'description': 'Отчет об отчете на отчет о справке по отчету (справки)'},
                 {'name': 'ОКР Единорог', 'description': 'Создание опытного образца робота-депутата DE PUT AT 2021'},
                 {'name': 'Разработка НПА', 'description': 'Разработка и сопровождение нормативной базы по '
                                                           'использованию IT-техологий для управления государством'},
                 {'name': 'Цифровой регион', 'description': 'Всё, что касается безопасности умных ламп и кофеварок'},
                 {'name': 'Освоение компетенций', 'description': 'Вопросы организации стажировок и самостоятельного '
                                                                 'повышения квалификации работников'}]


def fill_base():
    with app.app_context():
        for _ in range(10):
            fake_guy = fake.simple_profile()
            new_user = User(username=fake_guy['username'],
                            name=fake_guy['name'],
                            email=fake_guy['mail'],
                            is_boss=fake.pybool(),
                            avatar=random.choice([str(i) + '.jpg' for i in range(1, 13)]))
            new_user.set_password(fake.pystr(min_chars=5, max_chars=12))
            db.session.add(new_user)
        boss = User(username='boss', name='Превосходный', email='boss@hugo.boss', is_boss=True)
        worker = User(username='test_worker', name='Эрих-Мария', email='remark@me.io')
        boss.set_password('123')
        worker.set_password('123')
        db.session.add(boss)
        db.session.add(worker)
        new_projects = [Project(name=i['name'], description=i['description'],
                                author=random.choice([i for i, in db.session.query(User.username)
                                                     .filter(User.is_boss.is_(True)).all()])) for i in fake_projects]
        db.session.add_all(new_projects)
        for _ in range(25):
            new_task = Task(name=fake.sentence(nb_words=2).replace('.', ''), description=fake.sentence(nb_words=5),
                            deadline=fake.date_time_this_year(before_now=False, after_now=True),
                            created_on=fake.date_time_this_year(before_now=True, after_now=False),
                            status='в работе',
                            priority=random.choice(['низкий', 'средний', 'высокий']),
                            author=random.choice(db.session.query(User).filter(User.is_boss.is_(True)).all()),
                            project=random.choice(db.session.query(Project).all()),
                            users=random.sample(db.session.query(User).filter(User.is_boss.is_(False)).all(),
                                                random.randint(1, 3)))
            db.session.add(new_task)
        for _ in range(20):
            boss_task = Task(name=fake.sentence(nb_words=2).replace('.', ''), description=fake.sentence(nb_words=5),
                             deadline=fake.date_time_this_year(before_now=False, after_now=True),
                             created_on=fake.date_time_this_year(before_now=True, after_now=False),
                             status='на рассмотрении',
                             priority=random.choice(['низкий', 'средний', 'высокий']),
                             author=random.choice(db.session.query(User).filter(User.is_boss.is_(True)).all()),
                             project=random.choice(db.session.query(Project).all()),
                             users=random.sample(db.session.query(User).filter(User.is_boss.is_(False)).all(),
                                                 random.randint(1, 3)))
            db.session.add(boss_task)
            new_request = Request(executed_comment=fake.sentence(nb_words=4),
                                  executed_number=random.choice(['', str(random.randint(1, 6))]),
                                  date_of_execution=fake.date_between(boss_task.created_on.date(), date.today()),
                                  task=boss_task, user=random.choice(boss_task.users))
            db.session.add(new_request)

        for _ in range(77):
            executed_task = Task(name=fake.sentence(nb_words=2).replace('.', ''), description=fake.sentence(nb_words=5),
                                 created_on=fake.date_time_this_year(before_now=True, after_now=False),
                                 deadline=fake.date_time_this_year(before_now=False, after_now=True),
                                 status='выполнена', priority=random.choice(['низкий', 'средний', 'высокий']),
                                 author=random.choice(db.session.query(User).filter(User.is_boss.is_(True)).all()),
                                 project=random.choice(db.session.query(Project).all()),
                                 users=random.sample(db.session.query(User).filter(User.is_boss.is_(False)).all(),
                                                     random.randint(1, 3)))
            db.session.add(executed_task)
            executed_tasks_request = Request(executed_comment=fake.sentence(nb_words=4),
                                             executed_number=random.choice(['', str(random.randint(1, 666)),
                                                                            '21/7-' + str(random.randint(1, 100))]),
                                             executed_on=fake.date_time_between_dates(executed_task.created_on,
                                                                                      datetime.today()),
                                             boss_comment=fake.sentence(nb_words=2), is_considered=True,
                                             task=executed_task, user=random.choice(executed_task.users),
                                             )
            db.session.add(executed_tasks_request)
            executed_tasks_request.date_of_execution = executed_tasks_request.executed_on.date()
            executed_tasks_request.considered_on = fake.date_time_between(executed_tasks_request.executed_on,
                                                                          executed_tasks_request.executed_on + timedelta(
                                                                              days=5))
            executed_task.executor = executed_tasks_request.user
            executed_task.requests = [executed_tasks_request]
            executed_task.completed_on = executed_tasks_request.considered_on
            executed_task.executed_number = executed_tasks_request.executed_number
            executed_task.executed_date = executed_tasks_request.date_of_execution
            executed_task.closer = random.choice(db.session.query(User).filter(User.is_boss.is_(True)).all())
        db.session.commit()


if __name__ == '__main__':
    fill_base()
