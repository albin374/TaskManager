from django.urls import path
from . import views
from . import views_debug

urlpatterns = [
    path('sessions/', views.ChatSessionListCreateView.as_view(), name='chat-session-list'),
    path('sessions/<int:pk>/', views.ChatSessionDetailView.as_view(), name='chat-session-detail'),
    path('sessions/<int:session_id>/messages/', views.ChatMessageListCreateView.as_view(), name='chat-messages'),
    path('sessions/<int:session_id>/chat/', views.chat_with_bot, name='chat-with-bot'),
    path('sessions/<int:session_id>/chat-debug/', views_debug.chat_with_bot_debug, name='chat-with-bot-debug'),
    path('sessions/<int:session_id>/download/', views.download_chat_history, name='download-chat-history'),
    path('stats/', views.chatbot_stats, name='chatbot-stats'),
]
