import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Task

User = get_user_model()


class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get token from query string or headers
        token = None
        query_string = self.scope.get('query_string', b'').decode()
        if 'token=' in query_string:
            token = query_string.split('token=')[1].split('&')[0]
        
        if not token:
            await self.close()
            return
        
        # Verify JWT token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if user_id:
                self.user = await self.get_user(user_id)
                if self.user:
                    self.group_name = f"user_{self.user.id}"
                    await self.channel_layer.group_add(
                        self.group_name,
                        self.channel_name
                    )
                    await self.accept()
                else:
                    await self.close()
            else:
                await self.close()
        except jwt.ExpiredSignatureError:
            await self.close()
        except jwt.InvalidTokenError:
            await self.close()
    
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'task_update':
                task_id = text_data_json.get('task_id')
                new_status = text_data_json.get('status')
                
                # Update task status
                await self.update_task_status(task_id, new_status)
                
                # Broadcast update to all relevant users
                await self.broadcast_task_update(task_id, new_status)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    @database_sync_to_async
    def update_task_status(self, task_id, new_status):
        try:
            task = Task.objects.get(id=task_id)
            task.status = new_status
            task.save()
            return task
        except Task.DoesNotExist:
            return None

    async def broadcast_task_update(self, task_id, new_status):
        # Get task details
        task_data = await self.get_task_data(task_id)
        if task_data:
            # Send to task assignee
            if task_data['assigned_to_id']:
                await self.channel_layer.group_send(
                    f"user_{task_data['assigned_to_id']}",
                    {
                        'type': 'task_status_update',
                        'task_id': task_id,
                        'status': new_status,
                        'task_data': task_data
                    }
                )
            
            # Send to project creator
            if task_data['project_created_by_id']:
                await self.channel_layer.group_send(
                    f"user_{task_data['project_created_by_id']}",
                    {
                        'type': 'task_status_update',
                        'task_id': task_id,
                        'status': new_status,
                        'task_data': task_data
                    }
                )

    @database_sync_to_async
    def get_task_data(self, task_id):
        try:
            task = Task.objects.select_related('assigned_to', 'project__created_by').get(id=task_id)
            return {
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'assigned_to_id': task.assigned_to.id if task.assigned_to else None,
                'project_id': task.project.id,
                'project_created_by_id': task.project.created_by.id if task.project.created_by else None,
            }
        except Task.DoesNotExist:
            return None

    async def task_status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_status_update',
            'task_id': event['task_id'],
            'status': event['status'],
            'task_data': event['task_data']
        }))
    
    async def task_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_notification',
            'message': event['message'],
            'task_id': event['task_id'],
            'task_title': event['task_title'],
            'status': event.get('status'),
            'action': event['action']
        }))



