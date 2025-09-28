from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from django.conf import settings
from .models import Project
from .serializers import ProjectSerializer, ProjectListSerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Project.objects.all()
        elif user.is_manager:
            return Project.objects.filter(
                Q(created_by=user) | Q(assigned_to=user)
            ).distinct()
        else:
            return Project.objects.filter(assigned_to=user)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectListSerializer
        return ProjectSerializer


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Project.objects.all()
        elif user.is_manager:
            return Project.objects.filter(
                Q(created_by=user) | Q(assigned_to=user)
            ).distinct()
        else:
            return Project.objects.filter(assigned_to=user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def project_analytics(request):
    user = request.user
    
    # Base queryset based on user role
    if user.is_admin:
        projects = Project.objects.all()
    elif user.is_manager:
        # Manager can see projects they created OR are assigned to
        projects = Project.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        ).distinct()
    else:
        # Intern can only see projects they are assigned to
        projects = Project.objects.filter(assigned_to=user)
    
    # Analytics data
    total_projects = projects.count()
    active_projects = projects.filter(status='active').count()
    completed_projects = projects.filter(status='completed').count()
    
    # Status distribution
    status_distribution = projects.values('status').annotate(count=Count('status'))
    
    # Priority distribution
    priority_distribution = projects.values('priority').annotate(count=Count('priority'))
    
    # Projects by month (last 6 months) - simplified for SQLite
    from django.utils import timezone
    from datetime import timedelta
    six_months_ago = timezone.now().date() - timedelta(days=180)
    monthly_projects = projects.filter(
        created_at__date__gte=six_months_ago
    ).extra(
        select={'month': "substr(projects_project.created_at, 1, 7)"}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Debug information (only in development)
    if settings.DEBUG:
        print(f"User {user.username} ({user.role}) - Projects: {total_projects}")
        if not user.is_admin:
            assigned_projects = Project.objects.filter(assigned_to=user)
            print(f"Directly assigned projects: {assigned_projects.count()}")
            for project in assigned_projects:
                print(f"  - {project.title} (Status: {project.status})")
    
    return Response({
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'status_distribution': list(status_distribution),
        'priority_distribution': list(priority_distribution),
        'monthly_projects': list(monthly_projects),
    })



