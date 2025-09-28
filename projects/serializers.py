from rest_framework import serializers
from .models import Project
from accounts.serializers import UserSerializer


class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(many=True, read_only=True)
    assigned_to_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Project._meta.get_field('assigned_to').related_model.objects.all(),
        source='assigned_to'
    )
    total_tasks = serializers.ReadOnlyField()
    completed_tasks = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'start_date', 'end_date',
            'budget', 'progress', 'created_by', 'assigned_to', 'assigned_to_ids',
            'total_tasks', 'completed_tasks', 'completion_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(many=True, read_only=True)
    total_tasks = serializers.ReadOnlyField()
    completed_tasks = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'start_date', 'end_date',
            'budget', 'progress', 'created_by', 'assigned_to',
            'total_tasks', 'completed_tasks', 'completion_percentage',
            'created_at', 'updated_at'
        ]



