from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings
from .models import Task, TaskComment, TaskAttachment
from .serializers import (
    TaskSerializer, TaskListSerializer, TaskCommentSerializer,
    TaskCommentCreateSerializer, TaskAttachmentSerializer
)


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Task.objects.all()
        elif user.is_manager:
            return Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user) | Q(project__created_by=user)
            ).distinct()
        else:
            return Task.objects.filter(assigned_to=user)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TaskListSerializer
        return TaskSerializer


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Task.objects.all()
        elif user.is_manager:
            return Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user) | Q(project__created_by=user)
            ).distinct()
        else:
            return Task.objects.filter(assigned_to=user)


class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskComment.objects.filter(task_id=task_id)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCommentCreateSerializer
        return TaskCommentSerializer
    
    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        task = Task.objects.get(id=task_id)
        serializer.save(task=task)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def task_analytics(request):
    user = request.user
    
    # Base queryset based on user role
    if user.is_admin:
        tasks = Task.objects.all()
    elif user.is_manager:
        # Manager can see tasks they are assigned to, created by them, or in projects they created
        tasks = Task.objects.filter(
            Q(assigned_to=user) | Q(created_by=user) | Q(project__created_by=user)
        ).distinct()
    else:
        # Intern can only see tasks assigned to them
        tasks = Task.objects.filter(assigned_to=user)
    
    # Analytics data
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    overdue_tasks = tasks.filter(
        due_date__lt=timezone.now(),
        status__in=['todo', 'in_progress', 'review']
    ).count()
    
    # Status distribution
    status_distribution = tasks.values('status').annotate(count=Count('status'))
    
    # Priority distribution
    priority_distribution = tasks.values('priority').annotate(count=Count('priority'))
    
    # Tasks by user (workload distribution)
    workload_distribution = tasks.values('assigned_to__username').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Completion rate over time (last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    daily_completions = tasks.filter(
        status='completed',
        updated_at__gte=thirty_days_ago
    ).extra(
        select={'day': "date(tasks_task.updated_at)"}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Debug information (only in development)
    if settings.DEBUG:
        print(f"User {user.username} ({user.role}) - Tasks: {total_tasks}")
        if not user.is_admin:
            assigned_tasks = Task.objects.filter(assigned_to=user)
            print(f"Directly assigned tasks: {assigned_tasks.count()}")
            for task in assigned_tasks:
                print(f"  - {task.title} (Status: {task.status}, Project: {task.project.title})")
    
    return Response({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'overdue_tasks': overdue_tasks,
        'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
        'status_distribution': list(status_distribution),
        'priority_distribution': list(priority_distribution),
        'workload_distribution': list(workload_distribution),
        'daily_completions': list(daily_completions),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_tasks(request):
    user = request.user
    tasks = Task.objects.filter(assigned_to=user).order_by('-created_at')
    serializer = TaskListSerializer(tasks, many=True)
    return Response(serializer.data)



