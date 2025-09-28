# TaskManager Pro - Full-Stack Project Management with AI Chatbot

A comprehensive Task & Project Management Web Application with integrated AI chatbot for law/policy-related queries. Built with Django REST Framework backend and React frontend, featuring real-time updates, analytics, and role-based access control.

## 🎯 Features

### Core Functionality
- **Authentication & Authorization**: JWT-based authentication with role-based access (Admin, Manager, Intern)
- **Project Management**: Full CRUD operations for projects with status tracking and progress monitoring
- **Task Management**: Comprehensive task management with real-time status updates via WebSockets
- **Dashboard & Analytics**: Interactive charts showing project status, task completion rates, and workload distribution
- **AI Chatbot**: Integrated chatbot for law/policy queries with streaming responses and chat history
- **Real-time Updates**: WebSocket integration for live task status updates
- **Responsive Design**: Modern UI with purple+blue+white+black theme and dark/light mode toggle

### Advanced Features
- **Chat History**: Persistent chat sessions with PDF download functionality
- **Contextual Awareness**: Chatbot remembers last 5 messages for better conversations
- **Role-based Dashboards**: Different views and permissions based on user roles
- **File Attachments**: Support for task attachments and comments
- **Progress Tracking**: Visual progress bars and completion percentages
- **Overdue Alerts**: Automatic highlighting of overdue tasks

## 🛠️ Tech Stack

### Backend
- **Django 4.2.7** - Web framework
- **Django REST Framework 3.14.0** - API development
- **Django Simple JWT 5.3.0** - JWT authentication
- **PostgreSQL** - Primary database
- **Redis** - Caching and WebSocket channels
- **Channels 4.0.0** - WebSocket support
- **Celery 5.3.4** - Background tasks
- **Hugging Face Transformers** - AI chatbot integration

### Frontend
- **React 18.2.0** - Frontend framework
- **React Router DOM 6.8.1** - Client-side routing
- **Bootstrap 5.2.3** - UI framework
- **React Bootstrap 2.7.2** - Bootstrap components
- **Chart.js 4.2.1** - Data visualization
- **Axios 1.3.4** - HTTP client
- **Socket.IO Client 4.6.1** - WebSocket client

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp env.example .env
   ```
   Edit `.env` with your configuration:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DB_NAME=taskapp
   DB_USER=postgres
   DB_PASSWORD=Albin@8590301089
   DB_HOST=localhost
   DB_PORT=5432
   REDIS_URL=redis://127.0.0.1:6379/1
   HUGGINGFACE_API_KEY=your-huggingface-api-key
   ```

5. **PostgreSQL Database Setup**
   
   **Option A: Using Docker (Recommended)**
   ```bash
   # Start PostgreSQL and Redis with Docker
   docker-compose up -d db redis
   
   # Run the automated setup script
   python setup_postgresql.py
   ```
   
   **Option B: Manual Setup**
   ```bash
   # Install PostgreSQL (Ubuntu/Debian)
   sudo apt-get install postgresql postgresql-contrib
   
   # Install PostgreSQL (macOS with Homebrew)
   brew install postgresql
   brew services start postgresql
   
   # Install PostgreSQL (Windows)
   # Download from https://www.postgresql.org/download/windows/
   
   # Create database and user
   sudo -u postgres psql
   CREATE DATABASE taskapp;
   CREATE USER postgres WITH PASSWORD 'Albin@8590301089';
   GRANT ALL PRIVILEGES ON DATABASE taskapp TO postgres;
   \q
   
   # Run Django migrations
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

## 🤖 Hugging Face Model Setup

### Getting API Key
1. Visit [Hugging Face](https://huggingface.co/)
2. Create an account and go to Settings
3. Generate a new API token
4. Add the token to your `.env` file

### Model Configuration
The application uses `microsoft/DialoGPT-medium` for chatbot responses. You can modify the model in `chatbot/services.py`:

```python
self.api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
```

### Alternative Models
You can use other models by changing the URL:
- `microsoft/DialoGPT-large` - Larger, more capable model
- `facebook/blenderbot-400M-distill` - Conversational AI
- `microsoft/DialoGPT-small` - Faster, smaller model

## 📱 User Roles & Permissions

### Admin
- Full access to all features
- Can create, edit, delete projects and tasks
- Access to all user management
- View all analytics and reports

### Manager
- Can create and manage projects
- Assign tasks to team members
- View team analytics
- Access to chatbot

### Intern
- View assigned projects and tasks
- Update task status and progress
- Access to chatbot
- Limited dashboard view

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/` - Update user profile

### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Get project details
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project
- `GET /api/projects/analytics/` - Project analytics

### Tasks
- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `GET /api/tasks/{id}/` - Get task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task
- `GET /api/tasks/analytics/` - Task analytics
- `GET /api/tasks/my-tasks/` - User's tasks

### Chatbot
- `GET /api/chatbot/sessions/` - List chat sessions
- `POST /api/chatbot/sessions/` - Create chat session
- `GET /api/chatbot/sessions/{id}/messages/` - Get messages
- `POST /api/chatbot/sessions/{id}/chat/` - Send message (SSE)
- `GET /api/chatbot/sessions/{id}/download/` - Download chat PDF

## 🌐 WebSocket Events

### Task Updates
- **Connection**: `ws://localhost:8000/ws/tasks/`
- **Events**: Real-time task status updates
- **Authentication**: JWT token required

## 📊 Database Schema

### Key Models
- **User**: Custom user model with roles
- **Project**: Project management with status tracking
- **Task**: Task management with assignments and progress
- **ChatSession**: Chat session management
- **ChatMessage**: Individual chat messages

## 🎨 UI/UX Features

### Theme
- **Primary Colors**: Purple (#6f42c1) and Blue (#0d6efd)
- **Accent Colors**: White and Black
- **Gradients**: Purple to blue gradients throughout
- **Dark Mode**: Toggle available in chatbot interface

### Responsive Design
- Mobile-first approach
- Bootstrap 5 grid system
- Custom CSS variables for theming
- Smooth animations and transitions

## 🚀 Deployment

### Production Setup
1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up Redis for production
4. Configure static file serving
5. Set up SSL certificates
6. Configure environment variables

### Docker Deployment (Optional)
```dockerfile
# Add Dockerfile and docker-compose.yml for containerized deployment
```

## 🧪 Testing

### Backend Tests
```bash
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Performance Optimization

### Backend
- Database query optimization
- Redis caching
- Celery for background tasks
- WebSocket connection pooling

### Frontend
- React component optimization
- Lazy loading
- Image optimization
- Bundle splitting

## 🔒 Security Features

- JWT token authentication
- Role-based access control
- CSRF protection
- SQL injection prevention
- XSS protection
- Secure password hashing

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **PostgreSQL Database Connection Error**
   - Check PostgreSQL is running: `sudo systemctl status postgresql` (Linux) or `brew services list | grep postgresql` (macOS)
   - Verify database credentials in `.env`
   - Ensure database exists: `psql -h localhost -U postgres -d taskapp`
   - Check PostgreSQL logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`
   - Test connection: `python manage.py dbshell`

2. **Redis Connection Error**
   - Check Redis is running
   - Verify Redis URL in `.env`

3. **Hugging Face API Error**
   - Check API key is valid
   - Verify internet connection
   - Check API rate limits

4. **WebSocket Connection Issues**
   - Check Redis is running
   - Verify CORS settings
   - Check browser console for errors

### Support
For additional support, please create an issue in the repository or contact the development team.

## 🎥 Demo Video

A comprehensive demo video showcasing:
- User authentication and role-based access
- Project and task management features
- Real-time updates via WebSockets
- Dashboard analytics and charts
- AI chatbot integration with streaming responses
- Chat history and PDF download functionality

## 📸 Screenshots

### Dashboard
- Project summary cards with completion rates
- Interactive charts for status distribution
- Workload distribution visualization
- Real-time statistics

### Project Management
- Project cards with status badges
- Progress tracking with visual indicators
- User assignment and role management
- Priority and deadline management

### Task Management
- Task list with status updates
- Real-time status change notifications
- Overdue task highlighting
- Progress tracking

### AI Chatbot
- Modern chat interface with bubbles
- Streaming response implementation
- Dark/light theme toggle
- Chat session management
- PDF download functionality

---

**Built with ❤️ for efficient project management and AI-powered assistance**




