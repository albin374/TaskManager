import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Button, Modal, Form, Badge, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'planning',
    priority: 'medium',
    start_date: '',
    end_date: '',
    budget: '',
    assigned_to_ids: []
  });
  const { user } = useAuth();
  const wsRef = useRef(null);

  useEffect(() => {
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
      console.log('WebSocket connected for projects');
    };
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'task_status_update') {
        // Refresh projects to show updated task counts
        fetchProjects();
        toast.info(`Task status updated in project`);
      }
    };
    
    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const fetchProjects = async () => {
    try {
      const response = await axios.get('/api/projects/');
      setProjects(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
      toast.error('Failed to fetch projects');
    } finally {
      setLoading(false);
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
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = e.target.checked;
      setFormData(prev => ({
        ...prev,
        assigned_to_ids: checked
          ? [...prev.assigned_to_ids, parseInt(value)]
          : prev.assigned_to_ids.filter(id => id !== parseInt(value))
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingProject) {
        await axios.put(`/api/projects/${editingProject.id}/`, formData);
        toast.success('Project updated successfully!');
      } else {
        await axios.post('/api/projects/', formData);
        toast.success('Project created successfully!');
      }
      setShowModal(false);
      setEditingProject(null);
      resetForm();
      fetchProjects();
    } catch (error) {
      console.error('Error saving project:', error);
      toast.error('Failed to save project');
    }
  };

  const handleEdit = (project) => {
    setEditingProject(project);
    setFormData({
      title: project.title,
      description: project.description,
      status: project.status,
      priority: project.priority,
      start_date: project.start_date,
      end_date: project.end_date,
      budget: project.budget || '',
      assigned_to_ids: project.assigned_to?.map(user => user.id) || []
    });
    setShowModal(true);
  };

  const handleDelete = async (projectId) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await axios.delete(`/api/projects/${projectId}/`);
        toast.success('Project deleted successfully!');
        fetchProjects();
      } catch (error) {
        console.error('Error deleting project:', error);
        toast.error('Failed to delete project');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      status: 'planning',
      priority: 'medium',
      start_date: '',
      end_date: '',
      budget: '',
      assigned_to_ids: []
    });
  };

  const openModal = () => {
    resetForm();
    setEditingProject(null);
    setShowModal(true);
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'planning': { variant: 'secondary', text: 'Planning' },
      'active': { variant: 'primary', text: 'Active' },
      'on_hold': { variant: 'warning', text: 'On Hold' },
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
        <h1 className="h3 mb-0">Projects</h1>
        {(user?.role === 'admin' || user?.role === 'manager') && (
          <Button variant="primary" onClick={openModal}>
            <i className="fas fa-plus me-2"></i>New Project
          </Button>
        )}
      </div>

      <Row>
        {projects.map((project) => (
          <Col md={6} lg={4} key={project.id} className="mb-4">
            <Card className="h-100 project-card shadow-sm">
              <Card.Header className="d-flex justify-content-between align-items-center bg-light border-0">
                <h5 className="mb-0 fw-semibold">{project.title}</h5>
                <div className="d-flex gap-2">
                  {getStatusBadge(project.status)}
                  {getPriorityBadge(project.priority)}
                </div>
              </Card.Header>
              <Card.Body>
                <p className="text-muted">{project.description}</p>
                <div className="mb-2">
                  <small className="text-muted">
                    <strong>Created by:</strong> {project.created_by?.first_name} {project.created_by?.last_name}
                  </small>
                </div>
                <div className="mb-2">
                  <small className="text-muted">
                    <strong>Start:</strong> {new Date(project.start_date).toLocaleDateString()}
                  </small>
                </div>
                <div className="mb-2">
                  <small className="text-muted">
                    <strong>End:</strong> {new Date(project.end_date).toLocaleDateString()}
                  </small>
                </div>
                {project.budget && (
                  <div className="mb-2">
                    <small className="text-muted">
                      <strong>Budget:</strong> ${project.budget}
                    </small>
                  </div>
                )}
                <div className="mb-3">
                  <small className="text-muted">
                    <strong>Progress:</strong> {project.completion_percentage}%
                  </small>
                  <div className="progress mt-1">
                    <div 
                      className="progress-bar" 
                      style={{ width: `${project.completion_percentage}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <small className="text-muted">
                    <strong>Assigned to:</strong> {project.assigned_to?.map(user => user.first_name).join(', ') || 'No one'}
                  </small>
                </div>
              </Card.Body>
              <Card.Footer>
                <div className="d-flex gap-2">
                  {(user?.role === 'admin' || user?.role === 'manager') && (
                    <>
                      <Button 
                        variant="outline-primary" 
                        size="sm" 
                        onClick={() => handleEdit(project)}
                      >
                        Edit
                      </Button>
                      <Button 
                        variant="outline-danger" 
                        size="sm" 
                        onClick={() => handleDelete(project.id)}
                      >
                        Delete
                      </Button>
                    </>
                  )}
                </div>
              </Card.Footer>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Enhanced Project Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="xl" centered>
        <Modal.Header closeButton className="border-0 bg-gradient-primary text-white">
          <div className="d-flex align-items-center">
            <div className="me-3">
              <div className="bg-white bg-opacity-20 rounded-circle p-3">
                <i className="fas fa-project-diagram fa-2x"></i>
              </div>
            </div>
            <div>
              <Modal.Title className="mb-0 fw-bold">
                {editingProject ? 'Edit Project' : 'Create New Project'}
              </Modal.Title>
              <small className="opacity-90">
                {editingProject ? 'Update project details and settings' : 'Set up a new project with team assignments'}
              </small>
            </div>
          </div>
        </Modal.Header>
        
        <Form onSubmit={handleSubmit}>
          <Modal.Body className="p-0">
            {/* Form Steps Indicator */}
            <div className="form-steps">
              <div className="form-step active">
                <i className="fas fa-info-circle"></i>
                <span>Basic Info</span>
              </div>
              <div className="form-step">
                <i className="fas fa-cog"></i>
                <span>Details</span>
              </div>
              <div className="form-step">
                <i className="fas fa-users"></i>
                <span>Team</span>
              </div>
            </div>
            
            <div className="px-4 pb-4">
              {/* Basic Information Section */}
              <div className="mb-4">
                <div className="d-flex align-items-center mb-3">
                  <div className="bg-primary bg-opacity-10 rounded-circle p-2 me-3">
                    <i className="fas fa-info-circle text-primary"></i>
                  </div>
                  <h6 className="mb-0 fw-semibold">Basic Information</h6>
                </div>
            <Row>
                  <Col md={8}>
                    <Form.Group className="mb-3 form-group-with-icon">
                      <Form.Label>Project Title</Form.Label>
                      <i className="fas fa-tag form-icon"></i>
                  <Form.Control
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                        placeholder="Enter project title"
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
                        <option value="planning">📋 Planning</option>
                        <option value="active">🚀 Active</option>
                        <option value="on_hold">⏸️ On Hold</option>
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
                    placeholder="Describe the project objectives and scope..."
                    style={{ resize: 'none' }}
              />
            </Form.Group>
              </div>

              {/* Project Details Section */}
              <div className="mb-4">
                <div className="d-flex align-items-center mb-3">
                  <div className="bg-success bg-opacity-10 rounded-circle p-2 me-3">
                    <i className="fas fa-cog text-success"></i>
                  </div>
                  <h6 className="mb-0 fw-semibold">Project Details</h6>
                </div>
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
                  <Form.Label>Start Date</Form.Label>
                      <i className="fas fa-calendar-alt form-icon"></i>
                  <Form.Control
                    type="date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleInputChange}
                    required
                  />
                </Form.Group>
              </Col>
                  <Col md={3}>
                    <Form.Group className="mb-3 form-group-with-icon">
                  <Form.Label>End Date</Form.Label>
                      <i className="fas fa-calendar-check form-icon"></i>
                  <Form.Control
                    type="date"
                    name="end_date"
                    value={formData.end_date}
                    onChange={handleInputChange}
                    required
                  />
                </Form.Group>
              </Col>
                  <Col md={3}>
                    <Form.Group className="mb-3 form-group-with-icon">
              <Form.Label>Budget</Form.Label>
                      <i className="fas fa-dollar-sign form-icon"></i>
              <Form.Control
                type="number"
                step="0.01"
                name="budget"
                value={formData.budget}
                onChange={handleInputChange}
                        placeholder="0.00"
              />
            </Form.Group>
                  </Col>
                </Row>
              </div>

              {/* Team Assignment Section */}
              <div className="mb-4">
                <div className="d-flex align-items-center mb-3">
                  <div className="bg-warning bg-opacity-10 rounded-circle p-2 me-3">
                    <i className="fas fa-users text-warning"></i>
                  </div>
                  <h6 className="mb-0 fw-semibold">Team Assignment</h6>
                </div>
                <div className="row">
                {users.map((user) => (
                    <Col md={6} lg={4} key={user.id} className="mb-3">
                      <div className="form-check form-check-card">
                        <input
                          className="form-check-input"
                    type="checkbox"
                    id={`user-${user.id}`}
                    checked={formData.assigned_to_ids.includes(user.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFormData(prev => ({
                                ...prev,
                                assigned_to_ids: [...prev.assigned_to_ids, user.id]
                              }));
                            } else {
                              setFormData(prev => ({
                                ...prev,
                                assigned_to_ids: prev.assigned_to_ids.filter(id => id !== user.id)
                              }));
                            }
                          }}
                        />
                        <label className="form-check-label w-100" htmlFor={`user-${user.id}`}>
                          <div className="d-flex align-items-center p-2 border rounded">
                            <div className="avatar-sm me-3">
                              <div className="avatar-title bg-primary text-white rounded-circle">
                                {user.first_name.charAt(0)}{user.last_name.charAt(0)}
                              </div>
                            </div>
                            <div>
                              <div className="fw-semibold">{user.first_name} {user.last_name}</div>
                              <small className="text-muted text-capitalize">{user.role}</small>
                            </div>
                          </div>
                        </label>
                      </div>
                    </Col>
                ))}
              </div>
              </div>
            </div>
          </Modal.Body>
          
          <Modal.Footer className="border-0 bg-light">
            <div className="d-flex justify-content-between w-100">
              <Button 
                variant="outline-secondary" 
                onClick={() => setShowModal(false)}
                className="px-4 py-2"
              >
                <i className="fas fa-times me-2"></i>
                Cancel
              </Button>
              <Button 
                type="submit" 
                variant="primary"
                className="px-4 py-2"
              >
                <i className="fas fa-save me-2"></i>
                {editingProject ? 'Update Project' : 'Create Project'}
              </Button>
            </div>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  );
};

export default Projects;



