from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from free.models import Employee, Meeting
from free.serializers import EmployeeSerializer, ResponseFreeTimeSerializer, MeetingSerializer, RequestFreeTimeSerializer


class FreeTimeView(APIView):

    def get_or_post(self, input_data):
        free_times_query = RequestFreeTimeSerializer(data=input_data)
        if not free_times_query.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        output_data = free_times_query.get_freetimes()
        serializer = ResponseFreeTimeSerializer(output_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        return self.get_or_post(request.query_params)

    def post(self, request, *args, **kwargs):
        return self.get_or_post(request.data)


class EmployeeListView(generics.ListCreateAPIView):
    """
    For testing purposes
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class MeetingListView(generics.ListCreateAPIView):
    """
    For testing purposes
    """
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
