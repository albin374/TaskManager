import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Button, Modal, Form, Badge, Spinner, Alert, Table } from 'react-bootstrap';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';

const Tasks = () => {
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'todo',
    priority: 'medium',
    due_date: '',
    estimated_hours: '',
    project_id: '',
    assigned_to_id: ''
  });
  const { user } = useAuth();
  const wsRef = useRef(null);

  useEffect(() => {
    fetchTasks();
    fetchProjects();
    fetchUsers();
    
    // Initialize WebSocket connection
    initializeWebSocket();
    
    // Cleanup WebSocket on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const initializeWebSocket = () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/tasks/?token=${token}`;
    
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      console.log('WebSocket connected');
    };
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'task_status_update') {
        // Update task status in real-time
        setTasks(prevTasks => 
          prevTasks.map(task => 
            task.id === data.task_id 
              ? { ...task, status: data.status }
              : task
          )
        );
        
        toast.info(`Task "${data.task_data.title}" status updated to ${data.status}`);
      }
    };
    
    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const fetchTasks = async () => {
    try {
      const response = await axios.get('/api/tasks/');
      setTasks(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      toast.error('Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await axios.get('/api/projects/');
      setProjects(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get('/api/auth/users/');
      setUsers(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingTask) {
        await axios.put(`/api/tasks/${editingTask.id}/`, formData);
        toast.success('Task updated successfully!');
      } else {
        await axios.post('/api/tasks/', formData);
        toast.success('Task created successfully!');
      }
      setShowModal(false);
      setEditingTask(null);
      resetForm();
      fetchTasks();
    } catch (error) {
      console.error('Error saving task:', error);
      toast.error('Failed to save task');
    }
  };

  const handleEdit = (task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description,
      status: task.status,
      priority: task.priority,
      due_date: task.due_date ? task.due_date.split('T')[0] : '',
      estimated_hours: task.estimated_hours || '',
      project_id: task.project?.id || '',
      assigned_to_id: task.assigned_to?.id || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (taskId) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await axios.delete(`/api/tasks/${taskId}/`);
        toast.success('Task deleted successfully!');
        fetchTasks();
      } catch (error) {
        console.error('Error deleting task:', error);
        toast.error('Failed to delete task');
      }
    }
  };

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      await axios.patch(`/api/tasks/${taskId}/`, { status: newStatus });
      toast.success('Task status updated!');
      fetchTasks();
    } catch (error) {
      console.error('Error updating task status:', error);
      toast.error('Failed to update task status');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      status: 'todo',
      priority: 'medium',
      due_date: '',
      estimated_hours: '',
      project_id: '',
      assigned_to_id: ''
    });
  };

  const openModal = () => {
    resetForm();
    setEditingTask(null);
    setShowModal(true);
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'todo': { variant: 'secondary', text: 'To Do' },
      'in_progress': { variant: 'warning', text: 'In Progress' },
      'review': { variant: 'info', text: 'Review' },
      'completed': { variant: 'success', text: 'Completed' },
      'cancelled': { variant: 'danger', text: 'Cancelled' }
    };
    const statusInfo = statusMap[status] || { variant: 'secondary', text: status };
    return <Badge bg={statusInfo.variant}>{statusInfo.text}</Badge>;
  };

  const getPriorityBadge = (priority) => {
    const priorityMap = {
      'low': { variant: 'secondary', text: 'Low' },
      'medium': { variant: 'primary', text: 'Medium' },
      'high': { variant: 'warning', text: 'High' },
      'urgent': { variant: 'danger', text: 'Urgent' }
    };
    const priorityInfo = priorityMap[priority] || { variant: 'secondary', text: priority };
    return <Badge bg={priorityInfo.variant}>{priorityInfo.text}</Badge>;
  };

  const isOverdue = (dueDate) => {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date() && new Date(dueDate).toDateString() !== new Date().toDateString();
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
        <Spinner animation="border" variant="primary" />
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3 mb-0">Tasks</h1>
        {(user?.role === 'admin' || user?.role === 'manager') && (
          <Button variant="primary" onClick={openModal}>
            <i className="fas fa-plus me-2"></i>New Task
          </Button>
        )}
      </div>

      <Card>
        <Card.Body>
          <Table responsive hover>
            <thead>
              <tr>
                <th>Title</th>
                <th>Project</th>
                <th>Assigned To</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Due Date</th>
                <th>Progress</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.id} className={isOverdue(task.due_date) ? 'table-warning' : ''}>
                  <td>
                    <div>
                      <strong>{task.title}</strong>
                      {isOverdue(task.due_date) && (
                        <Badge bg="danger" className="ms-2">Overdue</Badge>
                      )}
                    </div>
                    <small className="text-muted">{task.description}</small>
                  </td>
                  <td>{task.project?.title}</td>
                  <td>{task.assigned_to?.first_name} {task.assigned_to?.last_name}</td>
                  <td>
                    <Form.Select
                      size="sm"
                      value={task.status}
                      onChange={(e) => handleStatusChange(task.id, e.target.value)}
                      style={{ width: 'auto' }}
                    >
                      <option value="todo">To Do</option>
                      <option value="in_progress">In Progress</option>
                      <option value="review">Review</option>
                      <option value="completed">Completed</option>
                      <option value="cancelled">Cancelled</option>
                    </Form.Select>
                  </td>
                  <td>{getPriorityBadge(task.priority)}</td>
                  <td>
                    {task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}
                  </td>
                  <td>
                    <div className="d-flex align-items-center">
                      <div className="progress me-2" style={{ width: '60px', height: '8px' }}>
                        <div 
                          className="progress-bar" 
                          style={{ width: `${task.progress}%` }}
                        ></div>
                      </div>
                      <small>{task.progress}%</small>
                    </div>
                  </td>
                  <td>
                    <div className="d-flex gap-1">
                      <Button 
                        variant="outline-primary" 
                        size="sm" 
                        onClick={() => handleEdit(task)}
                      >
                        Edit
                      </Button>
                      {(user?.role === 'admin' || user?.role === 'manager') && (
                        <Button 
                          variant="outline-danger" 
                          size="sm" 
                          onClick={() => handleDelete(task.id)}
                        >
                          Delete
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>

      {/* Enhanced Task Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="xl" centered>
        <Modal.Header closeButton className="border-0">
          <div className="d-flex align-items-center">
            <div className="me-3">
              <i className="fas fa-tasks fa-2x"></i>
            </div>
            <div>
              <Modal.Title className="mb-0">
                {editingTask ? 'Edit Task' : 'Create New Task'}
              </Modal.Title>
              <small className="opacity-75">
                {editingTask ? 'Update task details and assignments' : 'Create a new task and assign it to team members'}
              </small>
            </div>
          </div>
        </Modal.Header>
        
        <Form onSubmit={handleSubmit}>
          <Modal.Body className="p-0">
            {/* Form Steps Indicator */}
            <div className="form-steps">
              <div className="form-step active">1</div>
              <div className="form-step">2</div>
              <div className="form-step">3</div>
            </div>
            
            <div className="px-4 pb-4">
              {/* Basic Information Section */}
              <div className="mb-4">
                <h6 className="text-muted mb-3">
                  <i className="fas fa-info-circle me-2"></i>
                  Task Information
                </h6>
                <Row>
                  <Col md={8}>
                    <Form.Group className="mb-3 form-group-with-icon">
                      <Form.Label>Task Title</Form.Label>
                      <i className="fas fa-tag form-icon"></i>
                      <Form.Control
                        type="text"
                        name="title"
                        value={formData.title}
                        onChange={handleInputChange}
                        placeholder="Enter task title"
                        required
                      />
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>Status</Form.Label>
                      <Form.Select
                        name="status"
                        value={formData.status}
                        onChange={handleInputChange}
                      >
                        <option value="todo">📋 To Do</option>
                        <option value="in_progress">🚀 In Progress</option>
                        <option value="review">👀 Review</option>
                        <option value="completed">✅ Completed</option>
                        <option value="cancelled">❌ Cancelled</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>

                <Form.Group className="mb-3">
                  <Form.Label>Description</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    placeholder="Describe the task requirements and objectives..."
                    style={{ resize: 'none' }}
                  />
                </Form.Group>
              </div>

              {/* Task Details Section */}
              <div className="mb-4">
                <h6 className="text-muted mb-3">
                  <i className="fas fa-cog me-2"></i>
                  Task Details
                </h6>
                <Row>
                  <Col md={3}>
                    <Form.Group className="mb-3">
                      <Form.Label>Priority</Form.Label>
                      <Form.Select
                        name="priority"
                        value={formData.priority}
                        onChange={handleInputChange}
                      >
                        <option value="low">🟢 Low</option>
                        <option value="medium">🟡 Medium</option>
                        <option value="high">🟠 High</option>
                        <option value="urgent">🔴 Urgent</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                  <Col md={3}>
                    <Form.Group className="mb-3 form-group-with-icon">
                      <Form.Label>Due Date</Form.Label>
                      <i className="fas fa-calendar-alt form-icon"></i>
                      <Form.Control
                        type="datetime-local"
                        name="due_date"
                        value={formData.due_date}
                        onChange={handleInputChange}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={3}>
                    <Form.Group className="mb-3 form-group-with-icon">
                      <Form.Label>Estimated Hours</Form.Label>
                      <i className="fas fa-clock form-icon"></i>
                      <Form.Control
                        type="number"
                        step="0.5"
                        name="estimated_hours"
                        value={formData.estimated_hours}
                        onChange={handleInputChange}
                        placeholder="0.0"
                      />
                    </Form.Group>
                  </Col>
                  <Col md={3}>
                    <Form.Group className="mb-3">
                      <Form.Label>Progress</Form.Label>
                      <div className="d-flex align-items-center">
                        <Form.Range
                          name="progress"
                          value={formData.progress || 0}
                          onChange={handleInputChange}
                          min="0"
                          max="100"
                          className="me-2"
                        />
                        <span className="text-muted small">{formData.progress || 0}%</span>
                      </div>
                    </Form.Group>
                  </Col>
                </Row>
              </div>

              {/* Assignment Section */}
              <div className="mb-4">
                <h6 className="text-muted mb-3">
                  <i className="fas fa-user-plus me-2"></i>
                  Assignment
                </h6>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3 form-group-with-icon">
                      <Form.Label>Project</Form.Label>
                      <i className="fas fa-project-diagram form-icon"></i>
                      <Form.Select
                        name="project_id"
                        value={formData.project_id}
                        onChange={handleInputChange}
                        required
                      >
                        <option value="">Select a project</option>
                        {projects.map((project) => (
                          <option key={project.id} value={project.id}>
                            {project.title}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3 form-group-with-icon">
                      <Form.Label>Assign To</Form.Label>
                      <i className="fas fa-user form-icon"></i>
                      <Form.Select
                        name="assigned_to_id"
                        value={formData.assigned_to_id}
                        onChange={handleInputChange}
                        required
                      >
                        <option value="">Select a user</option>
                        {users.map((user) => (
                          <option key={user.id} value={user.id}>
                            {user.first_name} {user.last_name} ({user.role})
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>
              </div>
            </div>
          </Modal.Body>
          
          <Modal.Footer className="border-0 bg-light">
            <div className="d-flex justify-content-between w-100">
              <Button 
                variant="outline-secondary" 
                onClick={() => setShowModal(false)}
                className="btn-form btn-form-secondary"
              >
                <i className="fas fa-times me-2"></i>
                Cancel
              </Button>
              <Button 
                type="submit" 
                className="btn-form btn-form-primary"
              >
                <i className="fas fa-save me-2"></i>
                {editingTask ? 'Update Task' : 'Create Task'}
              </Button>
            </div>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  );
};

export default Tasks;



