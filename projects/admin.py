from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'created_by', 'start_date', 'end_date', 'progress')
    list_filter = ('status', 'priority', 'created_at', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'created_by__username')
    ordering = ('-created_at',)
    filter_horizontal = ('assigned_to',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Dates & Budget', {
            'fields': ('start_date', 'end_date', 'budget', 'progress')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to')
        }),
    )
    
    readonly_fields = ('created_by',)
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new project
            obj.created_by = request.user
        super().save_model(request, obj, form, change)



