import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Button, Form, Modal, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';

const Chatbot = () => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [showNewSessionModal, setShowNewSessionModal] = useState(false);
  const [newSessionTitle, setNewSessionTitle] = useState('');
  const [darkTheme, setDarkTheme] = useState(false);
  const [streamingResponse, setStreamingResponse] = useState('');
  const messagesEndRef = useRef(null);
  const { user } = useAuth();

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingResponse]);

  useEffect(() => {
    // Apply dark theme to body
    if (darkTheme) {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  }, [darkTheme]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSessions = async () => {
    try {
      const response = await axios.get('/api/chatbot/sessions/');
      setSessions(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching sessions:', error);
      toast.error('Failed to fetch chat sessions');
    }
  };

  const fetchMessages = async (sessionId) => {
    try {
      const response = await axios.get(`/api/chatbot/sessions/${sessionId}/messages/`);
      setMessages(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
      toast.error('Failed to fetch messages');
    }
  };

  const createNewSession = async () => {
    try {
      const response = await axios.post('/api/chatbot/sessions/', {
        title: newSessionTitle || `Chat ${new Date().toLocaleDateString()}`
      });
      const newSession = response.data;
      setSessions(prev => [newSession, ...prev]);
      setCurrentSession(newSession);
      setMessages([]);
      setNewSessionTitle('');
      setShowNewSessionModal(false);
      toast.success('New chat session created!');
    } catch (error) {
      console.error('Error creating session:', error);
      toast.error('Failed to create new session');
    }
  };

  const selectSession = async (session) => {
    setCurrentSession(session);
    await fetchMessages(session.id);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !currentSession) return;

    const userMessage = newMessage.trim();
    setNewMessage('');
    setSendingMessage(true);
    setStreamingResponse('');

    // Add user message to UI immediately
    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      // Use fetch with POST request instead of EventSource
      const response = await fetch(`/api/chatbot/sessions/${currentSession.id}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ message: userMessage })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let botResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.chunk) {
                botResponse += data.chunk;
                setStreamingResponse(botResponse);
              } else if (data.done) {
                // Add complete bot message to messages
                const botMsg = {
                  id: Date.now() + 1,
                  role: 'assistant',
                  content: botResponse,
                  timestamp: new Date().toISOString()
                };
                setMessages(prev => [...prev, botMsg]);
                setStreamingResponse('');
                setSendingMessage(false);
                return;
              }
            } catch (error) {
              console.error('Error parsing SSE data:', error);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
      setSendingMessage(false);
      setStreamingResponse('');
    }
  };

  const downloadChatHistory = async () => {
    if (!currentSession) return;

    try {
      const response = await axios.get(`/api/chatbot/sessions/${currentSession.id}/download/`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `chat_history_${currentSession.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('Chat history downloaded successfully!');
    } catch (error) {
      console.error('Error downloading chat history:', error);
      toast.error('Failed to download chat history');
    }
  };

  const formatMessageTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="fade-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3 mb-0">AI Assistant</h1>
        <div className="d-flex gap-2">
          <Button
            variant={darkTheme ? 'light' : 'dark'}
            onClick={() => setDarkTheme(!darkTheme)}
            size="sm"
          >
            {darkTheme ? '☀️ Light' : '🌙 Dark'}
          </Button>
          <Button variant="outline-primary" onClick={() => setShowNewSessionModal(true)}>
            <i className="fas fa-plus me-2"></i>New Chat
          </Button>
        </div>
      </div>

      <Row>
        {/* Chat Sessions Sidebar */}
        <Col md={3}>
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Chat Sessions</h5>
            </Card.Header>
            <Card.Body className="p-0">
              <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {sessions.map((session) => (
                  <div
                    key={session.id}
                    className={`p-3 border-bottom cursor-pointer ${
                      currentSession?.id === session.id ? 'bg-primary text-white' : ''
                    }`}
                    onClick={() => selectSession(session)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="fw-bold">{session.title}</div>
                    <small className="text-muted">
                      {session.message_count} messages
                    </small>
                    <br />
                    <small className="text-muted">
                      {new Date(session.updated_at).toLocaleDateString()}
                    </small>
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>

        {/* Chat Interface */}
        <Col md={9}>
          <Card className="chatbot-container">
            {currentSession ? (
              <>
                <Card.Header className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">{currentSession.title}</h5>
                  <div>
                    <Button
                      variant="outline-primary"
                      size="sm"
                      onClick={downloadChatHistory}
                      className="me-2"
                    >
                      <i className="fas fa-download me-1"></i>Download PDF
                    </Button>
                    <Button
                      variant="outline-secondary"
                      size="sm"
                      onClick={() => setCurrentSession(null)}
                    >
                      Close
                    </Button>
                  </div>
                </Card.Header>
                <Card.Body className="p-0">
                  <div className="chat-messages">
                    {messages.map((message) => (
                      <div key={message.id} className={`message ${message.role}`}>
                        <div className="message-bubble">
                          <div>{message.content}</div>
                          <small className="text-muted mt-1 d-block">
                            {formatMessageTime(message.timestamp)}
                          </small>
                        </div>
                      </div>
                    ))}
                    
                    {/* Streaming response */}
                    {streamingResponse && (
                      <div className="message assistant">
                        <div className="message-bubble">
                          <div>{streamingResponse}</div>
                          <div className="loading-spinner mt-1"></div>
                        </div>
                      </div>
                    )}
                    
                    <div ref={messagesEndRef} />
                  </div>
                  
                  <div className="chat-input">
                    <Form onSubmit={sendMessage}>
                      <div className="d-flex gap-2">
                        <Form.Control
                          type="text"
                          placeholder="Ask me anything about law and policy..."
                          value={newMessage}
                          onChange={(e) => setNewMessage(e.target.value)}
                          disabled={sendingMessage}
                        />
                        <Button
                          type="submit"
                          variant="primary"
                          disabled={!newMessage.trim() || sendingMessage}
                        >
                          {sendingMessage ? (
                            <Spinner size="sm" animation="border" />
                          ) : (
                            <i className="fas fa-paper-plane"></i>
                          )}
                        </Button>
                      </div>
                    </Form>
                  </div>
                </Card.Body>
              </>
            ) : (
              <Card.Body className="d-flex align-items-center justify-content-center">
                <div className="text-center">
                  <i className="fas fa-robot fa-3x text-muted mb-3"></i>
                  <h4>Welcome to AI Assistant</h4>
                  <p className="text-muted">
                    Select a chat session or create a new one to start chatting about law and policy.
                  </p>
                  <Button variant="primary" onClick={() => setShowNewSessionModal(true)}>
                    Start New Chat
                  </Button>
                </div>
              </Card.Body>
            )}
          </Card>
        </Col>
      </Row>

      {/* New Session Modal */}
      <Modal show={showNewSessionModal} onHide={() => setShowNewSessionModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Create New Chat Session</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group>
            <Form.Label>Session Title</Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter a title for your chat session"
              value={newSessionTitle}
              onChange={(e) => setNewSessionTitle(e.target.value)}
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowNewSessionModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={createNewSession}>
            Create Session
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default Chatbot;
