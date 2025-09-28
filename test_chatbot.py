#!/usr/bin/env python
"""
Simple test script to verify chatbot functionality
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')
django.setup()

from chatbot.services import ChatbotService

def test_chatbot():
    """Test the chatbot service"""
    print("Testing Chatbot Service...")
    
    chatbot = ChatbotService()
    
    # Test with a sample message
    test_message = "What are the basic requirements for a contract?"
    session_id = 1  # Assuming session exists
    
    print(f"User: {test_message}")
    print("Bot: ", end="")
    
    try:
        for chunk in chatbot.get_law_policy_response(test_message, session_id):
            print(chunk, end="", flush=True)
        print("\n")
        print("✅ Chatbot test completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_chatbot()



