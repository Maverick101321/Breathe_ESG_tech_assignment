const scopeStyles = {
  scope_1: "bg-green-100 text-green-800 ring-green-200",
  scope_2: "bg-amber-100 text-amber-800 ring-amber-200",
  scope_3: "bg-blue-100 text-blue-800 ring-blue-200",
}

const labels = {
  scope_1: "Scope 1",
  scope_2: "Scope 2",
  scope_3: "Scope 3",
}

export default function ScopeBadge({ value }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${scopeStyles[value] || "bg-slate-100 text-slate-700 ring-slate-200"}`}>
      {labels[value] || value || "Unknown"}
    </span>
  )
}
