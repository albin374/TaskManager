from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User
from .admin_models import AdminAuditLog

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin user management"""
    full_name = serializers.SerializerMethodField()
    total_projects = serializers.SerializerMethodField()
    total_tasks = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()
    is_active_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone_number', 'is_active', 'is_active_display',
            'date_joined', 'last_login', 'created_at',
            'total_projects', 'total_tasks', 'completed_tasks'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    
    def get_total_projects(self, obj):
        return obj.created_projects.count() + obj.assigned_projects.count()
    
    def get_total_tasks(self, obj):
        return obj.assigned_tasks.count()
    
    def get_completed_tasks(self, obj):
        return obj.assigned_tasks.filter(status='completed').count()
    
    def get_is_active_display(self, obj):
        return "Active" if obj.is_active else "Inactive"


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users by admin"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'phone_number', 'is_active'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users by admin"""
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'role', 'phone_number', 'is_active'
        ]
    
    def update(self, instance, validated_data):
        # Log role changes
        if 'role' in validated_data and instance.role != validated_data['role']:
            AdminAuditLog.objects.create(
                admin_user=self.context['request'].user,
                action='role_change',
                target_user=instance,
                description=f"Role changed from {instance.role} to {validated_data['role']}",
                ip_address=self.context['request'].META.get('REMOTE_ADDR'),
                user_agent=self.context['request'].META.get('HTTP_USER_AGENT', '')
            )
        
        return super().update(instance, validated_data)


class AdminProjectSerializer(serializers.ModelSerializer):
    """Serializer for admin project management"""
    created_by_name = serializers.SerializerMethodField()
    assigned_users_count = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        from projects.models import Project
        model = Project
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'start_date', 'end_date', 'budget', 'progress',
            'created_by_name', 'assigned_users_count', 'completion_percentage',
            'created_at', 'updated_at'
        ]
    
    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
    
    def get_assigned_users_count(self, obj):
        return obj.assigned_to.count()
    
    def get_completion_percentage(self, obj):
        return obj.completion_percentage


class AdminAnalyticsSerializer(serializers.Serializer):
    """Serializer for admin analytics data"""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    users_by_role = serializers.DictField()
    projects_by_status = serializers.DictField()
    tasks_by_status = serializers.DictField()
    workload_distribution = serializers.ListField()


class AdminAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for admin audit logs"""
    admin_username = serializers.CharField(source='admin_user.username', read_only=True)
    target_username = serializers.CharField(source='target_user.username', read_only=True)
    
    class Meta:
        model = AdminAuditLog
        fields = [
            'id', 'admin_username', 'action', 'target_username',
            'description', 'ip_address', 'timestamp'
        ]
