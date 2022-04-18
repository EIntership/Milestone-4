import random

from django.core.management.base import BaseCommand
from faker import Faker
import faker.providers
from apps.managers.models import Time, Task
import requests

url = 'https://www.boredapi.com/api/activity'


class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['nl_NL'])

        for _ in range(25000):
            task = name = fake.name() + ' task'
            randBits = bool(random.getrandbits(1))
            Task.objects.create(name=task, description=task, completed=randBits)
