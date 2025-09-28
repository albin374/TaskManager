from rest_framework import serializers
from .models import Task, TaskComment, TaskAttachment
from accounts.serializers import UserSerializer
from projects.serializers import ProjectListSerializer


class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'filename', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']


class TaskCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'content', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Task._meta.get_field('assigned_to').related_model.objects.all(),
        source='assigned_to'
    )
    project_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Task._meta.get_field('project').related_model.objects.all(),
        source='project'
    )
    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'due_date',
            'estimated_hours', 'actual_hours', 'progress', 'project', 'project_id',
            'assigned_to', 'assigned_to_id', 'created_by', 'comments', 'attachments',
            'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'due_date',
            'estimated_hours', 'actual_hours', 'progress', 'project',
            'assigned_to', 'is_overdue', 'created_at', 'updated_at'
        ]


class TaskCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComment
        fields = ['content']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['task'] = self.context['task']
        return super().create(validated_data)



