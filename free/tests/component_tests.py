import datetime

import pytest

from free.models import Employee, Meeting
from free.serializers import RequestFreeTimeSerializer
from free.tests import utils
from free.tests.utils import create_meeting_frames


@pytest.mark.django_db
def test_employees_meetings_between_earliest_and_latest(set_up):
    """
    Test meeting selection for the given time period.
    One employee item is good enough to validate the function.

    'x' = meeting 30 min (`X` - meeting start)
    -' = free time 30 min

    earliest = 11:00
    latest = 14:30

       earliest  latest
    8|Xx--Xx|x--Xx-X|x-Xx-|17

    """
    employee = Employee.objects.first()
    year, month, day = 2023, 2, 13

    start, end = create_meeting_frames(year, month, day, 8, 0, 9, 0)
    Meeting.objects.create(employee=employee, start=start, end=end)

    start, end = create_meeting_frames(year, month, day, 10, 0, 11, 30)
    Meeting.objects.create(employee=employee, start=start, end=end)

    start, end = create_meeting_frames(year, month, day, 12, 30, 13, 30)
    Meeting.objects.create(employee=employee, start=start, end=end)

    start, end = create_meeting_frames(year, month, day, 14, 0, 15, 0)
    Meeting.objects.create(employee=employee, start=start, end=end)

    start, end = create_meeting_frames(year, month, day, 15, 30, 16, 30)
    Meeting.objects.create(employee=employee, start=start, end=end)

    assert 5 == Meeting.objects.all().count()

    params = utils.request_free_time_data([employee],
                                          datetime.datetime(year, month, day, 11, 0),
                                          datetime.datetime(year, month, day, 14, 30))

    free_times_query = RequestFreeTimeSerializer(data=params)
    free_times_query.is_valid()
    meetings = free_times_query._employees_meetings()
    meetings_time_frames = [meeting.get_time_frame() for meeting in meetings]
    # only for internal representation
    assert meetings_time_frames == ['2023-02-13 10:00:00 - 2023-02-13 11:30:00',
                                    '2023-02-13 12:30:00 - 2023-02-13 13:30:00',
                                    '2023-02-13 14:00:00 - 2023-02-13 15:00:00']


def test_possible_start_times_for_whole_day():
    year, month, day = 2023, 2, 13
    params = utils.request_free_time_data(
        [],
        datetime.datetime(year, month, day, 7, 0),
        datetime.datetime(year, month, day, 18, 0),
        duration=120
    )

    free_times_query = RequestFreeTimeSerializer(data=params)
    free_times_query.is_valid()
    time_slots = free_times_query._possible_start_times()

    assert time_slots == [datetime.datetime(year, month, day, 8, 0),
                          datetime.datetime(year, month, day, 8, 30),
                          datetime.datetime(year, month, day, 9, 0),
                          datetime.datetime(year, month, day, 9, 30),
                          datetime.datetime(year, month, day, 10, 0),
                          datetime.datetime(year, month, day, 10, 30),
                          datetime.datetime(year, month, day, 11, 0),
                          datetime.datetime(year, month, day, 11, 30),
                          datetime.datetime(year, month, day, 12, 0),
                          datetime.datetime(year, month, day, 12, 30),
                          datetime.datetime(year, month, day, 13, 0),
                          datetime.datetime(year, month, day, 13, 30),
                          datetime.datetime(year, month, day, 14, 0),
                          datetime.datetime(year, month, day, 14, 30),
                          datetime.datetime(year, month, day, 15, 0)]


@pytest.mark.parametrize('year, month, day', [(2023, 2, 13), (2023, 12, 31), (2023, 2, 28)])
def test_possible_start_times_for_two_days(year, month, day):
    params = utils.request_free_time_data(
        [],
        datetime.datetime(year, month, day, 12, 0),
        datetime.datetime(year, month, day, 10, 0) + datetime.timedelta(days=1),
        duration=120
    )

    free_times_query = RequestFreeTimeSerializer(data=params)
    free_times_query.is_valid()

    time_slots = free_times_query._possible_start_times()

    assert time_slots == [datetime.datetime(year, month, day, 12, 0),
                          datetime.datetime(year, month, day, 12, 30),
                          datetime.datetime(year, month, day, 13, 0),
                          datetime.datetime(year, month, day, 13, 30),
                          datetime.datetime(year, month, day, 14, 0),
                          datetime.datetime(year, month, day, 14, 30),
                          datetime.datetime(year, month, day, 15, 0),
                          datetime.datetime(year, month, day, 8, 0) + datetime.timedelta(days=1),
                          datetime.datetime(year, month, day, 8, 30) + datetime.timedelta(days=1),
                          datetime.datetime(year, month, day, 9, 0) + datetime.timedelta(days=1),
                          datetime.datetime(year, month, day, 9, 30) + datetime.timedelta(days=1),
                          datetime.datetime(year, month, day, 10, 0) + datetime.timedelta(days=1)]


@pytest.mark.parametrize('year, month, day', [(2023, 2, 13), (2023, 12, 31), (2023, 2, 28)])
def test_possible_start_times_between_two_days_at_night(year, month, day):
    year, month, day = 2023, 2, 13
    params = utils.request_free_time_data(
        [],
        earliest=datetime.datetime(year, month, day, 17, 0),
        latest=datetime.datetime(year, month, day, 7, 0) + datetime.timedelta(days=1),
        duration=120
    )

    free_times_query = RequestFreeTimeSerializer(data=params)
    free_times_query.is_valid()

    time_slots = free_times_query._possible_start_times()

    assert time_slots == []


@pytest.mark.parametrize('year, month, day', [(2023, 2, 13), (2023, 12, 31), (2023, 2, 28)])
def test_possible_start_times_between_two_days_with_very_long_duration(year, month, day):
    year, month, day = 2023, 2, 13
    params = utils.request_free_time_data(
        [],
        earliest=datetime.datetime(year, month, day, 8, 0),
        latest=datetime.datetime(year, month, day, 17, 0) + datetime.timedelta(days=1),
        duration=60 * 20
    )

    free_times_query = RequestFreeTimeSerializer(data=params)
    free_times_query.is_valid()

    time_slots = free_times_query._possible_start_times()

    assert time_slots == []


def test_whole_working_day_time_slot_and_one_possible_start():
    year, month, day = 2023, 2, 13
    working_day = 60 * 8
    params = utils.request_free_time_data(
        [],
        earliest=datetime.datetime(year, month, day, 8, 0),
        latest=datetime.datetime(year, month, day, 8, 0),
        duration=working_day
    )

    free_times_query = RequestFreeTimeSerializer(data=params)
    free_times_query.is_valid()

    time_slots = free_times_query._possible_start_times()

    assert time_slots == [datetime.datetime(2023, 2, 13, 8, 0)]


def test_whole_working_day_time_slot():
    year, month, day = 2023, 2, 13
    working_day = 60 * 8
    params = utils.request_free_time_data(
        [],
        earliest=datetime.datetime(year, month, day, 8, 0),
        latest=datetime.datetime(year, month, day, 17, 0),
        duration=working_day
    )

    free_times_query = RequestFreeTimeSerializer(data=params)
    free_times_query.is_valid()

    time_slots = free_times_query._possible_start_times()

    assert time_slots == [datetime.datetime(2023, 2, 13, 8, 0),
                          datetime.datetime(2023, 2, 13, 8, 30),
                          datetime.datetime(2023, 2, 13, 9, 0)]
