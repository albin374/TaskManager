import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Spinner, Alert } from 'react-bootstrap';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const Dashboard = () => {
  const [projectStats, setProjectStats] = useState(null);
  const [taskStats, setTaskStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState(null);
  const { user } = useAuth();
  const wsRef = useRef(null);

  useEffect(() => {
    fetchDashboardData();
    setupWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [user]);

  const setupWebSocket = () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('token');
      if (!token) return;
      
      const wsUrl = `ws://localhost:8000/ws/tasks/?token=${token}`;
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
      };
      
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'task_notification') {
          setNotification({
            message: data.message,
            type: 'info',
            show: true
          });
          
          // Auto-hide notification after 5 seconds
          setTimeout(() => {
            setNotification(prev => ({ ...prev, show: false }));
          }, 5000);
          
          // Refresh dashboard data
          fetchDashboardData();
        }
      };
      
      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
      };
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Error setting up WebSocket:', error);
    }
  };

  const fetchDashboardData = async () => {
    try {
      console.log('Fetching dashboard data for user:', user?.username);
      
      const [projectResponse, taskResponse] = await Promise.all([
        axios.get('/api/projects/analytics/'),
        axios.get('/api/tasks/analytics/')
      ]);
      
      console.log('Project analytics response:', projectResponse.data);
      console.log('Task analytics response:', taskResponse.data);
      
      // Ensure we have valid data even if empty
      setProjectStats(projectResponse.data || {});
      setTaskStats(taskResponse.data || {});
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      console.error('Error details:', error.response?.data);
      
      // Set default empty data on error
      setProjectStats({});
      setTaskStats({});
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
        <Spinner animation="border" variant="primary" />
      </div>
    );
  }

  const projectStatusData = {
    labels: projectStats?.status_distribution?.map(item => item.status) || [],
    datasets: [{
      data: projectStats?.status_distribution?.map(item => item.count) || [],
      backgroundColor: [
        '#6f42c1',
        '#0d6efd',
        '#fd7e14',
        '#198754',
        '#dc3545'
      ],
      borderWidth: 2,
      borderColor: '#fff'
    }]
  };

  const taskStatusData = {
    labels: taskStats?.status_distribution?.map(item => item.status) || [],
    datasets: [{
      data: taskStats?.status_distribution?.map(item => item.count) || [],
      backgroundColor: [
        '#6c757d',
        '#fd7e14',
        '#ffc107',
        '#198754',
        '#dc3545'
      ],
      borderWidth: 2,
      borderColor: '#fff'
    }]
  };

  const workloadData = {
    labels: taskStats?.workload_distribution?.map(item => item.assigned_to__username) || [],
    datasets: [{
      label: 'Tasks Assigned',
      data: taskStats?.workload_distribution?.map(item => item.count) || [],
      backgroundColor: 'rgba(111, 66, 193, 0.8)',
      borderColor: 'rgba(111, 66, 193, 1)',
      borderWidth: 1
    }]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  };

  return (
    <div className="fade-in">
      {/* Notification */}
      {notification && notification.show && (
        <Alert 
          variant={notification.type} 
          dismissible 
          onClose={() => setNotification(prev => ({ ...prev, show: false }))}
          className="mb-3"
        >
          <i className="fas fa-bell me-2"></i>
          {notification.message}
        </Alert>
      )}
      
      <div className="dashboard-header">
        <h1 className="dashboard-title">Dashboard</h1>
        <p className="dashboard-subtitle">
          Welcome back, {user?.first_name || user?.username}! Here's your overview.
        </p>
        <div className="d-flex justify-content-end">
          <button 
            className="btn btn-outline-primary" 
            onClick={fetchDashboardData}
            disabled={loading}
          >
            <i className="fas fa-sync-alt me-2"></i>
            Refresh Data
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="dashboard-card text-center">
            <Card.Body>
              <Card.Title>{projectStats?.total_projects || 0}</Card.Title>
              <Card.Text>Total Projects</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="dashboard-card text-center">
            <Card.Body>
              <Card.Title>{projectStats?.active_projects || 0}</Card.Title>
              <Card.Text>Active Projects</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="dashboard-card text-center">
            <Card.Body>
              <Card.Title>{taskStats?.total_tasks || 0}</Card.Title>
              <Card.Text>Total Tasks</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="dashboard-card text-center">
            <Card.Body>
              <Card.Title>{taskStats?.completion_rate || 0}%</Card.Title>
              <Card.Text>Completion Rate</Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row>
        <Col md={6}>
          <div className="chart-container mb-4">
            <h5 className="chart-title">Project Status Distribution</h5>
            <Doughnut data={projectStatusData} options={chartOptions} />
          </div>
        </Col>
        <Col md={6}>
          <div className="chart-container mb-4">
            <h5 className="chart-title">Task Status Distribution</h5>
            <Doughnut data={taskStatusData} options={chartOptions} />
          </div>
        </Col>
      </Row>

      <Row>
        <Col md={12}>
          <div className="chart-container">
            <h5 className="chart-title">Workload Distribution</h5>
            <Bar data={workloadData} options={chartOptions} />
          </div>
        </Col>
      </Row>

      {/* Quick Stats */}
      <Row className="mt-4">
        <Col md={4}>
          <div className="quick-stat-card">
            <div className="quick-stat-number text-success">{taskStats?.completed_tasks || 0}</div>
            <div className="quick-stat-label">Completed Tasks</div>
          </div>
        </Col>
        <Col md={4}>
          <div className="quick-stat-card">
            <div className="quick-stat-number text-warning">{taskStats?.in_progress_tasks || 0}</div>
            <div className="quick-stat-label">In Progress</div>
          </div>
        </Col>
        <Col md={4}>
          <div className="quick-stat-card">
            <div className="quick-stat-number text-danger">{taskStats?.overdue_tasks || 0}</div>
            <div className="quick-stat-label">Overdue Tasks</div>
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;



