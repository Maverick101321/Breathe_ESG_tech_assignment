import { useState } from "react"
import { Fragment } from "react"
import { useQuery } from "@tanstack/react-query"
import { ChevronDown, ChevronRight } from "lucide-react"
import { getBatch, getBatches } from "../api/ingest"
import ScopeBadge from "../components/ScopeBadge"
import StatusBadge from "../components/StatusBadge"
import Table from "../components/Table"

function formatDate(value) {
  return value ? new Date(value).toLocaleString() : "-"
}

function BatchRows({ batchId }) {
  const batch = useQuery({ queryKey: ["batch", batchId], queryFn: () => getBatch(batchId) })

  if (batch.isLoading) return <div className="p-4 text-sm text-slate-500">Loading batch rows...</div>
  if (batch.isError) return <div className="p-4 text-sm font-medium text-red-700">Unable to load batch detail.</div>

  return (
    <div className="space-y-4 p-4">
      {batch.data.entries?.length ? (
        <Table columns={["Date", "Category", "Scope", "Description", "Original", "CO2e (kg)", "Status"]}>
          {batch.data.entries.map((entry) => (
            <tr key={entry.id} className="odd:bg-white even:bg-slate-50">
              <td className="px-4 py-3 text-slate-600">{formatDate(entry.activity_date)}</td>
              <td className="px-4 py-3 font-medium text-slate-900">{entry.category}</td>
              <td className="px-4 py-3"><ScopeBadge value={entry.scope} /></td>
              <td className="max-w-lg px-4 py-3 text-slate-600">{entry.description}</td>
              <td className="px-4 py-3 text-slate-600">{entry.original_value} {entry.original_unit}</td>
              <td className="px-4 py-3 text-slate-600">{Number(entry.co2e_kg).toFixed(2)}</td>
              <td className="px-4 py-3"><StatusBadge value={entry.review_status?.status} /></td>
            </tr>
          ))}
        </Table>
      ) : null}
      {batch.data.error_rows?.length ? (
        <Table columns={["Row", "Parse Error"]}>
          {batch.data.error_rows.map((row) => (
            <tr key={row.id} className="bg-red-50 text-red-800">
              <td className="px-4 py-3 font-semibold">{row.row_number}</td>
              <td className="px-4 py-3">{row.parse_error}</td>
            </tr>
          ))}
        </Table>
      ) : null}
    </div>
  )
}

export default function Batches() {
  const [expanded, setExpanded] = useState(null)
  const batches = useQuery({ queryKey: ["batches"], queryFn: getBatches })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950">Batches</h1>
        <p className="mt-1 text-sm text-slate-500">Inspect uploaded files and their normalized rows.</p>
      </div>

      {batches.isError ? <div className="rounded-md bg-red-50 px-4 py-3 text-sm font-medium text-red-700">Unable to load batches.</div> : null}

      {batches.isLoading ? (
        <div className="h-96 animate-pulse rounded-lg bg-slate-200" />
      ) : (
        <div className="overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-slate-200">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                {["", "Source Type", "Filename", "Uploaded At", "Rows", "Errors", "Status"].map((column) => (
                  <th key={column} className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">{column}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {batches.data.map((batch) => (
                <Fragment key={batch.id}>
                  <tr key={batch.id} className="odd:bg-white even:bg-slate-50 hover:bg-green-50/50">
                    <td className="px-4 py-3">
                      <button type="button" onClick={() => setExpanded(expanded === batch.id ? null : batch.id)} className="rounded-md p-1 text-slate-600 hover:bg-slate-100" aria-label="Expand batch">
                        {expanded === batch.id ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
                      </button>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{batch.source_type.replaceAll("_", " ")}</td>
                    <td className="px-4 py-3 font-medium text-slate-900">{batch.filename}</td>
                    <td className="px-4 py-3 text-slate-600">{formatDate(batch.uploaded_at)}</td>
                    <td className="px-4 py-3 text-slate-600">{batch.row_count}</td>
                    <td className="px-4 py-3 text-slate-600">{batch.error_count}</td>
                    <td className="px-4 py-3"><StatusBadge value={batch.status} /></td>
                  </tr>
                  {expanded === batch.id ? (
                    <tr key={`${batch.id}-detail`}>
                      <td colSpan="7" className="bg-slate-50 p-0"><BatchRows batchId={batch.id} /></td>
                    </tr>
                  ) : null}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
