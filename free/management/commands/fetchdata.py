# -*- coding: utf-8 -*-
import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help="The name of the target file [freebusy.txt]")
        parser.add_argument('--url', type=str, help="Download file via http request")

    def handle(self, *args, **options):
        try:
            remote_url = options['url']
            if remote_url is None:
                remote_url = "https://builds.lundalogik.com/api/v1/builds/freebusy/versions/1.0.0/file"

            file_name = options['file']
            if file_name is None:
                file_name = "freebusy.txt"

            # Make http request for remote file data
            data = requests.get(remote_url)

            # Save file data to local copy
            with open(file_name, 'wb') as file:
                file.write(data.content)

            self.stdout.write(self.style.SUCCESS('Download completed'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(e))
            exit(1)

# python3 manage.py fetchdata