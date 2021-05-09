from datetime import datetime
from app.main import bp2


@bp2.app_template_filter('timedelta')
def count_deadline(deadline):
    if isinstance(deadline, datetime) and deadline > datetime.utcnow():
        time_to_deadline = deadline - datetime.utcnow()
        days_to_deadline, seconds_to_deadline = time_to_deadline.days, time_to_deadline.seconds
        hours = seconds_to_deadline // 3600
        minutes = (seconds_to_deadline % 3600) // 60
        return f'{days_to_deadline} д. {hours} ч.' if days_to_deadline > 0 else f'{hours} ч. {minutes} мин.'
    else:
        return "срок истёк"


@bp2.app_template_filter('daytodl')
def deadline_days_for_tr_color(deadline):
    return (deadline - datetime.utcnow()).days if isinstance(deadline, datetime) else "Error"

