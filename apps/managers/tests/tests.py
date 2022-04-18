from rest_framework.test import APITestCase
from apps.managers.utils import Colors
from apps.managers.models import Task, TimeWork, Time, Comment
import random
import json
from django.contrib.auth.models import User
from rest_framework import status

from django.test.client import JSON_CONTENT_TYPE_RE  # noqa
from datetime import datetime
from abc import ABC


# Create your base tests here.

class AbstractClass(ABC):
    user_test1 = User.objects.get(username='test')

    def setUp(self):
        self.user_test1 = self.user_test1

    def _callTestMethod(self, method):
        class_name = self.__class__.__name__
        method_name = method.__name__
        print(
            f'{Colors.BOLD}{Colors.BLUE} {class_name}{Colors.END} -> {Colors.GREEN}{method_name}{Colors.END}'
        )
        super()._callTestMethod(method)


class TaskCRUDTests(APITestCase, AbstractClass):

    def setUp(self):
        self.client.force_authenticate(user=self.user_test1)
        self.fake_data = {
            "name": "string",
            "description": "string",
        }
        self.update_fake_data = {
            "name": "string1",
            "description": "string1"
        }
        self.time = {
            "date": f"{datetime.now()}",
            "date_finish": f"{datetime.now()}",  # None
        }
        self.comment_fake_data = {
            "comment": "alohaaaaaaaaaaaaa"
        }
        self.endpoint = '/manager/task/'
        self.endpoint_my = '/manager/mytask'
        self.queryset = Task.objects.all()
        self.time_queryset = Time.objects.all()
        self.comment_queryset = Comment.objects.all()

    def test_list(self):
        response = self.client.get(self.endpoint)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(f'{Colors.RED}{response}{Colors.END}')

    def test_create(self):
        response = self.client.post(self.endpoint, self.fake_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        instance = self.queryset.get()
        print(f'{Colors.RED}{response}{Colors.END}')

    def test_task_by_id(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        pk = response.get('id', 0)
        response = self.client.get(path=f'{self.endpoint}{pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(f'{Colors.RED}{response}{Colors.END}')

    def test_destroy(self) -> None:
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        pk = response.get('id', 0)
        delete_response = self.client.delete(path=f'{self.endpoint}{pk}/', data={})
        self.assertEqual(self.queryset.filter(pk=pk).count(), 0)
        print(f'{Colors.RED}{delete_response}{Colors.END}')

    def test_update(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.first()
        result = self.client.put(path=f'{self.endpoint}{instance.id}/', data=json.dumps(self.update_fake_data),
                                 content_type='application/json').json()
        instance.refresh_from_db()
        self.assertNotEqual(response, result)
        print(f'{Colors.RED}{response}->{result}{Colors.END}')

    def test_partial_update(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        self.assertEqual(self.queryset.filter(pk=response.get('id')).count(), 1)
        instance = self.queryset.first()
        index = random.randrange(0, len(self.fake_data))
        data = {**{key: value for key, value in list(self.fake_data.items())[:index]}}
        self.client.patch(path=f'{self.endpoint}{instance.id}/', data=json.dumps(data),
                          content_type='application/json').json()
        instance.refresh_from_db()
        self.assertNotEqual(instance, data)
        print(f'{Colors.RED}Success{Colors.END}')

    def test_task_start_time(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        print(response)
        self.assertEqual(self.queryset.filter(pk=response.get('id')).count(), 1)
        instance = self.queryset.filter(pk=response.get('id')).first()
        result = self.client.post(path=f'{self.endpoint}{instance.id}/start_time/',
                                  data=json.dumps(self.time),
                                  content_type='application/json').json()
        self.assertEqual(result.get("date_finished"), None)
        print(f'{Colors.RED}{result}{Colors.END}')

    def test_task_finish_time(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        self.assertEqual(self.queryset.filter(pk=response.get('id')).count(), 1)
        instance = self.queryset.filter(pk=response.get('id')).first()
        result = self.client.post(path=f'{self.endpoint}{instance.id}/start_time/',
                                  data=json.dumps(self.time),
                                  content_type='application/json').json()
        self.assertEqual(result.get("date_finished"), None)
        # result['date_finished'] = 0
        instance.refresh_from_db()
        updated = self.client.put(path=f'{self.endpoint}{instance.id}/finish_time/', data=json.dumps(self.time),
                                  content_type='application/json').json()
        # instance.refresh_from_db()
        time_instance = self.time_queryset.filter(task=instance).first()
        # self.assertNotEqual(time_instance.date_finished, None)
        print(f'{Colors.YELLOW}{updated}{Colors.END}')

    def test_task_detail(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        detail = self.client.get(path=f'{self.endpoint}detail/{instance.id}',
                                 content_type='application/json').json()
        self.assertEqual(detail.get('completed'), False)
        print(f'{Colors.RED}{detail}{Colors.END}')

    def test_my_task(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        detail = self.client.get(path=f'{self.endpoint_my}',
                                 content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        self.assertEqual(instance.users.filter(id__in=[self.user_test1.id]).exists(), True)
        print(f'{Colors.YELLOW}{instance.users.filter(id__in=[self.user_test1.id])}{Colors.END}')

    def test_top_biggest_time_task(self):
        i = 0
        while i < 30:
            self.client.post(path=self.endpoint,
                             data=json.dumps(self.fake_data),
                             content_type='application/json').json()
            i += 1
        for task in self.queryset:
            self.client.post(path=f'{self.endpoint}{task.id}/start_time/',
                             data=json.dumps(self.time),
                             content_type='application/json').json()
            self.client.put(path=f'{self.endpoint}{task.id}/finish_time/',
                            data=json.dumps(self.time),
                            content_type='application/json').json()
            task.refresh_from_db()
        top_biggest_time_task = self.client.get(path=f'{self.endpoint}top-biggest-time-task',
                                                content_type='application/json').json()
        print(top_biggest_time_task)

    def test_add_comment(self):

        response = self.client.post(path=f'{self.endpoint}',
                                    data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        comment = self.client.post(path=f'{self.endpoint}{instance.id}/add_comment/',
                                   data=json.dumps(self.comment_fake_data),
                                   content_type='application/json').json()
        self.assertNotEqual(comment, None)
        print(f'{Colors.RED}{comment}{Colors.END}')

    def test_comment(self):
        response = self.client.post(path=f'{self.endpoint}',
                                    data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        comment = self.client.post(path=f'{self.endpoint}{instance.id}/add_comment/',
                                   data=json.dumps(self.comment_fake_data),
                                   content_type='application/json').json()
        self.assertNotEqual(comment, None)
        result = self.client.get(path=f'{self.endpoint}{instance.id}/comment/',
                                 content_type='application/json').json()
        print(f'{Colors.RED}{result}{Colors.END}')


class TestWorkTime(APITestCase):
    def _callTestMethod(self, method):
        class_name = self.__class__.__name__
        method_name = method.__name__
        print(
            f'{Colors.BOLD}{Colors.BLUE} {class_name}{Colors.END} -> {Colors.GREEN}{method_name}{Colors.END}'
        )
        super()._callTestMethod(method)

    def setUp(self) -> None:
        self.endpoint = '/manager/work-time/'
        user_test1 = User.objects.create(username='test', password='test1234')
        user_test1.save()
        self.client.force_authenticate(user=user_test1)
        self.queryset = TimeWork.objects.all()
        self.fake_data = {'time_start': f'{datetime.now()}',
                          'time_finish': f'{datetime.now()}'}

    def test_start_time_work(self):
        response = self.client.post(path=f'{self.endpoint}start/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print(f'{Colors.RED}{response}{Colors.END}')

    def test_finish_time_work(self):
        response = self.client.post(path=f'{self.endpoint}start/', data=self.fake_data).json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        result = self.client.put(path=f'{self.endpoint}{instance.id}/finish/',
                                 data=json.dumps(self.fake_data),
                                 content_type='application/json').json()
        instance.refresh_from_db()
        self.assertNotEqual(result.get('time_finish'), None)
        print(f'{Colors.RED}{result}{Colors.END}')


class TestCompletedTask(APITestCase):
    def _callTestMethod(self, method):
        class_name = self.__class__.__name__
        method_name = method.__name__
        print(
            f'{Colors.BOLD}{Colors.BLUE} {class_name}{Colors.END} -> {Colors.GREEN}{method_name}{Colors.END}'
        )
        super()._callTestMethod(method)

    def setUp(self) -> None:
        user_test1 = User.objects.create(username='test', password='test1234')
        user_test1.save()
        self.client.force_authenticate(user=user_test1)
        self.endpoint = '/manager/complete'
        self.endpoint_task = '/manager/task/'
        self.fake_data = {
            "name": "string",
            "description": "string"
        }
        self.fake_data_completed = {
            "completed": 'true'
        }
        self.queryset = Task.objects.all()

    def test_completed_task_get(self):
        response = self.client.post(path=self.endpoint_task,
                                    data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        self.assertEqual(instance.completed, False)
        update = self.client.put(path=f'{self.endpoint}/{instance.id}',
                                 data=json.dumps(self.fake_data_completed),
                                 content_type='application/json').json()
        instance.refresh_from_db()
        self.assertEqual(instance.completed, True)
        detail = self.client.get(path=f'{self.endpoint_task}detail/{instance.id}',
                                 content_type='application/json').json()
       # self.assertEqual()
        print(f'{Colors.RED}{detail}{Colors.END}')

    def test_complete_task_update(self):
        response = self.client.post(path=self.endpoint_task,
                                    data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        update = self.client.put(path=f'{self.endpoint}/{instance.id}',
                                 data=json.dumps(self.fake_data_completed),
                                 content_type='application/json').json()
        instance.refresh_from_db()
        self.assertEqual(instance.completed, True)
        print(f'{Colors.RED}{update}{Colors.END}')


class TestAddTaskToUser(APITestCase):
    def _callTestMethod(self, method):
        class_name = self.__class__.__name__
        method_name = method.__name__
        print(
            f'{Colors.BOLD}{Colors.BLUE} {class_name}{Colors.END} -> {Colors.GREEN}{method_name}{Colors.END}'
        )
        super()._callTestMethod(method)

    def setUp(self) -> None:
        self.fake_data_user = {
            "users": [
                1
            ]
        }
        self.queryset = Task.objects.all()

    def test_add_task_to_user(self):
        response = self.client.post(path=self.endpoint,
                                    data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        self.client.put(path=f'{self.endpoint_user}{instance.id}',
                        data=json.dumps(self.fake_data_user),
                        content_type='application/json').json()
        instance.refresh_from_db()
        detail = self.client.get(path=f'{self.endpoint}detail/{instance.id}',
                                 content_type='application/json').json()
        self.assertEqual(detail.get('users'), [1])
        print(f'{Colors.RED}{detail}{Colors.END}')
