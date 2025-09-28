#!/usr/bin/env python
"""
Test authentication and chatbot endpoint
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')
django.setup()

from django.contrib.auth import get_user_model
from chatbot.models import ChatSession
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_auth_and_chatbot():
    """Test authentication and chatbot endpoint"""
    print("Testing authentication and chatbot...")
    
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'intern'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print("✅ Created test user")
        else:
            print("✅ Found existing test user")
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        print(f"✅ Generated JWT token")
        
        # Create a test chat session
        session, created = ChatSession.objects.get_or_create(
            user=user,
            title='Test Session',
            defaults={}
        )
        print(f"✅ Session ID: {session.id}")
        
        # Test the chatbot endpoint
        url = f"http://127.0.0.1:8000/api/chatbot/sessions/{session.id}/chat/"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        data = {
            'message': 'What is a contract?'
        }
        
        print(f"Testing endpoint: {url}")
        response = requests.post(url, headers=headers, json=data, stream=True)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Chatbot endpoint working!")
            # Read streaming response
            for line in response.iter_lines():
                if line:
                    print(f"Stream: {line.decode('utf-8')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth_and_chatbot()



