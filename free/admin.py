from django.contrib import admin

from free.models import Meeting, Employee

admin.site.register(Employee)
admin.site.register(Meeting)