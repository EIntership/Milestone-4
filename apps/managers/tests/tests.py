from django.urls import reverse
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
            1
        ]
    }
    endpoint = '/task/'
    endpoint_my = '/mytask'
    endpoint_complete = '/complete/'
    endpoint_user = '/add-task-to-user/'


class TaskCRUDTests(APITestCase, AbstractClass):

    def setUp(self):
        self.user_test1 = User.objects.create(username='test', password='123321')
        self.client.force_authenticate(user=self.user_test1)

    def test_list(self):
        response = self.client.get(self.endpoint)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        response = self.client.post(self.endpoint, self.fake_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        instance = self.queryset.get()

    def test_task_by_id(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        pk = response.get('id', 0)
        response = self.client.get(path=f'{self.endpoint}{pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy(self) -> None:
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        pk = response.get('id', 0)
        delete_response = self.client.delete(path=f'{self.endpoint}{pk}/', data={})
        self.assertEqual(self.queryset.filter(pk=pk).count(), 0)

    def test_update(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.first()
        result = self.client.put(path=f'{self.endpoint}{instance.id}/', data=json.dumps(self.update_fake_data),
                                 content_type='application/json').json()
        self.assertNotEqual(response, result)

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

    def test_task_start_time(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        self.assertEqual(self.queryset.filter(pk=response.get('id')).count(), 1)
        instance = self.queryset.filter(pk=response.get('id')).first()
        result = self.client.post(path=f'{self.endpoint}{instance.id}/start_time/',
                                  data=json.dumps(self.time),
                                  content_type='application/json').json()
        self.assertEqual(result.get("date_finished"), None)

    def test_task_detail(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        detail = self.client.get(path=f'{self.endpoint}detail/{instance.id}',
                                 content_type='application/json').json()
        self.assertEqual(detail.get('completed'), False)

    def test_my_task(self):
        response = self.client.post(path=self.endpoint, data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        detail = self.client.get(path=f'{self.endpoint_my}',
                                 content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        self.assertEqual(instance.users.filter(id__in=[self.user_test1.id]).exists(), True)

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
        self.assertLessEqual(len(top_biggest_time_task), 20)

    def test_add_comment(self):

        response = self.client.post(path=f'{self.endpoint}',
                                    data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        comment = self.client.post(path=f'{self.endpoint}{instance.id}/add_comment/',
                                   data=json.dumps(self.comment_fake_data),
                                   content_type='application/json').json()

        self.assertEqual(comment['comment'], self.comment_fake_data['comment'])

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
        object_comment = result.get('task_comment')[0]
        self.assertEqual(self.comment_fake_data['comment'], object_comment['comment'])


class TestWorkTime(APITestCase, AbstractClass):
    def setUp(self) -> None:
        self.endpoint_work_time = '/work-time/'
        user_test1 = User.objects.create(username='test', password='test1234')
        self.client.force_authenticate(user=user_test1)
        self.queryset = TimeWork.objects.all()
        self.fake_data = {'time_start': f'{datetime.now()}',
                          'time_finish': f'{datetime.now()}'}

    def test_start_time_work(self):
        response = self.client.post(path=f'{self.endpoint_work_time}start/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_finish_time_work(self):
        response = self.client.post(path=f'{self.endpoint_work_time}start/', data=self.fake_data).json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        result = self.client.put(path=f'{self.endpoint_work_time}{instance.id}/finish/',
                                 data=json.dumps(self.fake_data),
                                 content_type='application/json').json()
        instance.refresh_from_db()
        self.assertNotEqual(result.get('time_finish'), None)


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
        update = self.client.put(path=f'{self.endpoint_complete}{instance.id}',
                                 data=json.dumps(self.fake_data_completed),
                                 content_type='application/json').json()
        instance.refresh_from_db()
        self.assertEqual(instance.completed, True)
        detail = self.client.get(path=f'{self.endpoint}detail/{instance.id}',
                                 content_type='application/json').json()
        self.assertEqual(update.get('id'), detail.get('id'))

    #####################################################################################

    def test_complete_task_update(self):
        response = self.client.post(path=self.endpoint,
                                    data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        self.client.put(path=f'{self.endpoint_complete}{instance.id}',
                        data=json.dumps(self.fake_data_completed),
                        content_type='application/json').json()
        instance.refresh_from_db()
        self.assertEqual(instance.completed, True)


class TestAddTaskToUser(APITestCase, AbstractClass):
    def setUp(self) -> None:
        user_test1 = User.objects.create(username='User', password='user')
        self.client.force_authenticate(user=user_test1)

    def test_add_task_to_user(self):
        response = self.client.post(path=self.endpoint,
                                    data=json.dumps(self.fake_data),
                                    content_type='application/json').json()
        instance = self.queryset.filter(pk=response.get('id')).first()
        self.client.put(path=f'{self.endpoint_user}{instance.id}/',
                        data=json.dumps(self.fake_data_user),
                        content_type='application/json').json()
        instance.refresh_from_db()
        detail = self.client.get(path=f'{self.endpoint}detail/{instance.id}',
                                 content_type='application/json').json()

        # self.assertEqual(detail.get('users'), [1])


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
