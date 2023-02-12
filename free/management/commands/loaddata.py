# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import OperationalError
from free.models import Employee, Meeting
from freebusy.settings import DATETIME_FORMAT


class Command(BaseCommand):

    def __init__(self):
        self.verbose = True
        self.file_name = None
        self.items_counter = 0
        self.file_lines_counter = 0
        self.file_name = "freebusy.txt"
        self.errors = []
        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help="Download data from the provided path [freebusy.txt]")
        parser.add_argument('--verbose', type=str, default='Yes', help="Show traversed data [Yes]")

    def print_io(self, line, force_print=False):
        if "ERROR" in line:
            self.errors.append(line)
        if self.verbose or force_print:
            self.stdout.write(line)
            self.stdout.flush()

    def print_errors(self):
        for e in self.errors:
            self.stdout.write(e)

    def stream_lines_from_file(func):

        def wrap(self, *args, **kwargs):
            """ Wrapper Function """
            self.file_lines_counter = 0
            self.items_counter = 0
            try:
                with open(self.file_name, 'r') as file:
                    # Get line one by one since file might be big.
                    while True:
                        line = file.readline()
                        self.file_lines_counter += 1
                        # if line is empty end of the file is reached
                        if not line:
                            break

                        func(self, line)

                return self.items_counter
            except Exception as e:
                self.print_io(self.style.WARNING(f"[{func.__name__}] ") + self.style.ERROR(e), force_print=True)

        return wrap

    @stream_lines_from_file
    def handle_employee_data(self, line=""):
        try:
            data = line.strip().split(';')
            if len(data) == 2:
                self.items_counter += 1
                external_id = data[0]
                name = data[1]
                if name is None or len(name) < 1:
                    self.print_io(self.style.ERROR(f'{self.file_lines_counter}:ERROR:employee VALIDATION:') + line)
                else:
                    employee_exists = Employee.objects.filter(external_id=external_id).exists()
                    if employee_exists:
                        # perform update?
                        self.print_io(
                            self.style.WARNING(f'{self.items_counter}:employee EXISTS:') + f"{name} - {external_id}")
                    else:
                        employee = Employee.objects.create(name=name, external_id=external_id)
                        self.print_io(self.style.WARNING(f'{self.items_counter}: ') + f"{employee}")
            elif len(data) == 1:
                self.print_io(self.style.ERROR(f'{self.file_lines_counter}:ERROR:TRASH:') + line)
        except OperationalError as e:
            self.print_io(self.style.WARNING(f"[handle_employee_data] ") + self.style.ERROR(e), force_print=True)
            exit(1)
        except Exception as e:
            self.print_io(self.style.WARNING(f"[handle_employee_data] ") + self.style.ERROR(e), force_print=True)

    @stream_lines_from_file
    def handle_meeting_data(self, line=""):
        try:
            data = line.strip().split(';')
            data_len = len(data)
            if data_len == 4:
                self.items_counter += 1
                external_id = data[0]
                start = datetime.strptime(data[1], DATETIME_FORMAT)
                end = datetime.strptime(data[2], DATETIME_FORMAT)
                if start >= end:
                    self.print_io(self.style.ERROR(f'{self.file_lines_counter}:ERROR:START >= END:') + line)
                else:
                    employees = Employee.objects.filter(external_id=external_id)
                    if employees.exists():
                        employee = employees.first()
                        meeting, created = Meeting.objects.get_or_create(employee=employee, start=start, end=end)
                        if not created:
                            self.print_io(self.style.WARNING(f'{self.items_counter}:ALREADY LOADED:') + f"{meeting}")
                        else:
                            self.print_io(self.style.SUCCESS(f'{self.items_counter}:') + f"{meeting}")
                    else:
                        self.print_io(
                            self.style.ERROR(f'{self.file_lines_counter}:ERROR:EMPLOYEE DOES NOT EXISTS:') + line)
            elif data_len == 3 or data_len > 4:
                self.print_io(self.style.ERROR(f'{self.file_lines_counter}:ERROR:TRASH:') + line)
        except OperationalError as e:
            self.print_io(self.style.WARNING(f"[handle_meeting_data] ") + self.style.ERROR(e), force_print=True)
            exit(1)
        except Exception as e:
            self.print_io(self.style.WARNING(f"[handle_meeting_data] ") + self.style.ERROR(e), force_print=True)

    def handle(self, *args, **options):
        try:
            if options['file'] is not None:
                self.file_name = options['file']

            if options['verbose']:
                self.verbose = options['verbose'].lower() in ['yes', 'y', '1', 'true', 't', 'yep']

            start_time = time.time()
            employees_lines = self.handle_employee_data()
            meetings_lines = self.handle_meeting_data()
            elapsed = time.time() - start_time

            self.print_io(self.style.SUCCESS(f"Data loaded in {timedelta(seconds=elapsed)}"), force_print=True)
            self.print_io(self.style.SUCCESS(f"Traversed {employees_lines} lines with employee data"), force_print=True)
            self.print_io(self.style.SUCCESS(f"Traversed {meetings_lines} lines with meetings data"), force_print=True)
            self.print_io(self.style.SUCCESS(f"Database contains {Employee.objects.all().count()} employess"),
                          force_print=True)
            self.print_io(self.style.SUCCESS(f"Database contains {Meeting.objects.all().count()} meetings"),
                          force_print=True)
            # self.print_errors()
        except Exception as e:
            self.print_io("[handle] " + self.style.ERROR(e), force_print=True)
            exit(1)
