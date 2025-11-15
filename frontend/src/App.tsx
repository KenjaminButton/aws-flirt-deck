
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './components/auth/LoginPage';
import CallbackPage from './pages/CallbackPage';
import DashboardPage from './pages/DashboardPage';
import QuestionsPage from './pages/QuestionsPage';
import ConnectionsPage from './pages/ConnectionsPage';
import ConnectionDetailPage from './pages/ConnectionDetailPage';
import SettingsPage from './pages/SettingsPage';
import BillingPage from './pages/BillingPage';
import BillingSuccessPage from './pages/BillingSuccessPage';
import BillingCancelPage from './pages/BillingCancelPage';
import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer'; 



const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  // Get auth state from context
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-500"></div>
      </div>
    );
  }
  
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};


const AppContent = () => {
  return (
    <Router>
      <Routes>

        <Route path="/" element={<Navigate to="/login" replace />} />
        
        <Route path="/login" element={<LoginPage />} />
        
        <Route path="/auth/callback" element={<CallbackPage />} />
        
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Navbar />
              <DashboardPage />
              <Footer />  
            </ProtectedRoute>
          }
        />
        
        <Route 
          path="/questions" 
          element={
            <ProtectedRoute>
              <Navbar />
              <QuestionsPage />
              <Footer />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/connections" 
          element={
            <ProtectedRoute>
              <Navbar />
              <ConnectionsPage />
              <Footer />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/connections/:connectionId" 
          element={
            <ProtectedRoute>
              <Navbar />
              <ConnectionDetailPage />
              <Footer />
            </ProtectedRoute>
          } 
        />

        <Route path="/settings" element={
          <ProtectedRoute>
            <Navbar />
            <SettingsPage />
            <Footer />
          </ProtectedRoute>
        } />

        <Route path="/billing" element={
          <ProtectedRoute>
            <Navbar />
            <BillingPage />
            <Footer />
          </ProtectedRoute>
        } />

        <Route path="/billing/success" element={
          <ProtectedRoute>
            <BillingSuccessPage />
          </ProtectedRoute>
        } />

        <Route path="/billing/cancel" element={
          <ProtectedRoute>
            <BillingCancelPage />
          </ProtectedRoute>
        } />


        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
};


function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;



