import React from 'react';
import { Nav } from 'react-bootstrap';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar = () => {
  const location = useLocation();
  const { user } = useAuth();

  const getNavItems = () => {
    const baseItems = [
      { path: '/dashboard', label: '📊 Dashboard', icon: 'fas fa-tachometer-alt' },
      { path: '/projects', label: '📁 Projects', icon: 'fas fa-project-diagram' },
      { path: '/tasks', label: '✅ Tasks', icon: 'fas fa-tasks' },
      { path: '/chatbot', label: '🤖 AI Assistant', icon: 'fas fa-robot' },
    ];

    // Admin can see all items plus admin dashboard
    if (user?.role === 'admin') {
      return [
        ...baseItems,
        { path: '/admin-dashboard', label: '👑 Admin Panel', icon: 'fas fa-crown' }
      ];
    }

    // Manager can see all items
    if (user?.role === 'manager') {
      return baseItems;
    }

    // Interns see limited items
    return baseItems.filter(item => 
      item.path === '/dashboard' || 
      item.path === '/tasks' || 
      item.path === '/chatbot'
    );
  };

  const navItems = getNavItems();

  return (
    <div className="sidebar position-fixed d-flex flex-column" style={{ width: '280px', zIndex: 1000 }}>
      <Nav className="flex-column mt-3">
        {navItems.map((item) => (
          <Nav.Link
            key={item.path}
            href={item.path}
            className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
          >
            <i className={`${item.icon} me-2`}></i>
            {item.label}
          </Nav.Link>
        ))}
      </Nav>
      
      <div className="mt-auto p-3">
        <div className="text-muted small">
          <div>Role: <strong>{user?.role?.charAt(0).toUpperCase() + user?.role?.slice(1)}</strong></div>
          <div>Welcome, {user?.first_name || user?.username}!</div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;



