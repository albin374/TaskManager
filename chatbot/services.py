import json
import requests
import time
import random
from typing import List, Dict, Generator
from django.conf import settings
from .models import ChatMessage


class ChatbotService:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        self.headers = {
            "Authorization": f"Bearer {getattr(settings, 'HUGGINGFACE_API_KEY', '')}"
        }
        self.context_window = 5  # Keep last 5 messages for context
        
        # Fallback responses for when API is not available
        self.fallback_responses = [
            "I understand you're asking about legal matters. While I can provide general information, I recommend consulting with a qualified attorney for specific legal advice.",
            "That's an interesting legal question. In general, laws vary by jurisdiction, so it's important to check local regulations and consult with a legal professional.",
            "I can help explain general legal concepts, but for specific legal matters, I'd recommend speaking with an attorney who specializes in that area of law.",
            "Legal questions often require careful consideration of specific facts and circumstances. A qualified attorney would be best positioned to provide detailed guidance.",
            "I'm here to help with general legal information. For complex legal matters, professional legal counsel is typically the best approach."
        ]
    
    def get_context_messages(self, session_id: int) -> List[Dict]:
        """Get the last few messages for context"""
        messages = ChatMessage.objects.filter(
            session_id=session_id
        ).order_by('-timestamp')[:self.context_window]
        
        context = []
        for msg in reversed(messages):
            context.append({
                'role': msg.role,
                'content': msg.content
            })
        
        return context
    
    def generate_response(self, user_message: str, session_id: int) -> Generator[str, None, None]:
        """Generate streaming response from the chatbot"""
        try:
            # Get context
            context = self.get_context_messages(session_id)
            
            # Prepare the conversation history
            conversation = []
            for msg in context:
                if msg['role'] == 'user':
                    conversation.append(f"Human: {msg['content']}")
                elif msg['role'] == 'assistant':
                    conversation.append(f"Assistant: {msg['content']}")
            
            # Add current user message
            conversation.append(f"Human: {user_message}")
            conversation.append("Assistant:")
            
            # Join conversation
            full_conversation = "\n".join(conversation)
            
            # Check if we have API key
            api_key = getattr(settings, 'HUGGINGFACE_API_KEY', '')
            if not api_key:
                # Use fallback response
                response_text = random.choice(self.fallback_responses)
                # Simulate streaming by yielding word by word
                words = response_text.split()
                for word in words:
                    yield word + " "
                    time.sleep(0.1)  # Small delay to simulate streaming
                return
            
            # Make API call to Hugging Face
            payload = {
                "inputs": full_conversation,
                "parameters": {
                    "max_length": 200,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                # Stream the response
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'generated_text' in data:
                                yield data['generated_text']
                        except json.JSONDecodeError:
                            continue
            else:
                # Fallback response
                response_text = random.choice(self.fallback_responses)
                words = response_text.split()
                for word in words:
                    yield word + " "
                    time.sleep(0.1)
                
        except Exception as e:
            # Fallback response
            response_text = random.choice(self.fallback_responses)
            words = response_text.split()
            for word in words:
                yield word + " "
                time.sleep(0.1)
    
    def get_law_policy_response(self, user_message: str, session_id: int) -> Generator[str, None, None]:
        """Generate law/policy specific responses"""
        # Enhanced responses for law/policy queries
        law_responses = [
            "I understand you're asking about legal matters. While I can provide general information, I recommend consulting with a qualified attorney for specific legal advice.",
            "That's an interesting legal question. In general, laws vary by jurisdiction, so it's important to check local regulations and consult with a legal professional.",
            "I can help explain general legal concepts, but for specific legal matters, I'd recommend speaking with an attorney who specializes in that area of law.",
            "Legal questions often require careful consideration of specific facts and circumstances. A qualified attorney would be best positioned to provide detailed guidance.",
            "I'm here to help with general legal information. For complex legal matters, professional legal counsel is typically the best approach.",
            "That's a good question about legal procedures. Generally speaking, legal processes can be complex and vary by location, so professional guidance is often helpful.",
            "I can provide general information about legal concepts, but remember that laws can change and vary by jurisdiction. Consulting with a legal expert is recommended for specific situations."
        ]
        
        try:
            context = self.get_context_messages(session_id)
            
            # Check if we have API key
            api_key = getattr(settings, 'HUGGINGFACE_API_KEY', '')
            if not api_key:
                # Use fallback response
                response_text = random.choice(law_responses)
                # Simulate streaming by yielding word by word
                words = response_text.split()
                for word in words:
                    yield word + " "
                    time.sleep(0.1)  # Small delay to simulate streaming
                return
            
            # Build conversation with law context
            law_context = "You are a helpful legal assistant. You provide general information about laws and policies. You should be informative but not provide specific legal advice."
            conversation = [law_context]
            for msg in context:
                if msg['role'] == 'user':
                    conversation.append(f"Human: {msg['content']}")
                elif msg['role'] == 'assistant':
                    conversation.append(f"Assistant: {msg['content']}")
            
            conversation.append(f"Human: {user_message}")
            conversation.append("Assistant:")
            
            full_conversation = "\n".join(conversation)
            
            payload = {
                "inputs": full_conversation,
                "parameters": {
                    "max_length": 300,
                    "temperature": 0.6,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'generated_text' in data:
                                yield data['generated_text']
                        except json.JSONDecodeError:
                            continue
            else:
                response_text = random.choice(law_responses)
                words = response_text.split()
                for word in words:
                    yield word + " "
                    time.sleep(0.1)
                
        except Exception as e:
            response_text = random.choice(law_responses)
            words = response_text.split()
            for word in words:
                yield word + " "
                time.sleep(0.1)
