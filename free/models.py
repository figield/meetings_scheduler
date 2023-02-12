from django.db import models


class Employee(models.Model):
    name = models.CharField(max_length=255)
    external_id = models.CharField(max_length=50, blank=True, null=True, default=None)  # 39

    def __str__(self):
        return f"{self.name} - {self.external_id}"


class Meeting(models.Model):
    """
    It is tempting to use `many-to-many` relation between employee and meeting,
    but this is all about searching for free time, not common meetings.
    The `many-to-many` also slow down data loading process.

    employee = models.ManyToManyField(Employee, related_name="meetings")

    """
    employee = models.ForeignKey(Employee, related_name="meetings", on_delete=models.CASCADE)
    start = models.DateTimeField(null=True, blank=True, default=None)
    end = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.employee.name}: {self.start} - {self.end}"

    def get_time_frame(self):
        return f"{self.start} - {self.end}"
