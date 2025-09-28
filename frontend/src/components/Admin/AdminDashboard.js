import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Modal, Form, Alert, Badge, Tabs, Tab } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'react-toastify';
import axios from 'axios';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

const AdminDashboard = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    role: 'intern',
    phone_number: '',
    is_active: true
  });

  useEffect(() => {
    if (user && user.role === 'admin') {
      fetchData();
    }
  }, [user]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersRes, projectsRes, analyticsRes, auditRes] = await Promise.all([
        axios.get('/api/admin/users/'),
        axios.get('/api/admin/projects/'),
        axios.get('/api/admin/analytics/'),
        axios.get('/api/admin/audit-logs/')
      ]);
      
      // Handle paginated responses
      setUsers(usersRes.data.results || usersRes.data || []);
      setProjects(projectsRes.data.results || projectsRes.data || []);
      setAnalytics(analyticsRes.data);
      setAuditLogs(auditRes.data.results || auditRes.data || []);
    } catch (error) {
      console.error('Error fetching admin data:', error);
      toast.error('Failed to load admin data');
      // Set empty arrays as fallback
      setUsers([]);
      setProjects([]);
      setAuditLogs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleUserSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingUser) {
        await axios.put(`/api/admin/users/${editingUser.id}/`, formData);
        toast.success('User updated successfully');
      } else {
        await axios.post('/api/admin/users/', formData);
        toast.success('User created successfully');
      }
      setShowUserModal(false);
      setEditingUser(null);
      resetForm();
      fetchData();
    } catch (error) {
      console.error('Error saving user:', error);
      toast.error('Failed to save user');
    }
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      password: '',
      password_confirm: '',
      first_name: user.first_name,
      last_name: user.last_name,
      role: user.role,
      phone_number: user.phone_number || '',
      is_active: user.is_active
    });
    setShowUserModal(true);
  };

  const handleDeleteUser = async () => {
    try {
      await axios.delete(`/api/admin/users/${selectedUser.id}/`);
      toast.success('User deleted successfully');
      setShowDeleteModal(false);
      setSelectedUser(null);
      fetchData();
    } catch (error) {
      console.error('Error deleting user:', error);
      toast.error('Failed to delete user');
    }
  };

  const resetForm = () => {
    setFormData({
      username: '',
      email: '',
      password: '',
      password_confirm: '',
      first_name: '',
      last_name: '',
      role: 'intern',
      phone_number: '',
      is_active: true
    });
  };

  const exportUsersCSV = async () => {
    try {
      const response = await axios.post('/api/admin/export/users-csv/', {}, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `users_export_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Users exported successfully');
    } catch (error) {
      console.error('Error exporting users:', error);
      toast.error('Failed to export users');
    }
  };

  const exportAnalytics = async () => {
    try {
      const response = await axios.post('/api/admin/export/analytics-report/', {}, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `analytics_report_${new Date().toISOString().split('T')[0]}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Analytics exported successfully');
    } catch (error) {
      console.error('Error exporting analytics:', error);
      toast.error('Failed to export analytics');
    }
  };

  const getRoleBadgeVariant = (role) => {
    switch (role) {
      case 'admin': return 'danger';
      case 'manager': return 'warning';
      case 'intern': return 'info';
      default: return 'secondary';
    }
  };

  const getStatusBadgeVariant = (isActive) => {
    return isActive ? 'success' : 'danger';
  };

  // Chart configurations
  const usersByRoleChart = {
    labels: analytics?.users_by_role ? Object.keys(analytics.users_by_role) : [],
    datasets: [{
      data: analytics?.users_by_role ? Object.values(analytics.users_by_role) : [],
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
      borderWidth: 1
    }]
  };

  const projectsByStatusChart = {
    labels: analytics?.projects_by_status ? Object.keys(analytics.projects_by_status) : [],
    datasets: [{
      label: 'Projects',
      data: analytics?.projects_by_status ? Object.values(analytics.projects_by_status) : [],
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'],
      borderWidth: 1
    }]
  };

  const workloadChart = {
    labels: analytics?.workload_distribution ? analytics.workload_distribution.map(w => w.user) : [],
    datasets: [{
      label: 'Total Tasks',
      data: analytics?.workload_distribution ? analytics.workload_distribution.map(w => w.total_tasks) : [],
      backgroundColor: '#36A2EB',
      borderColor: '#36A2EB',
      borderWidth: 1
    }, {
      label: 'Completed Tasks',
      data: analytics?.workload_distribution ? analytics.workload_distribution.map(w => w.completed_tasks) : [],
      backgroundColor: '#4BC0C0',
      borderColor: '#4BC0C0',
      borderWidth: 1
    }]
  };

  if (!user || user.role !== 'admin') {
    return (
      <Container className="mt-5">
        <Alert variant="danger">
          <Alert.Heading>Access Denied</Alert.Heading>
          <p>You don't have permission to access the admin dashboard.</p>
        </Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container className="mt-5">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      <Row>
        <Col>
          <h2 className="mb-4">Admin Dashboard</h2>
        </Col>
      </Row>

      <Tabs defaultActiveKey="overview" className="mb-4">
        <Tab eventKey="overview" title="Overview">
          <Row className="mb-4">
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-primary">{analytics?.total_users || 0}</h3>
                  <p className="text-muted">Total Users</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-success">{analytics?.total_projects || 0}</h3>
                  <p className="text-muted">Total Projects</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-info">{analytics?.total_tasks || 0}</h3>
                  <p className="text-muted">Total Tasks</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-warning">{analytics?.completed_tasks || 0}</h3>
                  <p className="text-muted">Completed Tasks</p>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Card>
                <Card.Header>
                  <h5>Users by Role</h5>
                </Card.Header>
                <Card.Body>
                  <Doughnut data={usersByRoleChart} />
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card>
                <Card.Header>
                  <h5>Projects by Status</h5>
                </Card.Header>
                <Card.Body>
                  <Bar data={projectsByStatusChart} />
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Row className="mt-4">
            <Col>
              <Card>
                <Card.Header>
                  <h5>Workload Distribution</h5>
                </Card.Header>
                <Card.Body>
                  <Bar data={workloadChart} />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>

        <Tab eventKey="users" title="User Management">
          <Row className="mb-3">
            <Col>
              <Button 
                variant="primary" 
                onClick={() => {
                  setEditingUser(null);
                  resetForm();
                  setShowUserModal(true);
                }}
              >
                Add New User
              </Button>
              <Button 
                variant="success" 
                className="ms-2"
                onClick={exportUsersCSV}
              >
                Export CSV
              </Button>
            </Col>
          </Row>

          <Card>
            <Card.Body>
              <Table responsive striped hover>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Full Name</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Projects</th>
                    <th>Tasks</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users && users.length > 0 ? users.map(user => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td>{user.username}</td>
                      <td>{user.email}</td>
                      <td>{user.full_name}</td>
                      <td>
                        <Badge bg={getRoleBadgeVariant(user.role)}>
                          {user.role}
                        </Badge>
                      </td>
                      <td>
                        <Badge bg={getStatusBadgeVariant(user.is_active)}>
                          {user.is_active_display}
                        </Badge>
                      </td>
                      <td>{user.total_projects}</td>
                      <td>{user.total_tasks}</td>
                      <td>
                        <Button 
                          size="sm" 
                          variant="outline-primary" 
                          onClick={() => handleEditUser(user)}
                          className="me-2"
                        >
                          Edit
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline-warning"
                          onClick={async () => {
                            try {
                              const response = await axios.post('/api/admin/users/reset-password/', {
                                user_id: user.id
                              });
                              toast.success(`Password reset for ${user.username}. New password: ${response.data.temporary_password}`);
                            } catch (error) {
                              toast.error('Failed to reset password');
                            }
                          }}
                          className="me-2"
                        >
                          Reset Password
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline-secondary"
                          onClick={async () => {
                            try {
                              await axios.post('/api/admin/users/deactivate/', {
                                user_id: user.id
                              });
                              toast.success(`User ${user.username} deactivated`);
                              fetchData();
                            } catch (error) {
                              toast.error('Failed to deactivate user');
                            }
                          }}
                          className="me-2"
                        >
                          Deactivate
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline-danger"
                          onClick={() => {
                            setSelectedUser(user);
                            setShowDeleteModal(true);
                          }}
                        >
                          Delete
                        </Button>
                      </td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan="9" className="text-center text-muted">
                        No users found
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="projects" title="Project Management">
          <Card>
            <Card.Body>
              <Table responsive striped hover>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Created By</th>
                    <th>Progress</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {projects && projects.length > 0 ? projects.map(project => (
                    <tr key={project.id}>
                      <td>{project.id}</td>
                      <td>{project.title}</td>
                      <td>
                        <Badge bg="info">{project.status}</Badge>
                      </td>
                      <td>
                        <Badge bg="warning">{project.priority}</Badge>
                      </td>
                      <td>{project.created_by_name}</td>
                      <td>
                        <div className="progress" style={{ width: '100px' }}>
                          <div 
                            className="progress-bar" 
                            style={{ width: `${project.completion_percentage}%` }}
                          >
                            {project.completion_percentage}%
                          </div>
                        </div>
                      </td>
                      <td>
                        <Button 
                          size="sm" 
                          variant="outline-danger"
                          onClick={() => {
                            // Handle project deletion
                            toast.info('Project deletion feature coming soon');
                          }}
                        >
                          Delete
                        </Button>
                      </td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan="7" className="text-center text-muted">
                        No projects found
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="audit" title="Audit Logs">
          <Row className="mb-3">
            <Col>
              <Button 
                variant="success"
                onClick={exportAnalytics}
              >
                Export Analytics Report
              </Button>
            </Col>
          </Row>

          <Card>
            <Card.Body>
              <Table responsive striped hover>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Admin</th>
                    <th>Action</th>
                    <th>Target User</th>
                    <th>Description</th>
                    <th>IP Address</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs && auditLogs.length > 0 ? auditLogs.map(log => (
                    <tr key={log.id}>
                      <td>{new Date(log.timestamp).toLocaleString()}</td>
                      <td>{log.admin_username}</td>
                      <td>
                        <Badge bg="info">{log.action}</Badge>
                      </td>
                      <td>{log.target_username || 'N/A'}</td>
                      <td>{log.description}</td>
                      <td>{log.ip_address || 'N/A'}</td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan="6" className="text-center text-muted">
                        No audit logs found
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="system" title="System Control">
          <Row>
            <Col md={6}>
              <Card>
                <Card.Header>
                  <h5>System Health</h5>
                </Card.Header>
                <Card.Body>
                  <Button 
                    variant="info" 
                    onClick={async () => {
                      try {
                        const response = await axios.get('/api/admin/system/health/');
                        toast.success('System health check completed');
                        console.log('System Health:', response.data);
                      } catch (error) {
                        toast.error('Failed to check system health');
                      }
                    }}
                  >
                    Check System Health
                  </Button>
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card>
                <Card.Header>
                  <h5>User Activity</h5>
                </Card.Header>
                <Card.Body>
                  <Button 
                    variant="warning" 
                    onClick={async () => {
                      try {
                        const response = await axios.get('/api/admin/system/user-activity/');
                        toast.success('User activity summary loaded');
                        console.log('User Activity:', response.data);
                      } catch (error) {
                        toast.error('Failed to load user activity');
                      }
                    }}
                  >
                    View User Activity
                  </Button>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Row className="mt-4">
            <Col>
              <Card>
                <Card.Header>
                  <h5>Chatbot Settings</h5>
                </Card.Header>
                <Card.Body>
                  <Button 
                    variant="primary" 
                    onClick={async () => {
                      try {
                        const response = await axios.get('/api/admin/system/chatbot-settings/');
                        toast.success('Chatbot settings loaded');
                        console.log('Chatbot Settings:', response.data);
                      } catch (error) {
                        toast.error('Failed to load chatbot settings');
                      }
                    }}
                  >
                    View Chatbot Settings
                  </Button>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>
      </Tabs>

      {/* User Modal */}
      <Modal show={showUserModal} onHide={() => setShowUserModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>{editingUser ? 'Edit User' : 'Add New User'}</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleUserSubmit}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Username</Form.Label>
                  <Form.Control
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Email</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>First Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Last Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                    required
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Role</Form.Label>
                  <Form.Select
                    name="role"
                    value={formData.role}
                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                  >
                    <option value="intern">Intern</option>
                    <option value="manager">Manager</option>
                    <option value="admin">Admin</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Phone Number</Form.Label>
                  <Form.Control
                    type="text"
                    name="phone_number"
                    value={formData.phone_number}
                    onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>

            {!editingUser && (
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Password</Form.Label>
                    <Form.Control
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      required={!editingUser}
                      minLength={8}
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Confirm Password</Form.Label>
                    <Form.Control
                      type="password"
                      name="password_confirm"
                      value={formData.password_confirm}
                      onChange={(e) => setFormData({...formData, password_confirm: e.target.value})}
                      required={!editingUser}
                      minLength={8}
                    />
                  </Form.Group>
                </Col>
              </Row>
            )}

            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                label="Active"
                name="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowUserModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              {editingUser ? 'Update User' : 'Create User'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Are you sure you want to delete user "{selectedUser?.username}"? This action cannot be undone.
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeleteUser}>
            Delete User
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default AdminDashboard;
