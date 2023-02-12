from django.contrib import admin
from django.urls import path

from free.views import EmployeeListView, FreeTimeView, MeetingListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('employees/', EmployeeListView.as_view()),
    path('meetings/', MeetingListView.as_view()),
    path('api/free/', FreeTimeView.as_view())
]
