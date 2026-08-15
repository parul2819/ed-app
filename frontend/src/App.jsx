import { Navigate, Route, BrowserRouter, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import ParentAuthPage from "./pages/ParentAuthPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import AddChildPage from "./pages/AddChildPage";
import ChildLoginPage from "./pages/ChildLoginPage";
import TopicSelectPage from "./pages/TopicSelectPage";
import PracticePage from "./pages/PracticePage";
import ProgressPage from "./pages/ProgressPage";

function RootRedirect() {
  const { activeChild, isParentLoggedIn, cachedChildren } = useAuth();
  if (activeChild) return <Navigate to="/topics" replace />;
  if (isParentLoggedIn || cachedChildren.length > 0) {
    return <Navigate to="/children" replace />;
  }
  return <Navigate to="/parent/auth" replace />;
}

function RequireParent({ children }) {
  const { isParentLoggedIn } = useAuth();
  if (!isParentLoggedIn) return <Navigate to="/parent/auth" replace />;
  return children;
}

function RequireChild({ children }) {
  const { activeChild } = useAuth();
  if (!activeChild) return <Navigate to="/children" replace />;
  return children;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="app-shell">
          <Routes>
            <Route path="/" element={<RootRedirect />} />
            <Route path="/parent/auth" element={<ParentAuthPage />} />
            <Route path="/parent/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/parent/reset-password" element={<ResetPasswordPage />} />
            <Route
              path="/parent/reset-password/:token"
              element={<ResetPasswordPage />}
            />
            <Route path="/children" element={<ChildLoginPage />} />
            <Route
              path="/children/add"
              element={
                <RequireParent>
                  <AddChildPage />
                </RequireParent>
              }
            />
            <Route
              path="/topics"
              element={
                <RequireChild>
                  <TopicSelectPage />
                </RequireChild>
              }
            />
            <Route
              path="/practice/:track/:topic"
              element={
                <RequireChild>
                  <PracticePage />
                </RequireChild>
              }
            />
            <Route
              path="/progress"
              element={
                <RequireChild>
                  <ProgressPage />
                </RequireChild>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
