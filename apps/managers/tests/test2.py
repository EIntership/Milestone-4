import re
import requests
from drf_util.utils import gt
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from faker import Faker
from abc import ABC
from django.urls import (get_resolver, URLResolver, URLPattern, reverse, NoReverseMatch, resolve, ResolverMatch)



class AbstractClass(ABC):
    response = requests.get('http://127.0.0.1:8000/?format=openapi')
    data = response.json()
    paths = data.get('paths', {})
    definitions = data.get('definitions', {})
    fake = Faker(['nl_NL'])
    urls = []
    endpoint = '/manager/task/'

    def get_url_patterns(self, patterns, urls):
        for url in patterns.url_patterns:
            if isinstance(url, URLPattern):
                urls.append(url)

            if isinstance(url, URLResolver):
                self.get_url_patterns(url, urls)

    def execution_post_method(self, path: str) -> dict:
        for endpoint, methods in self.paths.items():
            for method in methods.items():
                http_method_name, options = method
                if http_method_name == 'parameters':
                    continue

                ss = endpoint.replace('{id}', '1')
                if http_method_name == 'post' and ss == path:
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
                    data = self.client.post(f'http://127.0.0.1:8000{path}', data=payload)
                    return data

    def execution_get_method(self, path):
        self.get_url_patterns(get_resolver(), urls=self.urls)
        #print(self.urls)
       # print(resolve(path='/manager/task/{id}/'))
        id_path = re.findall('\d', path)

        # for i in self.urls:
        #     print(i)
        #     # print(URLResolver.resolve(i))





        for resolver in self.urls:
            variabila = resolver.resolve(path='^task/(?P<pk>[^/.]+)/finish_time/$')
            print(resolver.callback.__name__)
            if variabila != None:
                print(variabila)





        for endpoint, methods in self.paths.items():
            #x = resolve(path=endpoint)
            #print(x)
            for method in methods.items():
                http_method_name, options = method
                if http_method_name == 'parameters':
                    continue
                try:
                    if http_method_name == 'get' and endpoint.format(**{"id": id_path[0]}) == path:
                        data = self.client.get(f'http://127.0.0.1:8000{path}')
                        return data.json()
                except IndexError:
                    pass


    def execution_put_method(self, path):
        id_path = re.findall('/\d/', path)
        for endpoint, methods in self.paths.items():
            for method in methods.items():
                http_method_name, options = method
                if http_method_name == 'parameters':
                    continue
                endpoint = endpoint.replace('{id}', '1')
                if http_method_name == 'put' and endpoint == path:
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
                    data = self.client.put(f'http://127.0.0.1:8000{path}', data=payload)
                    return data.json()

    def execution_delete_method(self, path):
        for endpoint, methods in self.paths.items():
            for method in methods.items():
                http_method_name, options = method
                if http_method_name == 'parameters':
                    continue
                ss = endpoint.replace('{id}', '1')
                if http_method_name == 'delete' and ss == path:
                    data = self.client.delete(f'http://127.0.0.1:8000{path}')
                    return data.json()


class TestTest(APITestCase, AbstractClass):
    def setUp(self) -> None:
        user_test1 = User.objects.create(username='test1', password='jasgdflkajshdfhkjgqdKLJSVA')
        self.client.force_authenticate(user=user_test1)

    def test_put_task(self):
        s = self.execution_get_method(path=f'{self.endpoint}')
        print(s)
    # def test_create(self):
    #     response = self.execution_post_method(path=f'{self.endpoint}')
    #    # print(response.status)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #
    #  #print(f'{Colors.RED}{response}{Colors.END}')
