from app import create_app
from app.models import db, User, Task, Project, Request

app = create_app()


#@app.shell_context_processor
#def make_shell_context():
#    return {'db': db, 'User': User, 'Task': Task, 'Project': 'Project'}


#if __name__ == '__main__':
    #app = create_app()
    #app.run()
