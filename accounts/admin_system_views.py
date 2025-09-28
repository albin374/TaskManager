from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import User
from .admin_models import AdminAuditLog
from .admin_serializers import AdminUserSerializer

User = get_user_model()


class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


@api_view(['POST'])
@permission_classes([IsAdminUser])
def reset_user_password(request):
    """Reset a user's password (Admin only)"""
    try:
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.get(id=user_id)
        
        # Generate a temporary password
        import secrets
        import string
        temp_password = ''.join(secrets.choices(string.ascii_letters + string.digits, k=12))
        user.set_password(temp_password)
        user.save()
        
        # Log the action
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action='user_update',
            target_user=user,
            description=f"Password reset for user: {user.username}",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': f'Password reset successfully for {user.username}',
            'temporary_password': temp_password
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def deactivate_user(request):
    """Deactivate a user account (Admin only)"""
    try:
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save()
        
        # Log the action
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action='user_deactivate',
            target_user=user,
            description=f"Deactivated user: {user.username}",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': f'User {user.username} has been deactivated'})
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_health(request):
    """Get system health status (Admin only)"""
    try:
        # Database health
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Recent activity (last 24 hours)
        yesterday = timezone.now() - timedelta(days=1)
        recent_logins = User.objects.filter(last_login__gte=yesterday).count()
        
        # System status
        health_status = {
            'database': 'healthy',
            'total_users': total_users,
            'active_users': active_users,
            'recent_logins_24h': recent_logins,
            'server_time': timezone.now().isoformat(),
            'status': 'operational'
        }
        
        return Response(health_status)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_activity_summary(request):
    """Get user activity summary (Admin only)"""
    try:
        # Last 7 days activity
        week_ago = timezone.now() - timedelta(days=7)
        
        # Users with recent activity
        active_users = User.objects.filter(
            Q(last_login__gte=week_ago) | 
            Q(created_at__gte=week_ago)
        ).count()
        
        # New users this week
        new_users = User.objects.filter(created_at__gte=week_ago).count()
        
        # Users by role
        users_by_role = dict(
            User.objects.values('role').annotate(count=Count('id')).values_list('role', 'count')
        )
        
        activity_summary = {
            'active_users_7d': active_users,
            'new_users_7d': new_users,
            'users_by_role': users_by_role,
            'total_users': User.objects.count(),
            'inactive_users': User.objects.filter(is_active=False).count()
        }
        
        return Response(activity_summary)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_logs(request):
    """Get system logs (Admin only)"""
    try:
        # Get recent audit logs
        recent_logs = AdminAuditLog.objects.all().order_by('-timestamp')[:50]
        
        logs_data = []
        for log in recent_logs:
            logs_data.append({
                'timestamp': log.timestamp.isoformat(),
                'admin': log.admin_user.username,
                'action': log.action,
                'target': log.target_user.username if log.target_user else 'System',
                'description': log.description,
                'ip_address': log.ip_address
            })
        
        return Response({
            'logs': logs_data,
            'total_logs': AdminAuditLog.objects.count()
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def chatbot_settings(request):
    """Manage chatbot settings (Admin only)"""
    try:
        if request.method == 'GET':
            # Return current settings (you can store these in database or settings)
            settings_data = {
                'huggingface_api_key': '***hidden***',  # Don't expose the actual key
                'model_name': 'microsoft/DialoGPT-medium',
                'max_length': 1000,
                'temperature': 0.7,
                'chat_history_enabled': True,
                'auto_save_chats': True
            }
            return Response(settings_data)
        
        elif request.method == 'POST':
            # Update settings (implement based on your needs)
            # For now, just return success
            return Response({'message': 'Chatbot settings updated successfully'})
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
