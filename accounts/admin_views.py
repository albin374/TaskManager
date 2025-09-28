from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpResponse
import csv
import json
from datetime import datetime, timedelta

from .models import User
from .admin_models import AdminAuditLog
from .admin_serializers import (
    AdminUserSerializer, AdminUserCreateSerializer, AdminUserUpdateSerializer,
    AdminProjectSerializer, AdminAnalyticsSerializer, AdminAuditLogSerializer
)
from projects.models import Project
from tasks.models import Task

User = get_user_model()


class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class AdminUserListView(generics.ListCreateAPIView):
    """List all users and create new users (Admin only)"""
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return User.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminUserCreateSerializer
        return AdminUserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Log the action
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action='user_create',
            target_user=user,
            description=f"Created new user: {user.username} with role: {user.role}",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response(
            AdminUserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a user (Admin only)"""
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AdminUserUpdateSerializer
        return AdminUserSerializer
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Log the action
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action='user_update',
            target_user=user,
            description=f"Updated user: {user.username}",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response(AdminUserSerializer(user).data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        username = instance.username
        
        # Log the action before deletion
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action='user_delete',
            target_user=instance,
            description=f"Deleted user: {username}",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminProjectListView(generics.ListAPIView):
    """List all projects (Admin only)"""
    permission_classes = [IsAdminUser]
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = AdminProjectSerializer


class AdminProjectDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a project (Admin only)"""
    permission_classes = [IsAdminUser]
    queryset = Project.objects.all()
    serializer_class = AdminProjectSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project_title = instance.title
        
        # Log the action
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action='project_delete',
            target_user=None,
            description=f"Deleted project: {project_title}",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_analytics(request):
    """Get system-wide analytics (Admin only)"""
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Project statistics
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status__in=['planning', 'active']).count()
    
    # Task statistics
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status='completed').count()
    overdue_tasks = Task.objects.filter(
        due_date__lt=timezone.now(),
        status__in=['todo', 'in_progress', 'review']
    ).count()
    
    # Users by role
    users_by_role = dict(User.objects.values('role').annotate(count=Count('id')).values_list('role', 'count'))
    
    # Projects by status
    projects_by_status = dict(Project.objects.values('status').annotate(count=Count('id')).values_list('status', 'count'))
    
    # Tasks by status
    tasks_by_status = dict(Task.objects.values('status').annotate(count=Count('id')).values_list('status', 'count'))
    
    # Workload distribution
    workload_distribution = []
    for user in User.objects.filter(is_active=True):
        task_count = user.assigned_tasks.count()
        completed_count = user.assigned_tasks.filter(status='completed').count()
        workload_distribution.append({
            'user': f"{user.first_name} {user.last_name}".strip() or user.username,
            'role': user.role,
            'total_tasks': task_count,
            'completed_tasks': completed_count,
            'completion_rate': round((completed_count / task_count * 100) if task_count > 0 else 0, 2)
        })
    
    analytics_data = {
        'total_users': total_users,
        'active_users': active_users,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'users_by_role': users_by_role,
        'projects_by_status': projects_by_status,
        'tasks_by_status': tasks_by_status,
        'workload_distribution': workload_distribution
    }
    
    return Response(analytics_data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_audit_logs(request):
    """Get admin audit logs (Admin only)"""
    logs = AdminAuditLog.objects.all().order_by('-timestamp')[:100]  # Last 100 actions
    serializer = AdminAuditLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def export_users_csv(request):
    """Export users list as CSV (Admin only)"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Username', 'Email', 'First Name', 'Last Name', 
        'Role', 'Phone Number', 'Is Active', 'Date Joined', 'Last Login'
    ])
    
    for user in User.objects.all():
        writer.writerow([
            user.id, user.username, user.email, user.first_name, user.last_name,
            user.role, user.phone_number, user.is_active, user.date_joined, user.last_login
        ])
    
    # Log the export action
    AdminAuditLog.objects.create(
        admin_user=request.user,
        action='user_create',  # Using existing action for export
        target_user=None,
        description="Exported users list as CSV",
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return response


@api_view(['POST'])
@permission_classes([IsAdminUser])
def export_analytics_report(request):
    """Export analytics report as JSON (Admin only)"""
    # Get analytics data
    analytics_response = admin_analytics(request)
    analytics_data = analytics_response.data
    
    response = HttpResponse(
        json.dumps(analytics_data, indent=2, default=str),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="analytics_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    
    # Log the export action
    AdminAuditLog.objects.create(
        admin_user=request.user,
        action='user_create',  # Using existing action for export
        target_user=None,
        description="Exported analytics report",
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return response
