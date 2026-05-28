import { LogOut, Menu } from "lucide-react"
import { useNavigate } from "react-router-dom"

export default function TopBar({ onMenu }) {
  const navigate = useNavigate()
  const email = localStorage.getItem("esg_email") || "Signed in"

  function logout() {
    localStorage.removeItem("esg_token")
    localStorage.removeItem("esg_email")
    navigate("/login", { replace: true })
  }

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 lg:px-6">
      <div className="flex items-center gap-3">
        <button type="button" onClick={onMenu} className="rounded-md p-2 text-slate-600 hover:bg-slate-100 lg:hidden" aria-label="Open navigation">
          <Menu className="h-5 w-5" />
        </button>
        <div className="text-base font-semibold text-slate-950">Breathe ESG</div>
      </div>
      <div className="flex items-center gap-3">
        <span className="hidden max-w-[220px] truncate text-sm font-medium text-slate-600 sm:block">{email}</span>
        <button type="button" onClick={logout} className="inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">
          <LogOut className="h-4 w-4" />
          Logout
        </button>
      </div>
    </header>
  )
}
