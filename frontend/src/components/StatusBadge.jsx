const statusStyles = {
  pending: "bg-slate-100 text-slate-700 ring-slate-200",
  flagged: "bg-amber-100 text-amber-800 ring-amber-200",
  approved: "bg-green-100 text-green-800 ring-green-200",
  rejected: "bg-red-100 text-red-800 ring-red-200",
  processing: "bg-blue-100 text-blue-800 ring-blue-200",
  complete: "bg-green-100 text-green-800 ring-green-200",
  failed: "bg-red-100 text-red-800 ring-red-200",
  uploaded: "bg-blue-100 text-blue-800 ring-blue-200",
  parsed: "bg-cyan-100 text-cyan-800 ring-cyan-200",
  edited: "bg-violet-100 text-violet-800 ring-violet-200",
  locked: "bg-slate-900 text-white ring-slate-900",
}

export default function StatusBadge({ value }) {
  const label = value || "unknown"
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold capitalize ring-1 ${statusStyles[label] || "bg-slate-100 text-slate-700 ring-slate-200"}`}>
      {label.replaceAll("_", " ")}
    </span>
  )
}
