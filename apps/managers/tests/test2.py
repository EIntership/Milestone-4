import requests
from drf_util.utils import gt
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from faker import Faker
from abc import ABC
from django.urls import (get_resolver, URLResolver, URLPattern, reverse, NoReverseMatch, )
from datetime import datetime


class AbstractClass(ABC):
    response = requests.get('http://127.0.0.1:8000/?format=openapi')
    data = response.json()
    paths = data.get('paths', {})
    definitions = data.get('definitions', {})
    fake = Faker(['nl_NL'])

    def execution_post_method(self, path: str) -> dict:
        for endpoint, methods in self.paths.items():
            for method in methods.items():
                http_method_name, options = method
                if http_method_name == 'parameters':
                    continue

                if http_method_name == 'post' and endpoint == path:
                    params = options.get('parameters', [])
                    body_payload = next(
                        iter([body_object for body_object in params if body_object.get('in', '') == 'body']))
                    definition = gt(body_payload, 'schema.$ref', None)
                    if not definition or not isinstance(definition, str):
                        continue
                    elements = definition.split('/')
                    element = elements[len(elements) - 1]
                    model = gt(self.definitions, f'{element}.properties', {})
                    keys = [key for key in model.keys() if key != 'id']
                    payload = {}
                    for key in keys:
                        if gt(self.definitions, f'{element}.properties.{key}.format', {}) != 'date-time':
                            payload.update({key: self.fake.name()})
                        else:
                            payload.update({key: self.fake.date_time_this_month()})
                    data = self.client.post(f'http://127.0.0.1:8000{endpoint}', data=payload)
                    return data.json()

    def execution_get_method(self, path):
        for endpoint, methods in self.paths.items():
            for method in methods.items():
                http_method_name, options = method
                if http_method_name == 'parameters':
                    continue
                if http_method_name == 'get' and endpoint == path:
                    data = self.client.get(f'http://127.0.0.1:8000{endpoint}')
                    return data.json()

    def execution_get_method_id(self, path):
        print()


class TestTest(APITestCase, AbstractClass):
    def setUp(self) -> None:
        user_test1 = User.objects.create(username='test1', password='jasgdflkajshdfhkjgqdKLJSVA')
        self.client.force_authenticate(user=user_test1)
        self.endpoint = '/manager/work-time/start/'

    def test_task(self):
        result = self.execution_post_method(path=self.endpoint)
        # result = self.execution_get_method(path=self.endpoint)
        print(result)
