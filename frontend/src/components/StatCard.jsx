export default function StatCard({ label, value, icon: Icon, tone = "green" }) {
  const tones = {
    green: "bg-green-50 text-green-700",
    amber: "bg-amber-50 text-amber-700",
    blue: "bg-blue-50 text-blue-700",
    red: "bg-red-50 text-red-700",
  }

  return (
    <div className="rounded-lg bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-3xl font-bold tracking-normal text-slate-950">{value}</div>
          <div className="mt-1 text-sm font-medium text-slate-500">{label}</div>
        </div>
        {Icon ? (
          <div className={`rounded-lg p-2.5 ${tones[tone] || tones.green}`}>
            <Icon className="h-5 w-5" />
          </div>
        ) : null}
      </div>
    </div>
  )
}
