from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import StreamingHttpResponse
import json
from .models import ChatSession, ChatMessage
from .services import ChatbotService


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def chat_with_bot_debug(request, session_id):
    """Debug version of chat with bot"""
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    user_message = request.data.get('message', '')
    if not user_message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Save user message
    ChatMessage.objects.create(
        session=session,
        role='user',
        content=user_message
    )
    
    # Generate bot response
    chatbot_service = ChatbotService()
    
    def generate_response():
        bot_response = ""
        try:
            for chunk in chatbot_service.get_law_policy_response(user_message, session_id):
                bot_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Save bot response
            if bot_response.strip():
                ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=bot_response.strip()
                )
            
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            # Send error response
            error_response = f"I apologize, but I'm experiencing technical difficulties: {str(e)}"
            yield f"data: {json.dumps({'chunk': error_response})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
    
    response = StreamingHttpResponse(
        generate_response(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'Cache-Control'
    return response
