from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from django.template.loader import render_to_string
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import json
from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer, ChatSessionListSerializer,
    ChatMessageSerializer, ChatMessageCreateSerializer
)
from .services import ChatbotService


class ChatSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ChatSessionListSerializer
        return ChatSessionSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChatSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)


class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return ChatMessage.objects.filter(
            session_id=session_id,
            session__user=self.request.user
        )
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChatMessageCreateSerializer
        return ChatMessageSerializer
    
    def perform_create(self, serializer):
        session_id = self.kwargs['session_id']
        session = ChatSession.objects.get(id=session_id, user=self.request.user)
        serializer.save(session=session)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def chat_with_bot(request, session_id):
    """Handle chat with the bot and return streaming response"""
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
    
    try:
        # Collect the full response first
        bot_response = ""
        for chunk in chatbot_service.get_law_policy_response(user_message, session_id):
            bot_response += chunk
        
        # Save bot response
        if bot_response.strip():
            ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=bot_response.strip()
            )
        
        # Return streaming response
        def generate_response():
            # Simulate streaming by sending the response in chunks
            words = bot_response.split()
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'chunk': word + ' '})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        response = StreamingHttpResponse(
            generate_response(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Cache-Control'
        return response
        
    except Exception as e:
        # Return error response
        error_response = f"I apologize, but I'm experiencing technical difficulties: {str(e)}"
        
        def generate_error_response():
            yield f"data: {json.dumps({'chunk': error_response})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        response = StreamingHttpResponse(
            generate_error_response(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Cache-Control'
        return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_chat_history(request, session_id):
    """Download chat history as PDF"""
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    user_style = ParagraphStyle(
        'UserMessage',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=12,
        textColor='blue'
    )
    
    bot_style = ParagraphStyle(
        'BotMessage',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=12,
        textColor='purple'
    )
    
    # Build PDF content
    story = []
    
    # Title
    story.append(Paragraph(f"Chat History - {session.title or f'Session {session.id}'}", title_style))
    story.append(Spacer(1, 12))
    
    # Messages
    for message in messages:
        if message.role == 'user':
            story.append(Paragraph(f"<b>You:</b> {message.content}", user_style))
        else:
            story.append(Paragraph(f"<b>Assistant:</b> {message.content}", bot_style))
        story.append(Spacer(1, 6))
    
    doc.build(story)
    
    # Prepare response
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="chat_history_{session_id}.pdf"'
    
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chatbot_stats(request):
    """Get chatbot usage statistics"""
    user = request.user
    
    total_sessions = ChatSession.objects.filter(user=user).count()
    total_messages = ChatMessage.objects.filter(session__user=user).count()
    
    # Recent activity
    recent_sessions = ChatSession.objects.filter(user=user).order_by('-updated_at')[:5]
    recent_sessions_data = ChatSessionListSerializer(recent_sessions, many=True).data
    
    return Response({
        'total_sessions': total_sessions,
        'total_messages': total_messages,
        'recent_sessions': recent_sessions_data
    })
