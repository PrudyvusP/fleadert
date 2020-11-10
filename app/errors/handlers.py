from flask import render_template
from app import db
from app.errors import bp


@bp.errorhandler(404)
def err_404(error):
    return render_template('errors/404.html'), 404


@bp.errorhandler(413)
def err_413(error):
    return "Файл превышает допустимое число памями (1 мегабайт)"


@bp.errorhandler(500)
def err_500(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
