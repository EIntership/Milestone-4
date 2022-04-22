from rest_framework.test import APITestCase

from apps.managers.utils import Colors
from apps.managers.models import Task, TimeWork, Time, Comment
import random
import json
from django.contrib.auth.models import User
from rest_framework import status

from django.test.client import JSON_CONTENT_TYPE_RE  # noqa
from datetime import datetime, timedelta
from abc import ABC


# Create your base tests here.

class AbstractClass(ABC):
    user_test2 = User.objects.get(username='User')
    time_queryset = Time.objects.all()
    queryset = Task.objects.all()
    comment_queryset = Comment.objects.all()
    fake_data = {
        "name": "string",
        "description": "string",
    }
    update_fake_data = {
        "name": "string1",
        "description": "string1"
    }
    time = {
        "date": f"{datetime.now()}",
        "date_finish": f"{datetime.now()}",  # None
    }
    comment_fake_data = {
        "comment": "alohaaaaaaaaaaaaa"
    }
    fake_data_completed = {
        "completed": 'true'
    }
    fake_data_user = {
        "users": [
            user_test2.id
        ]
    }
    endpoint = '/manager/task/'
    endpoint_my = '/manager/mytask'
    endpoint_complete = '/manager/complete'
    endpoint_user = '/manager/add-task-to-user/'
    def _callTestMethod(self, method):
        class_name = self.__class__.__name__
        method_name = method.__name__
        print(
            f'{Colors.BOLD}{Colors.BLUE} {class_name}{Colors.END} -> {Colors.GREEN}{method_name}{Colors.END}'
        )
        super()._callTestMethod(method)


class TaskCRUDTests(APITestCase, AbstractClass):
    def _callTestMethod(self, method):
        class_name = self.__class__.__name__
        method_name = method.__name__
        print(
            f'{Colors.BOLD}{Colors.BLUE} {class_name}{Colors.END} -> {Colors.GREEN}{method_name}{Colors.END}'
        )
        super()._callTestMethod(method)

    def setUp(self):
        self.user_test1 = User.objects.create(username='test', password='123321')
        self.client.force_authenticate(user=self.user_test1)

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
        id_result = result.get('id')
        updated = self.client.put(path='/manager/task/1/finish_time/',
                                  data=json.dumps({'date_finished': f'{datetime.now()}'}),
                                  content_type='application/json').json()
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
                            data=json.dumps({'date_finished': f'{datetime.now() + timedelta(hours=task.id)}'}),
                            content_type='application/json').json()
        top_biggest_time_task = self.client.get(path=f'{self.endpoint}top-biggest-time-task',
                                                content_type='application/json').json()
        assert (len(top_biggest_time_task) <= 20)

    def test_add_comment(self):

        response = self.client.post(path=f'{self.endpoint}',
                                    data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        comment = self.client.post(path=f'{self.endpoint}{instance.id}/add_comment/',
                                   data=json.dumps(self.comment_fake_data),
                                   content_type='application/json').json()

        self.assertEqual(comment['comment'], self.comment_fake_data['comment'])
        print(f'{Colors.RED}{comment}{Colors.END}')

    def test_comment(self):
        response = self.client.post(path=f'{self.endpoint}',
                                    data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        comment = self.client.post(path=f'{self.endpoint}{instance.id}/add_comment/',
                                   data=json.dumps(self.comment_fake_data),
                                   content_type='application/json').json()
        self.assertEqual(comment['comment'], self.comment_fake_data['comment'])
        result = self.client.get(path=f'{self.endpoint}{instance.id}/comment/',
                                 content_type='application/json').json()
        print(result['task_comment'][0])
        print(f'{Colors.RED}{result}{Colors.END}')


class TestWorkTime(APITestCase, AbstractClass):
    def setUp(self) -> None:
        self.endpoint_work_time = '/manager/work-time/'
        user_test1 = User.objects.create(username='test', password='test1234')
        self.client.force_authenticate(user=user_test1)
        self.queryset = TimeWork.objects.all()
        self.fake_data = {'time_start': f'{datetime.now()}',
                          'time_finish': f'{datetime.now()}'}

    def test_start_time_work(self):
        response = self.client.post(path=f'{self.endpoint_work_time}start/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print(f'{Colors.RED}{response}{Colors.END}')

    def test_finish_time_work(self):
        response = self.client.post(path=f'{self.endpoint_work_time}start/', data=self.fake_data).json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        result = self.client.put(path=f'{self.endpoint_work_time}{instance.id}/finish/',
                                 data=json.dumps(self.fake_data),
                                 content_type='application/json').json()
        instance.refresh_from_db()
        self.assertNotEqual(result.get('time_finish'), None)
        print(f'{Colors.RED}{result}{Colors.END}')


class TestCompletedTask(APITestCase, AbstractClass):
    def setUp(self) -> None:
        user_test1 = User.objects.create(username='test', password='test1234')
        self.client.force_authenticate(user=user_test1)

    def test_completed_task_get(self):
        response = self.client.post(path=self.endpoint,
                                    data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        self.assertEqual(instance.completed, False)
        update = self.client.put(path=f'{self.endpoint_complete}/{instance.id}',
                                 data=json.dumps(self.fake_data_completed),
                                 content_type='application/json').json()
        instance.refresh_from_db()
        self.assertEqual(instance.completed, True)
        detail = self.client.get(path=f'{self.endpoint}detail/{instance.id}',
                                 content_type='application/json').json()
        print(f'{Colors.RED}{detail}{Colors.END}')
#####################################################################################

    def test_complete_task_update(self):
        response = self.client.post(path=self.endpoint,
                                    data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        update = self.client.put(path=f'{self.endpoint}/{instance.id}',
                                 data=json.dumps(self.fake_data_completed),
                                 content_type='application/json').json()
        instance.refresh_from_db()
        self.assertEqual(instance.completed, True)
        print(f'{Colors.RED}{update}{Colors.END}')


class TestAddTaskToUser(APITestCase, AbstractClass):
    def setUp(self) -> None:
        user_test1 = User.objects.create(username='User', password='user')
        self.client.force_authenticate(user=user_test1)

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


class TestMyTask(APITestCase, AbstractClass):
    def setUp(self):
        self.user_test1 = User.objects.create(username='test', password='123321')
        self.client.force_authenticate(user=self.user_test1)

    def test_my_task(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        self.client.get(path=f'{self.endpoint_my}', content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        self.assertEqual(instance.users.filter(id__in=[self.user_test1.id]).exists(), True)
        print(f'{Colors.YELLOW}{instance.users.filter(id__in=[self.user_test1.id])}{Colors.END}')