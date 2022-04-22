import re
import requests
from drf_util.utils import gt
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from faker import Faker
from abc import ABC
from datetime import datetime


class AbstractClass(ABC):
    def __init__(self, api):
        self.response = api
        self.data = self.response.json()
        self.paths = self.data.get('paths', {})
        self.definitions = self.data.get('definitions', {})
        self.fake = Faker(['nl_NL'])

    urls = []
    endpoint = None
    endpoint_work_time = '/manager/work-time/'

    def execution_method(self, path, http_method):
        id_path = re.findall('\d', path)
        for endpoint, methods in self.paths.items():
            for method in methods.items():
                http_method_name, options = method
                if http_method_name == 'parameters':
                    continue
                try:
                    endpoint = endpoint.format(**{"id": id_path[0]})
                except IndexError:
                    pass
                if http_method_name == http_method and endpoint == path:

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
                            payload.update({key: self.fake.date_time_this_month(after_now=True)})
                    return payload

    def execution_post_method(self, path: str, client) -> dict:
        data = client.post(f'http://127.0.0.1:8000{path}', data=self.execution_method(path, http_method='post'))
        return data.json()

    def execution_get_method(self, path, client):
        id_path = re.findall('\d', path)
        for endpoint, methods in self.paths.items():
            for method in methods.items():
                http_method_name, options = method
                if http_method_name == 'parameters':
                    continue
                try:
                    endpoint = endpoint.format(**{"id": id_path[0]})
                except IndexError:
                    pass
                if http_method_name == 'get' and endpoint == path:
                    data = client.get(f'http://127.0.0.1:8000{path}')
                    return data.json()

    def execution_put_method(self, path, client):
        data = client.put(f'http://127.0.0.1:8000{path}', data=self.execution_method(path, http_method='put'))
        return data.json()

    def execution_delete_method(self, path, client):
        data = client.delete(f'http://127.0.0.1:8000{path}')
        return data


class TestCrudTask(APITestCase, AbstractClass):
    endpoint = '/manager/task/'

    def setUp(self) -> None:
        user_test1 = User.objects.create(username='admin', password='admin')
        self.object = AbstractClass(requests.get('http://127.0.0.1:8000/?format=openapi'))
        self.client.force_authenticate(user=user_test1)

    def test_post_task(self):
        response = self.object.execution_post_method(path=f'{self.endpoint}', client=self.client)
        self.assertEqual(response.get('id'), 1)

    def test_put_task(self):
        response = self.object.execution_post_method(path=f'{self.endpoint}', client=self.client)
        id_response = response.get('id')
        name_response = response.get('name')
        self.assertEqual(id_response, 1)
        update = self.object.execution_put_method(path=f'{self.endpoint}{id_response}/', client=self.client)
        id_update = update.get('id')
        name_update = update.get('name')
        self.assertEqual(id_response, id_update)
        self.assertNotEqual(name_update, name_response)

    def test_get_list_task(self):
        response = self.object.execution_post_method(path=f'{self.endpoint}', client=self.client)
        self.assertEqual(response.get('id'), 1)
        get_response = self.object.execution_get_method(path=f'{self.endpoint}', client=self.client)
        self.assertEqual(get_response[0].get('name'), response.get('name'))

    def test_get_task(self):
        response = self.object.execution_post_method(path=f'{self.endpoint}', client=self.client)
        id_response = response.get('id')
        self.assertEqual(id_response, 1)
        get_response = self.object.execution_get_method(path=f'{self.endpoint}{id_response}/', client=self.client)
        self.assertEqual(get_response.get('name'), response.get('name'))

    def test_delete_task(self):
        response = self.object.execution_post_method(path=f'{self.endpoint}', client=self.client)
        id_response = response.get('id')
        self.assertEqual(id_response, 1)
        delete = self.object.execution_delete_method(path=f'{self.endpoint}{id_response}/', client=self.client)
        get_response = self.object.execution_get_method(path=f'{self.endpoint}{id_response}/', client=self.client)
        self.assertEqual(delete.status_code, 204)
        self.assertEqual(get_response.get('detail'), 'Not found.')

    def test_task_add_comment(self):
        response = self.object.execution_post_method(path=f'{self.endpoint}', client=self.client)
        id_response = response.get('id')
        self.assertEqual(id_response, 1)
        comment = self.object.execution_post_method(path=f'{self.endpoint}{id_response}/add_comment/',
                                                    client=self.client)
        self.assertEqual(type(comment.get('comment')), str)

    def test_task_get_comment(self):
        response = self.object.execution_post_method(path=f'{self.endpoint}', client=self.client)
        id_response = response.get('id')
        self.assertEqual(id_response, 1)
        comment = self.object.execution_post_method(path=f'{self.endpoint}{id_response}/add_comment/',
                                                    client=self.client)
        self.assertEqual(type(comment.get('comment')), str)
        get_comment = self.object.execution_get_method(path=f'{self.endpoint}{id_response}/comment/',
                                                       client=self.client)
        self.assertEqual(get_comment['task_comment'][0].get('comment'), comment.get('comment'))

    def test_task_start_time(self):
        response = self.object.execution_post_method(path=f'{self.endpoint}', client=self.client)
        id_response = response.get('id')
        self.assertEqual(id_response, 1)
        time = self.object.execution_post_method(path=f'{self.endpoint}{id_response}/start_time/', client=self.client)
        time_id = time.get('id')
        self.assertEqual(time.get('date_finish'), None)
        self.assertIn('2022-04', time.get('date'))
        self.assertEqual(time_id, 1)

    def test_task_finish_time(self):
        response = self.object.execution_post_method(path=f'{self.endpoint}', client=self.client)
        id_response = response.get('id')
        time = self.object.execution_post_method(path=f'{self.endpoint}{id_response}/start_time/', client=self.client)
        time_finish = self.object.execution_put_method(path=f'{self.endpoint}{id_response}/finish_time/',
                                                       client=self.client)
        self.assertEqual(time.get('id'), time_finish.get('id'))
        self.assertNotEqual(time_finish.get('date_finished'), None)

    def test_task_top_biggest_time_task(self):
        i = 1
        while i < 30:
            self.object.execution_post_method(path=f'{self.endpoint}', client=self.client)
            self.object.execution_post_method(path=f'{self.endpoint}{i}/start_time/',
                                              client=self.client)
            self.object.execution_put_method(path=f'{self.endpoint}{i}/finish_time/',
                                             client=self.client)
            i += 1
        top_biggest_time_task = self.object.execution_get_method(path=f'{self.endpoint}top-biggest-time-task',
                                                                 client=self.client)
        self.assertLess(len(top_biggest_time_task), 20)

    def test_task_detail(self):
        response = self.object.execution_post_method(path=f'{self.endpoint}', client=self.client)
        id_response = response.get('id')
        self.assertEqual(id_response, 1)
        detail = self.object.execution_get_method(path=f'{self.endpoint}detail/{id_response}', client=self.client)
        self.assertEqual(len(detail), 6)


class TestMyTask(APITestCase, AbstractClass):
    def setUp(self):
        self.user_test1 = User.objects.create(username='admin', password='admin')
        self.object = AbstractClass(requests.get('http://127.0.0.1:8000/?format=openapi'))
        self.client.force_authenticate(user=self.user_test1)

    def test_my_task(self):
        response = self.object.execution_post_method(path=f'{self.endpoint}', client=self.client)
        id_response = response.get('id')
        self.object.execution_get_method(path=f'/manager/mytask', client=self.client)
        detail = self.object.execution_get_method(path=f'{self.endpoint}detail/{id_response}', client=self.client)
        self.assertEqual(detail['users'][0], self.user_test1.id)


class TestWorkTime(APITestCase, AbstractClass):
    def setUp(self) -> None:
        user_test1 = User.objects.create(username='test', password='test1234')
        self.client.force_authenticate(user=user_test1)
        self.object = AbstractClass(requests.get('http://127.0.0.1:8000/?format=openapi'))

    def test_start_time_work(self):
        response = self.object.execution_post_method(path=f'{self.endpoint_work_time}start/', client=self.client)
        self.assertEqual(response.get('time_finish'), None)

    def test_finish_time_work(self):
        response = self.object.execution_post_method(path=f'{self.endpoint_work_time}start/', client=self.client)
        self.assertEqual(response.get('time_finish'), None)
        id_response = response.get('id')
        finish = self.object.execution_put_method(path=f'{self.endpoint_work_time}{id_response}/finish/',
                                                  client=self.client)
        self.assertNotEqual(finish.get('time_finish'), None)

# class TestCompletedTask(APITestCase, AbstractClass):
#     def setUp(self) -> None:
#         user_test1 = User.objects.create(username='test', password='test1234')
#         self.client.force_authenticate(user=user_test1)
#         self.object = AbstractClass(requests.get('http://127.0.0.1:8000/?format=openapi'))
#
#     def test_completed_task_get(self):
#         response = self.object.execution_post_method(path=f'{self.endpoint_work_time}start/', client=self.client)
#         instance = self.queryset.filter(pk=response.get('id')).first()
#         self.assertEqual(instance.completed, False)
#         update = self.client.put(path=f'{self.endpoint_complete}/{instance.id}',
#                                  data=json.dumps(self.fake_data_completed),
#                                  content_type='application/json').json()
#         instance.refresh_from_db()
#         self.assertEqual(instance.completed, True)
#         detail = self.client.get(path=f'{self.endpoint}detail/{instance.id}',
#                                  content_type='application/json').json()
#
        # id_result = result.get('id')
        # self.object.execution_put_method(path=f'{self.endpoint}{id_result}/', client=self.client)
        # print(self.object.execution_get_method(path=f'{self.endpoint}{id_result}/', client=self.client))
        # print(self.object.execution_delete_method(path=f'{self.endpoint}{id_result}/', client=self.client))
