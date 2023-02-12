import datetime
from random import choice

from free.models import Employee
from free.utils.parser import get_datetime_text

API_URL = "/api/free/"


def create_meeting_frames(year, month, day, hour_from, minutes_from, hour_to, minutes_to):
    start = datetime.datetime(year, month, day, hour_from, minutes_from)
    end = datetime.datetime(year, month, day, hour_to, minutes_to)
    return start, end


def http_call(client, http_method, request_data):
    if http_method == "GET":
        return client.get(API_URL, request_data, format='json')
    else:
        return client.post(API_URL, request_data, format='json')


def request_free_time_data(employees, earliest, latest, duration=60, office_hours='8-17'):
    return {
        'employee_ids': ",".join([employee.external_id for employee in employees]),
        'duration': duration,
        'earliest_start': get_datetime_text(earliest),
        'latest_start': get_datetime_text(latest),
        'office_hours': office_hours
    }


def random_employee():
    """
    Return a random Employee object from db.
    """
    employees = Employee.objects.all()
    return choice(employees)
