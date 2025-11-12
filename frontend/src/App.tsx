
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './components/auth/LoginPage';
import CallbackPage from './pages/CallbackPage';
import DashboardPage from './pages/DashboardPage';
import QuestionsPage from './pages/QuestionsPage';
import ConnectionsPage from './pages/ConnectionsPage';
import ConnectionDetailPage from './pages/ConnectionDetailPage';
import Navbar from './components/common/Navbar';



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
            </ProtectedRoute>
          }
        />
        
        <Route 
          path="/questions" 
          element={
            <ProtectedRoute>
              <Navbar />
              <QuestionsPage />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/connections" 
          element={
            <ProtectedRoute>
              <Navbar />
              <ConnectionsPage />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/connections/:connectionId" 
          element={
            <ProtectedRoute>
              <Navbar />
              <ConnectionDetailPage />
            </ProtectedRoute>
          } 
        />

        // Add placeholder routes for Settings and Billing
        <Route path="/settings" element={
          <ProtectedRoute>
            <>
              <Navbar />
              <div className="p-8 text-center">
                <h1 className="text-3xl font-bold">⚙️ Settings</h1>
                <p className="text-gray-600 mt-4">Coming soon!</p>
              </div>
            </>
          </ProtectedRoute>
        } />

        <Route path="/billing" element={
          <ProtectedRoute>
            <>
              <Navbar />
              <div className="p-8 text-center">
                <h1 className="text-3xl font-bold">💳 Billing</h1>
                <p className="text-gray-600 mt-4">Coming soon!</p>
              </div>
            </>
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



