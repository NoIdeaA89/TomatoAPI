import { Routes, Route, Navigate } from "react-router-dom"
import PrivateRoute from "./routes/PrivateRoute.jsx"
import PublicOnlyRoute from "./routes/PublicOnlyRoute.jsx"
import AppLayout from "./components/layout/AppLayout.jsx"
import LoginPage from "./pages/LoginPage.jsx"
import RegisterPage from "./pages/RegisterPage.jsx"
import DashboardPage from "./pages/DashboardPage.jsx"
import PlantacionesPage from "./pages/PlantacionesPage.jsx"
import PlantacionFormPage from "./pages/PlantacionFormPage.jsx"
import PlantacionDetailPage from "./pages/PlantacionDetailPage.jsx"
import NotFoundPage from "./pages/NotFoundPage.jsx"

export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicOnlyRoute>
            <LoginPage />
          </PublicOnlyRoute>
        }
      />
      <Route
        path="/registro"
        element={
          <PublicOnlyRoute>
            <RegisterPage />
          </PublicOnlyRoute>
        }
      />

      <Route
        element={
          <PrivateRoute>
            <AppLayout />
          </PrivateRoute>
        }
      >
        <Route path="/" element={<DashboardPage />} />
        <Route path="/plantaciones" element={<PlantacionesPage />} />
        <Route path="/plantaciones/nueva" element={<PlantacionFormPage />} />
        <Route path="/plantaciones/:id" element={<PlantacionDetailPage />} />
        <Route path="/plantaciones/:id/editar" element={<PlantacionFormPage />} />
      </Route>

      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  )
}
