import { FileClock, Gauge, ListChecks, UploadCloud, ClipboardList } from "lucide-react"
import { NavLink } from "react-router-dom"

const links = [
  { to: "/dashboard", label: "Dashboard", icon: Gauge },
  { to: "/ingest", label: "Ingest Data", icon: UploadCloud },
  { to: "/review", label: "Review", icon: ListChecks },
  { to: "/batches", label: "Batches", icon: ClipboardList },
  { to: "/audit", label: "Audit Log", icon: FileClock },
]

export default function Sidebar({ open, onClose }) {
  return (
    <>
      <div className={`fixed inset-0 z-30 bg-slate-950/40 lg:hidden ${open ? "block" : "hidden"}`} onClick={onClose} />
      <aside className={`fixed inset-y-0 left-0 z-40 w-72 transform bg-sidebar text-white transition-transform lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex h-16 items-center border-b border-white/10 px-6">
          <div className="text-lg font-bold">Breathe ESG</div>
        </div>
        <nav className="space-y-1 px-3 py-5">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition ${
                  isActive ? "bg-white text-sidebar" : "text-slate-300 hover:bg-white/10 hover:text-white"
                }`
              }
            >
              <Icon className="h-5 w-5" />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  )
}
