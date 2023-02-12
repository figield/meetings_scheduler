from datetime import datetime, timedelta

from rest_framework import serializers

from free.models import Employee, Meeting
from free.utils import parser
from freebusy.settings import DATETIME_FORMAT_RESPONSE


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("external_id", "name")


class MeetingSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()

    class Meta:
        model = Meeting
        fields = ("employee", "start", "end")


class ResponseFreeTimeSerializer(serializers.Serializer):
    freetimes = serializers.ListField(child=serializers.DateTimeField(format=DATETIME_FORMAT_RESPONSE))


class FreeTimes:

    def __init__(self, freetimes):
        self.freetimes = freetimes


class RequestFreeTimeSerializer:

    def __init__(self, data, shortest_time_slot=30):
        self.data = data
        self.shortest_time_slot = shortest_time_slot
        self.meeting_length = None
        self.earliest_start = None
        self.latest_start = None
        self.start_office_hour = None
        self.end_office_hour = None
        self.external_ids = None

    def is_valid(self):
        try:
            self.meeting_length = int(self.data.get('duration'))
            self.earliest_start = parser.get_datetime(self.data.get('earliest_start'))
            self.latest_start = parser.get_datetime(self.data.get('latest_start'))
            self.start_office_hour, self.end_office_hour = parser.get_start_end_hours(self.data.get('office_hours'))
            self.external_ids = self.data.get('employee_ids').split(",")
        except:
            return False
        return True

    def get_freetimes(self):
        employees_meetings = self._employees_meetings()

        free_times_slots = set()
        possible_start_times = self._possible_start_times()
        for possible_time_slot in possible_start_times:
            possible_start = possible_time_slot
            possible_end = possible_start + timedelta(minutes=self.meeting_length)
            valid = True
            for meeting in employees_meetings:
                meeting_start = meeting.start
                meeting_end = meeting.end
                if meeting_start <= possible_start < meeting_end:
                    """
                    Possible free time slot is placed in meeting
                     ---XxYyxx--- or ---XxYy--- or ---XxYyPp---
                     y = p & x
                    """
                    valid = False
                    break
                if possible_start <= meeting_start < possible_end:
                    """
                    Possible free time slot starts before and ends during the meeting.
                     ---PpYyx--- or ---Ppp---
                     y = p & x
                    """
                    valid = False
                    break

            if valid:
                free_times_slots.add(possible_time_slot)

        free_times_list = sorted(list(free_times_slots))
        return FreeTimes(free_times_list)

    def _employees_meetings(self):
        """
        'x' = meeting 30 min (`X` - meeting start)
        '-' = free time 30 min

            8   earliest latest  17
         Xxx|Xx--Xx|x--Xx-X|x-Xx-|--Xx (overtime)

        In the example above, three meeting should be taken into a consideration
        between earliest_start and latest_start time frames.
        Meetings can be spread over several days.
        Meetings are orederd by start time.
        """

        return Meeting.objects.filter(employee__external_id__in=self.external_ids,
                                      start__lt=self.latest_start,
                                      end__gt=self.earliest_start).order_by('start')

    def _possible_start_times(self):
        """
        Get possible start times between earliest and latest start time and duration.
        Also considering the working hours.
        """
        meeting_slots_set = set()
        duration = timedelta(minutes=self.meeting_length)
        meeting_step_unit = timedelta(minutes=self.shortest_time_slot)
        meeting_slot_start = self.earliest_start
        meeting_slot_end = meeting_slot_start + duration
        while self.latest_start >= meeting_slot_start:
            if self.start_office_hour <= meeting_slot_start.hour < self.end_office_hour \
                    and meeting_slot_end <= datetime(meeting_slot_start.year,
                                                     meeting_slot_start.month,
                                                     meeting_slot_start.day,
                                                     self.end_office_hour, 0):  # office_end_minutes (was not required)
                meeting_slots_set.add(meeting_slot_start)
            meeting_slot_start = meeting_slot_start + meeting_step_unit
            meeting_slot_end = meeting_slot_start + duration

        return sorted(list(meeting_slots_set))
