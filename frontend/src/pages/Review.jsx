import { useMemo, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Check, Flag, Lock, X } from "lucide-react"
import { getEntries, submitReviewAction } from "../api/review"
import ScopeBadge from "../components/ScopeBadge"
import StatusBadge from "../components/StatusBadge"
import Table from "../components/Table"

const sourceTypes = ["sap_fuel_procurement", "utility_electricity", "corporate_travel"]

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString() : "-"
}

function EntryActionForm({ action, onSubmit, onCancel, pending }) {
  const [reason, setReason] = useState("")
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        onSubmit(reason)
      }}
      className="flex min-w-56 items-center gap-2"
    >
      <input
        value={reason}
        onChange={(event) => setReason(event.target.value)}
        placeholder={action === "flag" ? "Flag reason" : "Rejection reason"}
        className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-xs outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-100"
        required
      />
      <button type="submit" disabled={pending} className="rounded-md bg-slate-900 px-2 py-1.5 text-xs font-semibold text-white">Save</button>
      <button type="button" onClick={onCancel} className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100" aria-label="Cancel">
        <X className="h-4 w-4" />
      </button>
    </form>
  )
}

export default function Review() {
  const queryClient = useQueryClient()
  const [filters, setFilters] = useState({ status: "", scope: "", source_type: "" })
  const [page, setPage] = useState(1)
  const [selected, setSelected] = useState([])
  const [inlineAction, setInlineAction] = useState(null)

  const params = useMemo(() => {
    const next = { page }
    Object.entries(filters).forEach(([key, value]) => {
      if (value) next[key] = value
    })
    return next
  }, [filters, page])

  const entries = useQuery({ queryKey: ["entries", params], queryFn: () => getEntries(params) })

  const actionMutation = useMutation({
    mutationFn: ({ entryId, action, reason }) => submitReviewAction(entryId, action, reason),
    onSuccess: () => {
      setInlineAction(null)
      setSelected([])
      queryClient.invalidateQueries({ queryKey: ["entries"] })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })

  const rows = entries.data?.results || []
  const selectedPendingRows = rows.filter((row) => selected.includes(row.id) && row.review_status?.status === "pending")

  function updateFilter(key, value) {
    setPage(1)
    setFilters((current) => ({ ...current, [key]: value }))
  }

  function toggleSelected(entryId) {
    setSelected((current) => (current.includes(entryId) ? current.filter((id) => id !== entryId) : [...current, entryId]))
  }

  async function approveSelected() {
    await Promise.all(selectedPendingRows.map((row) => submitReviewAction(row.id, "approve")))
    setSelected([])
    queryClient.invalidateQueries({ queryKey: ["entries"] })
    queryClient.invalidateQueries({ queryKey: ["dashboard"] })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950">Review Entries</h1>
        <p className="mt-1 text-sm text-slate-500">Approve, flag, or reject normalized emissions entries.</p>
      </div>

      {entries.isError || actionMutation.isError ? (
        <div className="rounded-md bg-red-50 px-4 py-3 text-sm font-medium text-red-700">Unable to complete the review request.</div>
      ) : null}

      <div className="rounded-lg bg-white p-4 shadow-sm ring-1 ring-slate-200">
        <div className="grid gap-3 md:grid-cols-4">
          <select value={filters.status} onChange={(event) => updateFilter("status", event.target.value)} className="rounded-md border border-slate-300 px-3 py-2 text-sm">
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="flagged">Flagged</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <select value={filters.scope} onChange={(event) => updateFilter("scope", event.target.value)} className="rounded-md border border-slate-300 px-3 py-2 text-sm">
            <option value="">All scopes</option>
            <option value="scope_1">Scope 1</option>
            <option value="scope_2">Scope 2</option>
            <option value="scope_3">Scope 3</option>
          </select>
          <select value={filters.source_type} onChange={(event) => updateFilter("source_type", event.target.value)} className="rounded-md border border-slate-300 px-3 py-2 text-sm">
            <option value="">All source types</option>
            {sourceTypes.map((source) => <option key={source} value={source}>{source.replaceAll("_", " ")}</option>)}
          </select>
          <button
            type="button"
            onClick={approveSelected}
            disabled={!selectedPendingRows.length}
            className="rounded-md bg-green-600 px-3 py-2 text-sm font-bold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Approve selected
          </button>
        </div>
      </div>

      {entries.isLoading ? (
        <div className="h-96 animate-pulse rounded-lg bg-slate-200" />
      ) : (
        <Table columns={["", "Date", "Category", "Scope", "Description", "Original", "CO2e (kg)", "Status", "Actions"]}>
          {rows.map((entry) => {
            const status = entry.review_status?.status
            const locked = entry.review_status?.is_locked
            return (
              <tr key={entry.id} className="odd:bg-white even:bg-slate-50 hover:bg-green-50/50">
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selected.includes(entry.id)}
                    disabled={status !== "pending"}
                    onChange={() => toggleSelected(entry.id)}
                    className="h-4 w-4 rounded border-slate-300 text-green-600"
                  />
                </td>
                <td className="px-4 py-3 text-slate-600">{formatDate(entry.activity_date)}</td>
                <td className="px-4 py-3 font-medium text-slate-900">{entry.category}</td>
                <td className="px-4 py-3"><ScopeBadge value={entry.scope} /></td>
                <td className="max-w-md px-4 py-3 text-slate-600">{entry.description}</td>
                <td className="px-4 py-3 text-slate-600">{entry.original_value} {entry.original_unit}</td>
                <td className="px-4 py-3 text-slate-600">{Number(entry.co2e_kg).toFixed(2)}</td>
                <td className="px-4 py-3"><StatusBadge value={status} /></td>
                <td className="px-4 py-3">
                  {locked ? (
                    <div className="flex items-center gap-2 text-sm font-semibold text-slate-500">
                      <Lock className="h-4 w-4" />
                      Locked
                    </div>
                  ) : inlineAction?.entryId === entry.id ? (
                    <EntryActionForm
                      action={inlineAction.action}
                      pending={actionMutation.isPending}
                      onCancel={() => setInlineAction(null)}
                      onSubmit={(reason) => actionMutation.mutate({ entryId: entry.id, action: inlineAction.action, reason })}
                    />
                  ) : (
                    <div className="flex flex-wrap items-center gap-2">
                      <button type="button" onClick={() => actionMutation.mutate({ entryId: entry.id, action: "approve" })} className="rounded-md bg-green-600 p-2 text-white hover:bg-green-700" aria-label="Approve">
                        <Check className="h-4 w-4" />
                      </button>
                      <button type="button" onClick={() => setInlineAction({ entryId: entry.id, action: "flag" })} className="rounded-md bg-amber-500 p-2 text-white hover:bg-amber-600" aria-label="Flag">
                        <Flag className="h-4 w-4" />
                      </button>
                      <button type="button" onClick={() => setInlineAction({ entryId: entry.id, action: "reject" })} className="rounded-md bg-red-600 p-2 text-white hover:bg-red-700" aria-label="Reject">
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            )
          })}
        </Table>
      )}

      <div className="flex items-center justify-end gap-3">
        <button type="button" disabled={!entries.data?.previous} onClick={() => setPage((current) => Math.max(1, current - 1))} className="rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 disabled:opacity-50">Previous</button>
        <span className="text-sm font-medium text-slate-600">Page {page}</span>
        <button type="button" disabled={!entries.data?.next} onClick={() => setPage((current) => current + 1)} className="rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 disabled:opacity-50">Next</button>
      </div>
    </div>
  )
}
