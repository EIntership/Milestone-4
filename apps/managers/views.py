import datetime
from time import timezone

from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from apps.managers.models import Task, Comment, Time_Work
from rest_framework.generics import get_object_or_404
from apps.managers.serializers import (
    TaskSerializer,
    TaskDetailsSerializer,
    AssignTaskToUserSerializer,
    CompleteTaskSerializer,
    CommentSerializer,
    ViewCommentsSerializer,
    TimeLogSerializer,
    TimeWorkSerializer,
    TimeFinishWorkSerializer,
    TimeSerializer,
    TimeFinishSerializer, )
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


# Create your views here.


class TaskView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ['name']


class TaskDetailView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TaskDetailsSerializer

    def get(self, request, pk):
        task = get_object_or_404(Task.objects.filter(pk=pk))
        return Response(TaskDetailsSerializer(task).data)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return
        return super().get_queryset()


class MyTaskView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(users=user)


class CompletedTaskView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(completed=True)


class AssignTaskToUser(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AssignTaskToUserSerializer
    queryset = Task.objects.all()


class CompleteTaskView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CompleteTaskSerializer
    queryset = Task.objects.all()


class CommentAddView(generics.CreateAPIView):
    permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()


class TimeLogView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        task = get_object_or_404(Task.objects.filter(pk=pk))
        return Response(TimeLogSerializer(task).data)


class TimeLogMouthView(generics.ListAPIView):
    serializer_class = TimeLogSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(users=user, date=datetime.datetime(2022,4,1,8,25,12))


class CommentView(generics.ListAPIView):
    permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = ViewCommentsSerializer

    def get(self, request, pk):
        task = get_object_or_404(Task.objects.filter(pk=pk))
        return Response(ViewCommentsSerializer(task).data)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return
        return super().get_queryset()


class TimeWorkView(generics.ListCreateAPIView):
    permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeWorkSerializer
    queryset = Time_Work.objects.all()


class TimeFinishWorkView(generics.UpdateAPIView):
    permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeFinishWorkSerializer
    queryset = Time_Work.objects.all()


class TimeView(generics.UpdateAPIView):
    permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeSerializer
    queryset = Task.objects.all()


class TimeFinishView(generics.UpdateAPIView):
    permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeFinishSerializer
    queryset = Task.objects.all()
