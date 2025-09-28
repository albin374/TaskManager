from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Task


@receiver(post_save, sender=Task)
def task_created_or_updated(sender, instance, created, **kwargs):
    """Signal handler for when a task is created or updated"""
    if settings.DEBUG:
        action = "created" if created else "updated"
        print(f"Task {action}: {instance.title}")
        print(f"  - Assigned to: {instance.assigned_to.username}")
        print(f"  - Status: {instance.status}")
        print(f"  - Project: {instance.project.title}")
    
    # Send WebSocket notification
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            # Notify the assigned user
            if instance.assigned_to:
                async_to_sync(channel_layer.group_send)(
                    f"user_{instance.assigned_to.id}",
                    {
                        'type': 'task_notification',
                        'message': f"Task '{instance.title}' was {action}",
                        'task_id': instance.id,
                        'task_title': instance.title,
                        'status': instance.status,
                        'action': action
                    }
                )
            
            # Notify the project creator (if different from assigned user)
            if instance.project.created_by and instance.project.created_by != instance.assigned_to:
                async_to_sync(channel_layer.group_send)(
                    f"user_{instance.project.created_by.id}",
                    {
                        'type': 'task_notification',
                        'message': f"Task '{instance.title}' was {action} in project '{instance.project.title}'",
                        'task_id': instance.id,
                        'task_title': instance.title,
                        'status': instance.status,
                        'action': action
                    }
                )
    except Exception as e:
        if settings.DEBUG:
            print(f"Error sending WebSocket notification: {e}")


@receiver(post_delete, sender=Task)
def task_deleted(sender, instance, **kwargs):
    """Signal handler for when a task is deleted"""
    if settings.DEBUG:
        print(f"Task deleted: {instance.title}")
        print(f"  - Was assigned to: {instance.assigned_to.username}")
    
    # Send WebSocket notification
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            # Notify the assigned user
            if instance.assigned_to:
                async_to_sync(channel_layer.group_send)(
                    f"user_{instance.assigned_to.id}",
                    {
                        'type': 'task_notification',
                        'message': f"Task '{instance.title}' was deleted",
                        'task_id': instance.id,
                        'task_title': instance.title,
                        'action': 'deleted'
                    }
                )
    except Exception as e:
        if settings.DEBUG:
            print(f"Error sending WebSocket notification: {e}")
