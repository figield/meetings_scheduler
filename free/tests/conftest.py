import os
import sys
import uuid

import pytest
from faker import Faker
from rest_framework.test import APIClient

from free.models import Employee

sys.path.append(os.path.dirname(__file__))

faker = Faker("en_US")


@pytest.fixture
def client():
    client = APIClient()
    return client


@pytest.fixture
def set_up():
    create_employees(5)


def create_employees(amount):
    for _ in range(amount):
        external_id = uuid.uuid4()
        Employee.objects.create(name=faker.name(), external_id=external_id)
