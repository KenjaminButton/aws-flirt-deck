/**
 * App.tsx - Main Application Component
 * 
 * BIG PICTURE:
 * This is the root component of the entire application.
 * It sets up:
 * 1. React Router (navigation between pages)
 * 2. Auth Context Provider (makes auth available everywhere)
 * 3. Route definitions (which URLs show which components)
 * 4. Protected routes (require login to access)
 * 
 * STRUCTURE:
 * <AuthProvider>           ← Wraps everything so auth is available
 *   <Router>               ← Enables routing/navigation
 *     <Routes>             ← Defines which path shows which component
 *       <Route /login>     ← Public route
 *       <Route /callback>  ← Public route
 *       <Route /dashboard> ← Protected route (requires login)
 *     </Routes>
 *   </Router>
 * </AuthProvider>
 * 
 * ANALOGY:
 * Think of this as a building directory:
 * - AuthProvider = Security desk (checks if you belong here)
 * - Router = Elevator system (gets you where you need to go)
 * - Routes = Floor directory (1st floor = login, 2nd floor = dashboard, etc.)
 * - ProtectedRoute = Locked floors (need keycard to access)
 */

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './components/auth/LoginPage';
import CallbackPage from './pages/CallbackPage';
import DashboardPage from './pages/DashboardPage';
/**
 * ProtectedRoute Component
 * 
 * BIG PICTURE:
 * This is a wrapper for routes that require authentication.
 * It checks if the user is logged in:
 * - If YES: Show the requested component
 * - If NO: Redirect to login page
 * 
 * WHY WE NEED THIS:
 * Prevents users from accessing protected pages by typing the URL directly.
 * 
 * Example without protection:
 * User types /dashboard → Sees dashboard even though not logged in → BAD!
 * 
 * Example with protection:
 * User types /dashboard → ProtectedRoute checks auth → Not logged in → Redirect to /login → GOOD!
 * 
 * USAGE:
 * <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
 */
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  // Get auth state from context
  const { isAuthenticated, loading } = useAuth();
  
  /**
   * Show loading spinner while checking authentication
   * 
   * WHY: When app first loads, AuthContext is fetching user profile.
   * We don't know yet if user is logged in or not.
   * 
   * Without this check, user would briefly see login page even if logged in
   * (causes a flash/flicker - bad UX)
   */
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-500"></div>
      </div>
    );
  }
  
  /**
   * Check authentication and render accordingly
   * 
   * If authenticated: Render the protected component (children)
   * If not authenticated: Redirect to login page
   */
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

/**
 * Temporary Dashboard Component
 * 
 * This is a placeholder for Day 10 when we'll build the actual dashboard.
 * For now, it just shows that login worked and provides a logout button.
 */
// const DashboardPlaceholder = () => {
//   const { user, logout } = useAuth();
  
//   return (
//     <div className="min-h-screen bg-gray-100 p-8">
//       <div className="max-w-4xl mx-auto">
//         <div className="bg-white rounded-lg shadow-md p-6">
//           <h1 className="text-3xl font-bold text-gray-800 mb-4">
//             Welcome to FlirtDeck! 🎉
//           </h1>
          
//           <div className="mb-6">
//             <p className="text-gray-600 mb-2">
//               <strong>Email:</strong> {user?.email}
//             </p>
//             <p className="text-gray-600 mb-2">
//               <strong>Name:</strong> {user?.name || 'Not set'}
//             </p>
//             <p className="text-gray-600 mb-2">
//               <strong>Subscription:</strong> {user?.subscription_status}
//             </p>
//           </div>
          
//           <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
//             <p className="text-sm text-blue-700">
//               ✅ <strong>Day 9 Complete!</strong> Authentication is working.
//               <br />
//               📅 <strong>Next:</strong> Day 10 - Build the actual dashboard with navigation.
//             </p>
//           </div>
          
//           <button
//             onClick={logout}
//             className="bg-red-500 text-white font-semibold py-2 px-4 rounded-lg hover:bg-red-600 transition duration-200"
//           >
//             Logout
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

/**
 * AppContent Component
 * 
 * Contains the actual routing logic.
 * Separated from App component because it needs to be inside AuthProvider
 * (to access useAuth hook).
 */
const AppContent = () => {
  return (
    <Router>
      <Routes>
        {/* ============================================
            PUBLIC ROUTES (No authentication required)
            ============================================ */}
        
        {/**
         * Root path: Redirect to login
         * 
         * When user visits http://localhost:5173/, redirect to /login
         * Later, we might make this a landing page instead
         */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        
        {/**
         * Login page: Sign in with Google
         * 
         * Path: /login
         * Anyone can access this (public route)
         */}
        <Route path="/login" element={<LoginPage />} />
        
        {/**
         * OAuth callback page: Handles Google redirect
         * 
         * Path: /auth/callback
         * This is where Cognito sends users after Google OAuth
         * Must be public (user isn't logged in yet when they land here)
         */}
        <Route path="/auth/callback" element={<CallbackPage />} />
        
        {/* ============================================
            PROTECTED ROUTES (Authentication required)
            ============================================ */}
        
        {/**
         * Dashboard: Main app interface
         * 
         * Path: /dashboard
         * Protected route - requires login
         * 
         * For Day 9, this is just a placeholder.
         * On Day 10, we'll replace DashboardPlaceholder with the real Dashboard component.
         */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        
        {/**
         * Catch-all route: 404 Not Found
         * 
         * If user navigates to any undefined path, show 404 or redirect
         * For now, just redirect to login
         * 
         * The * matches any path that hasn't been matched above
         */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
};

/**
 * Main App Component
 * 
 * This is the top-level component that React renders.
 * It wraps everything in AuthProvider so auth state is available everywhere.
 * 
 * STRUCTURE:
 * <AuthProvider>    ← Provides auth to entire app
 *   <AppContent />  ← Contains router and routes
 * </AuthProvider>
 */
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;

/**
 * ============================================
 * HOW THE AUTH FLOW WORKS WITH THESE ROUTES
 * ============================================
 * 
 * SCENARIO 1: New user visits app
 * 1. Browser loads → App renders
 * 2. AuthProvider checks localStorage → No token found
 * 3. Navigate to "/" → Redirects to "/login"
 * 4. LoginPage shows "Sign in with Google" button
 * 5. User clicks → login() in AuthContext redirects to Cognito
 * 6. Cognito → Google → User approves → Cognito redirects to "/auth/callback?code=abc"
 * 7. CallbackPage extracts code, exchanges for tokens, stores in localStorage
 * 8. CallbackPage redirects to "/dashboard"
 * 9. ProtectedRoute checks auth → User is logged in → Shows DashboardPlaceholder
 * 
 * SCENARIO 2: Logged-in user refreshes page
 * 1. Browser loads → App renders
 * 2. AuthProvider checks localStorage → Token found
 * 3. AuthProvider calls /auth/me → Gets user profile
 * 4. User state is set
 * 5. If on /dashboard → ProtectedRoute checks auth → User is logged in → Shows dashboard
 * 6. If on /login → LoginPage checks auth → Redirects to /dashboard
 * 
 * SCENARIO 3: User logs out
 * 1. User clicks "Logout" button
 * 2. logout() in AuthContext clears localStorage
 * 3. User state is set to null
 * 4. Redirects to "/login"
 * 5. If user tries to access "/dashboard" → ProtectedRoute redirects to "/login"
 * 
 * SCENARIO 4: User tries to access protected route without login
 * 1. User types "http://localhost:5173/dashboard" in browser
 * 2. Router matches path to /dashboard route
 * 3. ProtectedRoute checks auth → Not logged in
 * 4. Redirects to "/login"
 */