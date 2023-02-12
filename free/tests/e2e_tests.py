import datetime

import pytest
from rest_framework import status

from free.models import Employee, Meeting
from free.tests.utils import create_meeting_frames, http_call, request_free_time_data
from free.utils.parser import get_datetime_text as ft


@pytest.mark.parametrize('http_method', ['GET', 'POST'])
@pytest.mark.django_db
def test_no_free_time(client, set_up, http_method):
    """
     Employee has whole day of meetings.
     There is no free time slot.

       8|Xxxxxxxxxxxxxxxx|17

    """
    employees = Employee.objects.all()
    employee1 = employees.first()
    employee2 = employees.last()
    year, month, day = 2023, 2, 11
    start_m1, end_m1 = create_meeting_frames(year, month, day, 8, 0, 17, 30)
    start_m2, end_m2 = create_meeting_frames(year, month, day, 8, 0, 17, 30)
    Meeting.objects.create(employee=employee1, start=start_m1, end=end_m1)
    Meeting.objects.create(employee=employee2, start=start_m2, end=end_m2)
    assert 2 == Meeting.objects.all().count()

    request_data = request_free_time_data([employee1, employee2],
                                          datetime.datetime(year, month, day, 11, 0),
                                          datetime.datetime(year, month, day, 15, 30),
                                          duration=90)
    response = http_call(client, http_method, request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['freetimes'] == []


@pytest.mark.parametrize('http_method', ['GET', 'POST'])
@pytest.mark.django_db
def test_one_free_time_slot_lunch_brake(client, set_up, http_method):
    """
     It is the whole day of meetings.
     There is one free time slot - lunch time. 60 minutes.

       8|Xxxxxxxx--Xxxxxxxx|17

    """
    employee = Employee.objects.all().first()
    year, month, day = 2023, 2, 12
    start_m1, end_m1 = create_meeting_frames(year, month, day, 8, 0, 12, 00)
    start_m2, end_m2 = create_meeting_frames(year, month, day, 13, 0, 17, 00)
    Meeting.objects.create(employee=employee, start=start_m1, end=end_m1)
    Meeting.objects.create(employee=employee, start=start_m2, end=end_m2)
    assert 2 == Meeting.objects.all().count()

    request_data = request_free_time_data([employee],
                                          datetime.datetime(year, month, day, 8, 0),
                                          datetime.datetime(year, month, day, 16, 0))
    response = http_call(client, http_method, request_data)
    assert response.status_code == status.HTTP_200_OK
    # The time format (ft) depends from the configuration: '02/12/2023 12:00:00 PM' or '2/12/2023 12:00:00 PM'
    assert response.data['freetimes'] == [ft(datetime.datetime(year, month, day, 12, 0))]


@pytest.mark.parametrize('http_method', ['GET', 'POST'])
@pytest.mark.django_db
def test_tree_free_time_slots(client, set_up, http_method):
    """
     There are 2 separate meetings of 2 employees.
     Requested meeting duration is 60 minutes.
     Free slots are having 60 minutes.

       8|--Xxxxxx--Xxxxxx--|17

    """
    employees = Employee.objects.all()
    employee1 = employees.first()
    employee2 = employees.last()
    year, month, day = 2023, 2, 12
    start_m1, end_m1 = create_meeting_frames(year, month, day, 9, 0, 12, 00)
    start_m2, end_m2 = create_meeting_frames(year, month, day, 13, 0, 16, 00)
    Meeting.objects.create(employee=employee1, start=start_m1, end=end_m1)
    Meeting.objects.create(employee=employee2, start=start_m2, end=end_m2)
    assert 2 == Meeting.objects.all().count()

    request_data = request_free_time_data([employee1, employee2],
                                          datetime.datetime(year, month, day, 8, 0),
                                          datetime.datetime(year, month, day, 16, 0))
    response = http_call(client, http_method, request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['freetimes'] == [ft(datetime.datetime(year, month, day, 8, 0)),
                                          ft(datetime.datetime(year, month, day, 12, 0)),
                                          ft(datetime.datetime(year, month, day, 16, 0))]


@pytest.mark.parametrize('http_method', ['GET', 'POST'])
@pytest.mark.django_db
def test_tree_free_time_slots_with_short_duration(client, set_up, http_method):
    """
     There are 2 separate meetings of 2 employees.
     Free slots are having 60 minutes.
     Requested meeting duration is 30 minutes.

       8|--Xxxxxx--Xxxxxx--|17

    """
    employees = Employee.objects.all()
    employee1 = employees.first()
    employee2 = employees.last()
    year, month, day = 2023, 2, 12
    start_m1, end_m1 = create_meeting_frames(year, month, day, 9, 0, 12, 00)
    start_m2, end_m2 = create_meeting_frames(year, month, day, 13, 0, 16, 00)
    Meeting.objects.create(employee=employee1, start=start_m1, end=end_m1)
    Meeting.objects.create(employee=employee2, start=start_m2, end=end_m2)
    assert 2 == Meeting.objects.all().count()

    request_data = request_free_time_data([employee1, employee2],
                                          datetime.datetime(year, month, day, 8, 0),
                                          datetime.datetime(year, month, day, 16, 30),
                                          duration=30)
    response = http_call(client, http_method, request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['freetimes'] == [ft(datetime.datetime(year, month, day, 8, 0)),
                                          ft(datetime.datetime(year, month, day, 8, 30)),
                                          ft(datetime.datetime(year, month, day, 12, 0)),
                                          ft(datetime.datetime(year, month, day, 12, 30)),
                                          ft(datetime.datetime(year, month, day, 16, 0)),
                                          ft(datetime.datetime(year, month, day, 16, 30))]


@pytest.mark.parametrize('http_method', ['GET', 'POST'])
@pytest.mark.django_db
def test_tree_free_time_slots_for_two_days(client, set_up, http_method):
    """
     There are 2 separate meetings of 2 employees during 2 days.
     Free slots are having 60 minutes.
     Requested meeting duration is 60 minutes.
     Earliest start meeting 13:00 first day.
     Latest start meeting 10:30 next day.

                    earliest           latest
       8|------------Xx|xx--|17   8|--Xxx|xxx----------|17

    """
    employees = Employee.objects.all()
    employee1 = employees.first()
    employee2 = employees.last()
    year, month, day = 2023, 2, 12
    start_m1, end_m1 = create_meeting_frames(year, month, day, 13, 0, 16, 0)
    start_m2, end_m2 = create_meeting_frames(year, month, day + 1, 9, 0, 12, 0)
    Meeting.objects.create(employee=employee1, start=start_m1, end=end_m1)
    Meeting.objects.create(employee=employee2, start=start_m2, end=end_m2)
    assert 2 == Meeting.objects.all().count()

    request_data = request_free_time_data([employee1, employee2],
                                          datetime.datetime(year, month, day, 13, 0),
                                          datetime.datetime(year, month, day + 1, 10, 30),
                                          duration=60)
    response = http_call(client, http_method, request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['freetimes'] == [ft(datetime.datetime(year, month, day, 16, 0)),
                                          ft(datetime.datetime(year, month, day + 1, 8, 0))]


@pytest.mark.parametrize('http_method', ['GET, POST'])
@pytest.mark.django_db
def test_404_error(client, set_up, http_method):
    """
     Wrong request parameter value.
    """
    employee = Employee.objects.all().first()
    year, month, day = 2023, 2, 11
    start_m1, end_m1 = create_meeting_frames(year, month, day, 8, 0, 17, 30)
    start_m2, end_m2 = create_meeting_frames(year, month, day, 8, 0, 17, 30)
    Meeting.objects.create(employee=employee, start=start_m1, end=end_m1)
    Meeting.objects.create(employee=employee, start=start_m2, end=end_m2)
    assert 2 == Meeting.objects.all().count()

    request_data = request_free_time_data([employee],
                                          datetime.datetime(year, month, day, 11, 0),
                                          datetime.datetime(year, month, day, 15, 30),
                                          duration=90)
    request_data['office_hours'] = "817"
    response = http_call(client, http_method, request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

