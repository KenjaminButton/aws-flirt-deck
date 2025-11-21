/**
 * Navbar Component - FIXED VERSION
 * Desktop logout now works properly with correct z-index layering
 */

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: '🏠' },
    { name: 'Questions', path: '/questions', icon: '💬' },
    { name: 'Connections', path: '/connections', icon: '👥' }
  ];

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    setMobileMenuOpen(false);
    setProfileDropdownOpen(false);
    logout();
  };

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-2">
            <span className="text-2xl">💕</span>
            <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              FlirtDecks
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`
                  flex items-center gap-2 px-3 py-2 rounded-lg font-medium transition-colors
                  ${isActive(link.path)
                    ? 'bg-purple-100 text-purple-700'
                    : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
              >
                <span>{link.icon}</span>
                <span>{link.name}</span>
              </Link>
            ))}
          </div>

          {/* Desktop Profile Dropdown */}
          <div className="hidden md:block relative z-50">
            <button
              onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
              className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors relative z-50"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-white font-bold">
                {user?.name?.charAt(0).toUpperCase() || '?'}
              </div>
              <div className="text-left hidden lg:block">
                <p className="text-sm font-medium text-gray-900">{user?.name || 'User'}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
              <span className="text-gray-400">▼</span>
            </button>

            {/* Desktop Dropdown Menu */}
            {profileDropdownOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50">
                <div className="px-4 py-3 border-b border-gray-100">
                  <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                  <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                  <p className="text-xs text-purple-600 font-medium mt-1">
                    {user?.subscription_status === 'free' ? '🆓 Free Tier' : '⭐ Premium'}
                  </p>
                </div>
                
                <Link
                  to="/settings"
                  onClick={() => setProfileDropdownOpen(false)}
                  className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <span>⚙️</span>
                  <span>Settings</span>
                </Link>
                
                <Link
                  to="/billing"
                  onClick={() => setProfileDropdownOpen(false)}
                  className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <span>💳</span>
                  <span>Billing</span>
                </Link>

                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 border-t border-gray-100 mt-2"
                >
                  <span>🚪</span>
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
          >
            <span className="text-2xl">{mobileMenuOpen ? '✕' : '☰'}</span>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white relative z-50">
          {/* User Info Section */}
          <div className="px-4 py-4 bg-gradient-to-r from-purple-50 to-pink-50 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-white font-bold text-lg">
                {user?.name?.charAt(0).toUpperCase() || '?'}
              </div>
              <div>
                <p className="font-medium text-gray-900">{user?.name || 'User'}</p>
                <p className="text-sm text-gray-600">{user?.email}</p>
                <p className="text-xs text-purple-600 font-medium mt-1">
                  {user?.subscription_status === 'free' ? '🆓 Free Tier' : '⭐ Premium'}
                </p>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="py-2">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 font-medium transition-colors
                  ${isActive(link.path)
                    ? 'bg-purple-50 text-purple-700 border-l-4 border-purple-500'
                    : 'text-gray-700 hover:bg-gray-50'
                  }
                `}
              >
                <span className="text-xl">{link.icon}</span>
                <span>{link.name}</span>
              </Link>
            ))}
          </div>

          {/* Profile Actions */}
          <div className="border-t border-gray-200 py-2">
            <Link
              to="/settings"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50"
            >
              <span className="text-xl">⚙️</span>
              <span>Settings</span>
            </Link>
            
            <Link
              to="/billing"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50"
            >
              <span className="text-xl">💳</span>
              <span>Billing</span>
            </Link>

            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-3 text-red-600 hover:bg-red-50 font-medium"
            >
              <span className="text-xl">🚪</span>
              <span>Logout</span>
            </button>
          </div>
        </div>
      )}

      {/* Overlay to close dropdowns - ONLY z-40 */}
      {(mobileMenuOpen || profileDropdownOpen) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setMobileMenuOpen(false);
            setProfileDropdownOpen(false);
          }}
        />
      )}
    </nav>
  );
};

export default Navbar;