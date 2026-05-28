import { useQuery } from "@tanstack/react-query"
import { AlertTriangle, CheckCircle2, Clock3, Factory } from "lucide-react"
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { getBatches } from "../api/ingest"
import { getDashboard, getEntries } from "../api/review"
import StatCard from "../components/StatCard"
import StatusBadge from "../components/StatusBadge"
import Table from "../components/Table"

function formatDate(value) {
  return value ? new Date(value).toLocaleString() : "-"
}

function Skeleton() {
  return <div className="h-32 animate-pulse rounded-lg bg-slate-200" />
}

export default function Dashboard() {
  const dashboard = useQuery({ queryKey: ["dashboard"], queryFn: getDashboard })
  const batches = useQuery({ queryKey: ["batches"], queryFn: getBatches })
  const entries = useQuery({ queryKey: ["dashboard-entries"], queryFn: () => getEntries({ page: 1 }) })

  const rows = entries.data?.results || []
  const countsByScope = ["scope_1", "scope_2", "scope_3"].map((scope) => ({
    scope: scope.replace("_", " ").replace(/\b\w/g, (char) => char.toUpperCase()),
    count: rows.filter((entry) => entry.scope === scope).length,
  }))

  if (dashboard.isError || batches.isError) {
    return <div className="rounded-md bg-red-50 px-4 py-3 text-sm font-medium text-red-700">Unable to load dashboard data.</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">Tenant-wide ingestion and review summary.</p>
      </div>

      {dashboard.isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Skeleton />
          <Skeleton />
          <Skeleton />
          <Skeleton />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Total Pending" value={dashboard.data.total_pending} icon={Clock3} tone="blue" />
          <StatCard label="Total Flagged" value={dashboard.data.total_flagged} icon={AlertTriangle} tone="amber" />
          <StatCard label="Total Approved" value={dashboard.data.total_approved} icon={CheckCircle2} tone="green" />
          <StatCard label="Total CO2e Approved" value={`${(Number(dashboard.data.total_co2e_approved || 0) / 1000).toFixed(2)} t`} icon={Factory} tone="red" />
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[1fr_1.4fr]">
        <section className="rounded-lg bg-white p-5 shadow-sm ring-1 ring-slate-200">
          <h2 className="text-base font-bold text-slate-950">Breakdown by Scope</h2>
          <div className="mt-4 h-72">
            {entries.isLoading ? (
              <div className="h-full animate-pulse rounded-lg bg-slate-100" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={countsByScope}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="scope" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#22c55e" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </section>

        <section>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-950">Recent Batches</h2>
          </div>
          {batches.isLoading ? (
            <div className="h-72 animate-pulse rounded-lg bg-slate-200" />
          ) : (
            <Table columns={["Filename", "Source Type", "Uploaded At", "Rows", "Errors", "Status"]}>
              {batches.data.slice(0, 5).map((batch) => (
                <tr key={batch.id} className="odd:bg-white even:bg-slate-50 hover:bg-green-50/50">
                  <td className="px-4 py-3 font-medium text-slate-900">{batch.filename}</td>
                  <td className="px-4 py-3 text-slate-600">{batch.source_type.replaceAll("_", " ")}</td>
                  <td className="px-4 py-3 text-slate-600">{formatDate(batch.uploaded_at)}</td>
                  <td className="px-4 py-3 text-slate-600">{batch.row_count}</td>
                  <td className="px-4 py-3 text-slate-600">{batch.error_count}</td>
                  <td className="px-4 py-3"><StatusBadge value={batch.status} /></td>
                </tr>
              ))}
            </Table>
          )}
        </section>
      </div>
    </div>
  )
}
