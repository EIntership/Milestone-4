from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
# Create your models here.


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


class Comment(models.Model):
    task = models.ForeignKey(Task, related_name="task_comment", on_delete=models.CASCADE, null=True)
    comment = models.TextField()


class TimeWork(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    time_start = models.DateTimeField(auto_now_add=False, null=True)
    time_finish = models.DateTimeField(auto_now_add=False, null=True)
    minutes = models.IntegerField(null=True, default=0)

    def save(self, **kwargs):
        date = self.time_start
        date_finish = self.time_finish
        if date_finish and date:
            time = date_finish - date
            minute = (time.days * 1440) + (time.seconds // 60)
            self.minutes = minute
        super(TimeWork, self).save(**kwargs)


class Time(models.Model):
    task = models.OneToOneField(Task, related_name="time", on_delete=models.CASCADE, null=True, blank=True)
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


