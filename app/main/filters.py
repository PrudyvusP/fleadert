from datetime import datetime
from app.main import bp2


@bp2.app_template_filter('timedelta')
def count_deadline(deadline):
    if isinstance(deadline, datetime) and deadline > datetime.utcnow():
        time_to_deadline = deadline - datetime.utcnow()
        days_to_deadline, seconds_to_deadline = time_to_deadline.days, time_to_deadline.seconds
        hours = seconds_to_deadline // 3600
        minutes = (seconds_to_deadline % 3600) // 60
        if days_to_deadline > 0:
            return '{} д. {} ч.'.format(days_to_deadline, hours)
        else:
            return '{} ч. {} мин.'.format(hours, minutes)
    else:
        return "срок истёк"


@bp2.app_template_filter('daytodl')
def deadline_days_for_tr_color(deadline):
    if isinstance(deadline, datetime):
        time_to_deadline = (deadline - datetime.utcnow()).days
        return time_to_deadline
    else:
        return "Error"

