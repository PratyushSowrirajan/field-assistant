import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "@/components/Layout";
import { useAuth } from "@/hooks/useAuth";
import AlertsPage from "@/pages/AlertsPage";
import FieldDetailPage from "@/pages/FieldDetailPage";
import FieldsPage from "@/pages/FieldsPage";
import HomePage from "@/pages/HomePage";
import InsightsPage from "@/pages/InsightsPage";
import LiveRoverPage from "@/pages/LiveRoverPage";
import LoginPage from "@/pages/LoginPage";
import NewFieldPage from "@/pages/NewFieldPage";
import RegisterPage from "@/pages/RegisterPage";
// Isolated, removable feature — see src/features/leaf-check/README.md
import LeafCheckPage from "@/features/leaf-check/LeafCheckPage";

function Protected({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const hasToken = !!localStorage.getItem("sfa_token");

  if (!hasToken) return <Navigate to="/login" replace />;
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-cream text-forest">
        Loading your fields...
      </div>
    );
  }
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        element={
          <Protected>
            <Layout />
          </Protected>
        }
      >
        <Route path="/" element={<HomePage />} />
        <Route path="/fields" element={<FieldsPage />} />
        <Route path="/fields/new" element={<NewFieldPage />} />
        <Route path="/fields/:fieldId" element={<FieldDetailPage />} />
        <Route path="/live" element={<LiveRoverPage />} />
        <Route path="/insights" element={<InsightsPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        {/* Isolated, removable feature — see src/features/leaf-check/README.md */}
        <Route path="/leaf-check" element={<LeafCheckPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
