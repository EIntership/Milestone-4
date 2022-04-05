from rest_framework import serializers
from apps.managers.models import Task, Comment, Time_Work, Time
from django.core.mail import EmailMessage


class TimeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Time
        fields = ['id', 'date', 'date_finished', 'minutes']


class TaskSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False, write_only=True)
    time = TimeTaskSerializer()

    class Meta:
        model = Task
        fields = ['id', 'name', 'time', 'description']

    def create(self, validated_data):
        request = self.context['request']
        if user := request.user:
            validated_data.update({
                'users': [user]
            })
        return super(TaskSerializer, self).create(validated_data)


class TaskDetailsSerializer(serializers.ModelSerializer):
    time = TimeTaskSerializer()

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'completed', 'users', 'time']


class AssignTaskToUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['users']

    def update(self, instance, validated_data):
        to = []
        for user in validated_data.get('users', []):
            if not getattr(user, "email", None):
                continue
            to.append(user.email)

        email = EmailMessage(
            'Test mail',
            'Task was assigned to you',
            'eugenshow83@gmail.com',
            to
        )
        print(validated_data)
        email.fail_silently = False
        email.send()
        return super(AssignTaskToUserSerializer, self).update(instance, validated_data)


class CompleteTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'completed']

    def update(self, instance, validated_data):
        if not instance.completed:
            print(instance.date)
            instance.completed = not instance.completed
            to = []
            users = instance.users.all()
            for user in users:
                if not getattr(user, "email", None):
                    continue
                to.append(user.email)
            email = EmailMessage(
                'Test mail',
                'You complit a task',
                'eugenshow83@gmail.com',
                to
            )

            email.fail_silently = False
            email.send()
        return super(CompleteTaskSerializer, self).update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['task', 'comment']


class ViewCommentsSerializer(serializers.ModelSerializer):
    task_comment = CommentSerializer(many=True)

    class Meta:
        model = Task
        fields = ['task_comment']


class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Time
        fields = ['date', 'date_finished', 'time']


class TimeWorkSerializer(serializers.ModelSerializer):
    time_start = serializers.DateTimeField(required=True)

    class Meta:
        model = Time_Work
        fields = ['time_start']


class TimeFinishWorkSerializer(serializers.ModelSerializer):
    time_finish = serializers.DateTimeField(required=True)

    class Meta:
        model = Time_Work
        fields = ['time_finish']


class TimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Time
        fields = ['task', 'date']


class TimeFinishSerializer(serializers.ModelSerializer):
    date_finished = serializers.DateTimeField(required=True)

    class Meta:
        model = Time
        fields = ['date_finished']

