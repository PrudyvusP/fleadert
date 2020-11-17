from datetime import datetime
from app.main import bp2


@bp2.app_template_filter('timedelta')
def count_delta(deadline):
    time_to_deadline = '---'
    if isinstance(deadline, datetime):
        time_to_deadline = (deadline - datetime.utcnow()).days
        if time_to_deadline < 0:
            time_to_deadline = 0
    return time_to_deadline
