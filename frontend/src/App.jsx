import { Navigate, Route, Routes } from "react-router-dom"
import ProtectedRoute from "./components/ProtectedRoute"
import Audit from "./pages/Audit"
import Batches from "./pages/Batches"
import Dashboard from "./pages/Dashboard"
import Ingest from "./pages/Ingest"
import Login from "./pages/Login"
import Review from "./pages/Review"

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/ingest" element={<Ingest />} />
        <Route path="/review" element={<Review />} />
        <Route path="/batches" element={<Batches />} />
        <Route path="/audit" element={<Audit />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
