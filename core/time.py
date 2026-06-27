from datetime import datetime


DEFAULT_TIME_FORMAT = "%d.%m.%Y %H:%M:%S"


def now():
    return datetime.now()


def now_string():
    return now().strftime(DEFAULT_TIME_FORMAT)
