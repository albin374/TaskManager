from django.urls import path
from . import admin_views, admin_system_views

urlpatterns = [
    # User Management
    path('users/', admin_views.AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<int:pk>/', admin_views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    
    # Project Management
    path('projects/', admin_views.AdminProjectListView.as_view(), name='admin-project-list'),
    path('projects/<int:pk>/', admin_views.AdminProjectDetailView.as_view(), name='admin-project-detail'),
    
    # Analytics
    path('analytics/', admin_views.admin_analytics, name='admin-analytics'),
    
    # Audit Logs
    path('audit-logs/', admin_views.admin_audit_logs, name='admin-audit-logs'),
    
    # Export Functions
    path('export/users-csv/', admin_views.export_users_csv, name='admin-export-users-csv'),
    path('export/analytics-report/', admin_views.export_analytics_report, name='admin-export-analytics'),
    
    # System Control
    path('system/chatbot-settings/', admin_system_views.chatbot_settings, name='admin-chatbot-settings'),
    path('system/health/', admin_system_views.system_health, name='admin-system-health'),
    path('system/user-activity/', admin_system_views.user_activity_summary, name='admin-user-activity'),
    path('system/logs/', admin_system_views.system_logs, name='admin-system-logs'),
    
    # User Management Actions
    path('users/reset-password/', admin_system_views.reset_user_password, name='admin-reset-password'),
    path('users/deactivate/', admin_system_views.deactivate_user, name='admin-deactivate-user'),
]
