import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { getAuditLogs } from "../api/review"
import StatusBadge from "../components/StatusBadge"
import Table from "../components/Table"

const actions = ["uploaded", "parsed", "edited", "flagged", "approved", "rejected", "locked"]

function formatDate(value) {
  return value ? new Date(value).toLocaleString() : "-"
}

export default function Audit() {
  const [action, setAction] = useState("")
  const logs = useQuery({ queryKey: ["audit", action], queryFn: () => getAuditLogs(action ? { action } : {}) })
  const filtered = action ? (logs.data || []).filter((log) => log.action === action) : logs.data || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950">Audit Log</h1>
        <p className="mt-1 text-sm text-slate-500">Trace uploads, edits, and review decisions.</p>
      </div>

      {logs.isError ? <div className="rounded-md bg-red-50 px-4 py-3 text-sm font-medium text-red-700">Unable to load audit logs.</div> : null}

      <div className="rounded-lg bg-white p-4 shadow-sm ring-1 ring-slate-200">
        <select value={action} onChange={(event) => setAction(event.target.value)} className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm md:w-72">
          <option value="">All actions</option>
          {actions.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
      </div>

      {logs.isLoading ? (
        <div className="h-96 animate-pulse rounded-lg bg-slate-200" />
      ) : (
        <Table columns={["Timestamp", "Actor", "Action", "Target Type", "Target ID", "Notes"]}>
          {filtered.map((log) => (
            <tr key={log.id} className="odd:bg-white even:bg-slate-50 hover:bg-green-50/50">
              <td className="px-4 py-3 text-slate-600">{formatDate(log.timestamp)}</td>
              <td className="px-4 py-3 text-slate-600">{log.actor}</td>
              <td className="px-4 py-3"><StatusBadge value={log.action} /></td>
              <td className="px-4 py-3 text-slate-600">{log.target_type}</td>
              <td className="px-4 py-3 font-mono text-xs text-slate-600">{log.target_id}</td>
              <td className="px-4 py-3 text-slate-600">{log.notes || "-"}</td>
            </tr>
          ))}
        </Table>
      )}
    </div>
  )
}
