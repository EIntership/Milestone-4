from django.db import models
from django.conf import settings
import datetime


# Create your models here.
from django.http import HttpResponse


class Task(models.Model):
    name = models.CharField(max_length=35)
    description = models.TextField()
    public = models.BooleanField('completed', default=False)
    priority = models.CharField(
        max_length=6,
        choices=(
            ('NONE', 'None'),
            ('LOW', 'Low'),
            ('Medium', 'Medium'),
            ('HIGH', 'High'),
        )
        ,
        default='NONE',
        db_index=True
    )
    completed = models.BooleanField(default=False)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='users'
    )

    def __str__(self):
        return self.name


class TaskList(models.Model):
    tasks = models.ManyToManyField(Task, blank=True)
    name = models.CharField(max_length=250, unique=False)

    def __str__(self):
        return self.name


class Project(models.Model):
    task = models.ForeignKey(TaskList, related_name="project", null=True, on_delete=models.CASCADE)
    name = models.CharField(null=True, max_length=250)
    description = models.TextField()
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True
    )

    def __str__(self):
        return self.name


class Comment(models.Model):
    task = models.ForeignKey(Task, related_name="task_comment", on_delete=models.CASCADE, null=True)
    comment = models.TextField()


class Time_Work(models.Model):
    time_start = models.DateTimeField(auto_now_add=True)
    time_finish = models.DateTimeField(auto_now_add=False, null=True)
    time = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if self.time_finish:
            self.time = self.time_finish.replace(tzinfo=None)-self.time_start.replace(tzinfo=None)
        super(Time_Work, self).save(*args, **kwargs)


class Time(models.Model):
    task = models.OneToOneField(Task, related_name="time", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=False, null=True)
    date_finished = models.DateTimeField(auto_now_add=False, null=True)
    minutes = models.IntegerField(null=True, default=0)

    def save(self, **kwargs):
        date = self.date
        date_finish = self.date_finished
        if date_finish and date:
            time = date_finish - date
            minute = (time.days * 1440)+(time.seconds//60)
            self.minutes = minute
        super(Time, self).save(**kwargs)





