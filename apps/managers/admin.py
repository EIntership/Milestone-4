from django.contrib import admin
from apps.managers.models import *


# Register your models here.

class CommentAdmin(admin.StackedInline):
    model = Comment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = [CommentAdmin]
    list_display = ('name', 'public', 'completed')

    class Meta:
        model = Task


admin.site.register(TaskList)
admin.site.register(Project)
