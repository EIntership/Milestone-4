from rest_framework import routers
from django.urls import path
from apps.managers.views import (
    TaskView,
    TaskDetailView,
    MyTaskView,
    CompletedTaskView,
    AssignTaskToUser,
    CompleteTaskView,
    # CommentAddView,
    # CommentView,
    TimeWorkView,
    TimeView,
    TaskMonthView,
    TopBiggestTimeTask,
)

router = routers.SimpleRouter()
router.register(r'work-time', TimeWorkView)
router.register(r'time', TimeView)
router.register(r'task', TaskView)

urlpatterns = [
    #path('task', TaskView.as_view(), name='create-task-view'),
    path('task/detail/<int:pk>', TaskDetailView.as_view(), name='task-info-view'),
    path('task/top-biggest-time-task', TopBiggestTimeTask.as_view(), name='task-time-log-view'),
    path('time-month', TaskMonthView.as_view(), name='task-time-log-view'),
    path('mytask', MyTaskView.as_view(), name='my-task-view'),
    path('complete', CompletedTaskView.as_view(), name='completed-task'),
    path('add-task-to-user/<int:pk>', AssignTaskToUser.as_view(), name="add-task-to-user"),
    path('complete/<int:pk>', CompleteTaskView.as_view(), name="complete-task-view"),

]
urlpatterns += router.urls
