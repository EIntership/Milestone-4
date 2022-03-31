from django.urls import path
from apps.managers.views import (
    TaskView,
    TaskDetailView,
    MyTaskView,
    CompletedTaskView,
    AssignTaskToUser,
    CompleteTaskView,
    CommentAddView,
    CommentView,
    TimeLogView,)

urlpatterns = [
    path('task', TaskView.as_view(), name='create-task-view'),
    path('task/<int:pk>', TaskDetailView.as_view(), name='task-info-view'),
    path('time/<int:pk>', TimeLogView.as_view(), name='task-time-log-view'),
    path('mytask', MyTaskView.as_view(), name='my-task-view'),
    path('compited-task', CompletedTaskView.as_view(), name='completed-task'),
    path('add-task-to-user/<int:pk>', AssignTaskToUser.as_view(), name="add-task-to-user"),
    path('complete-task/<int:pk>', CompleteTaskView.as_view(), name="complete-task-view"),
    path('add-comment', CommentAddView.as_view(), name="comment-add-view"),
    path('comment/<int:pk>', CommentView.as_view(), name="comment-view"),
]