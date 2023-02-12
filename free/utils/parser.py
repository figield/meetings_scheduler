from datetime import datetime

from freebusy.settings import DATETIME_FORMAT, DATETIME_FORMAT_RESPONSE


def get_datetime(datime_text):
    return datetime.strptime(datime_text, DATETIME_FORMAT)


def get_datetime_text(datime_obj):
    return datetime.strftime(datime_obj, DATETIME_FORMAT_RESPONSE)


def get_start_end_hours(hours_text):
    hours = hours_text.split('-')
    start_hours = int(hours[0])
    end_hours = int(hours[1])
    return start_hours, end_hours
