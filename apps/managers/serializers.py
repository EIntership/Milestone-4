from rest_framework import serializers
from apps.managers.models import Task, Comment, TimeWork, Time
from django.core.mail import EmailMessage


class MakeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'description']

    def create(self, validated_data):
        request = self.context['request']
        if user := request.user:
            validated_data.update({
                'users': [user]
            })
        return super(MakeTaskSerializer, self).create(validated_data)


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
        fields = ['comment']


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
    time_start = serializers.DateTimeField(required=False)
    time_finish = serializers.DateTimeField(required=False)

    class Meta:
        model = TimeWork
        fields = ['id', 'time_start', 'time_finish']

    def validate(self, attrs):
        request = self.context['request']
        method = request.method  # POST, PUT, PATCH
        if method == 'POST':
            attrs.pop('time_finish', None)
        if method == 'PUT':
            attrs.pop('time_start', None)
        return attrs


class TimeSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(required=False)
    date_finished = serializers.DateTimeField(required=False)

    class Meta:
        model = Time
        fields = ['id', 'date', 'date_finished']

    def validate(self, attrs):
        request = self.context['request']
        method = request.method
        if method == 'POST':
            attrs.pop('date_finished', None)
        if method == 'PUT':
            attrs.pop('date', None)
            attrs.pop('task', None)
        return attrs
