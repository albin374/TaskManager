from django.contrib import admin
from .models import Task, TaskComment, TaskAttachment


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    readonly_fields = ('user', 'created_at')


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0
    readonly_fields = ('uploaded_by', 'uploaded_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'priority', 'due_date', 'progress')
    list_filter = ('status', 'priority', 'created_at', 'due_date', 'project')
    search_fields = ('title', 'description', 'assigned_to__username', 'project__title')
    ordering = ('-created_at',)
    inlines = [TaskCommentInline, TaskAttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Assignment & Timing', {
            'fields': ('project', 'assigned_to', 'due_date', 'estimated_hours', 'actual_hours', 'progress')
        }),
    )
    
    readonly_fields = ('created_by',)
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new task
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'task__title')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'created_at')


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'filename', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('filename', 'task__title', 'uploaded_by__username')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_by', 'uploaded_at')



