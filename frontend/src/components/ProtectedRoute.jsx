import { Navigate, Outlet } from "react-router-dom"
import Layout from "./Layout"

export default function ProtectedRoute() {
  const token = localStorage.getItem("esg_token")
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return (
    <Layout>
      <Outlet />
    </Layout>
  )
}
