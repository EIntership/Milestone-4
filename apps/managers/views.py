import requests
from django.db.models import Sum
from rest_framework import generics, permissions
from django.utils import timezone
from django.http import JsonResponse
from apps.managers.models import Task, Comment, Time_Work, Time
from rest_framework.generics import get_object_or_404
from apps.managers.serializers import (
    TaskSerializer,
    TaskDetailsSerializer,
    AssignTaskToUserSerializer,
    CompleteTaskSerializer,
    CommentSerializer,
    ViewCommentsSerializer,
    # TimeLogSerializer,
    TimeWorkSerializer,
    TimeFinishWorkSerializer,
    TimeSerializer,
    TimeFinishSerializer,
    TimeTaskSerializer, )
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta


# Create your views here.


class TaskView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ['name']


class TaskTimeView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


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


# class TimeLogView(generics.ListAPIView):
#    permission_classes = (permissions.IsAuthenticated,)

#    def get(self, request, pk):
#        task = get_object_or_404(Task.objects.filter(pk=pk))
#        return Response(TimeLogSerializer(task).data)


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


class TimeView(generics.CreateAPIView):
    permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeSerializer
    queryset = Time.objects.all()


class TimeFinishView(generics.UpdateAPIView):
    permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeFinishSerializer
    queryset = Time.objects.all()


class TaskMouthView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeSerializer
    queryset = Time.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = super(TaskMouthView, self).get_queryset()
        today = timezone.now()
        from datetime import datetime, timedelta
        x = today - timedelta(days=30)
        queryset = queryset.filter(task__users__id__in=[user.id], date__gte=x, date__lte=today)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        from django.db.models import Sum
        all_sum = queryset.aggregate(Sum('minutes'))['minutes__sum']
        return Response({'minutes': all_sum if all_sum else 0,
                         'time': str(timedelta(minutes=all_sum)),
                         'objects': TimeSerializer(queryset, many=True).data})


class TopBiggestTimeTask(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeTaskSerializer
    queryset = Time.objects.all().order_by('minutes').reverse()[:20]
