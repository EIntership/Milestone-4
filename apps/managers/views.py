from django.db.models import Sum
from rest_framework import generics, permissions, viewsets
from django.utils import timezone
from rest_framework.decorators import action

from apps.managers.models import Task, Comment, TimeWork, Time
from rest_framework.generics import get_object_or_404
from apps.managers.serializers import (
    TaskSerializer,
    TaskDetailsSerializer,
    AssignTaskToUserSerializer,
    CompleteTaskSerializer,
    CommentSerializer,
    ViewCommentsSerializer,
    TimeWorkSerializer,
    # TimeFinishWorkSerializer,
    TimeSerializer,
    # TimeFinishSerializer,
    TimeTaskSerializer,
    MakeTaskSerializer, )
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta


# Create your views here.


class TaskView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Task.objects.all()
    serializer_class = MakeTaskSerializer
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


class TimeWorkView(viewsets.ModelViewSet):  # generics.ListCreateAPIView):
    permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeWorkSerializer
    queryset = TimeWork.objects.all()

    @action(detail=False, methods=["POST"])
    def start(self, request):
        data = request.data
        user = request.user
        serializer = TimeWorkSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=201)
        return Response({'status': 'negative'})

    @action(detail=True, methods=["PUT"])
    def finish(self, request, pk=None):
        data = request.data
        instance = TimeWork.objects.filter(id=pk).first()
        serializer = TimeWorkSerializer(data=data, instance=instance, context={'request': request})
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=201)


class TimeView(viewsets.ModelViewSet):
    permissions_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeSerializer
    queryset = Time.objects.all()

    @action(detail=False, methods=["POST"])
    def start(self, request):
        data = request.data
        serializer = TimeSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        print(serializer.is_valid())
        return Response({'status': 'negative'})

    @action(detail=True, methods=["PUT"])
    def finish(self, request, pk=None):
        data = request.data
        instance = Time.objects.filter(id=pk).first()
        serializer = TimeSerializer(data=data, instance=instance, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response({'status': 'negative'})


# class TimeFinishView(generics.UpdateAPIView):
#    permissions_classes = (permissions.IsAuthenticated,)
#    serializer_class = TimeFinishSerializer
#    queryset = Time.objects.all()


class TaskMonthView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeSerializer
    queryset = Time.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = super(TaskMonthView, self).get_queryset()
        today = timezone.now()
        month = today - timedelta(days=30)
        queryset = queryset.filter(task__users__id__in=[user.id], date__gte=month, date__lte=today)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        all_sum = queryset.aggregate(Sum('minutes'))['minutes__sum']
        return Response({'minutes': all_sum if all_sum else 0,
                         'time': str(timedelta(minutes=all_sum)),
                         'objects': TimeSerializer(queryset, many=True).data})


class TopBiggestTimeTask(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeTaskSerializer
    queryset = Time.objects.all()

    def get_queryset(self):
        queryset = super(TopBiggestTimeTask, self).get_queryset()
        queryset = queryset.filter().order_by('minutes').reverse()[:20]
        return queryset
