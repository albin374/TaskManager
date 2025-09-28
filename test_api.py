#!/usr/bin/env python
"""
Test script to check API endpoints
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

User = get_user_model()

def test_api():
    """Test the API endpoints"""
    print("Testing API endpoints...")
    
    # Test if we can create a user and session
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
        
        # Create a test chat session
        session, created = ChatSession.objects.get_or_create(
            user=user,
            title='Test Session',
            defaults={}
        )
        if created:
            print("✅ Created test chat session")
        else:
            print("✅ Found existing test chat session")
        
        print(f"Session ID: {session.id}")
        print(f"User ID: {user.id}")
        
        # Test the chatbot service directly
        from chatbot.services import ChatbotService
        chatbot = ChatbotService()
        
        print("\nTesting chatbot service...")
        test_message = "What is a contract?"
        print(f"User: {test_message}")
        print("Bot: ", end="")
        
        response_parts = []
        for chunk in chatbot.get_law_policy_response(test_message, session.id):
            response_parts.append(chunk)
            print(chunk, end="", flush=True)
        
        print(f"\n✅ Chatbot service test completed!")
        print(f"Response length: {len(''.join(response_parts))}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()



