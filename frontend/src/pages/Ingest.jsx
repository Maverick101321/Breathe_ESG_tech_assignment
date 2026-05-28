import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { Database, Plane, PlugZap } from "lucide-react"
import { uploadFile } from "../api/ingest"

const sources = [
  {
    title: "SAP Fuel & Procurement",
    sourceType: "sap_fuel_procurement",
    description: "CSV export with posting date, plant, material, movement type, quantity, UOM, cost center, and vendor.",
    sample: "sap_sample.csv",
    icon: Database,
  },
  {
    title: "Utility Electricity",
    sourceType: "utility_electricity",
    description: "CSV with meter or consumer number, billing period, consumption, unit, site name, and tariff code.",
    sample: "utility_sample.csv",
    icon: PlugZap,
  },
  {
    title: "Corporate Travel",
    sourceType: "corporate_travel",
    description: "CSV export with employee, travel date, airfare category, airport codes, class, distance, and vendor.",
    sample: "travel_sample.csv",
    icon: Plane,
  },
]

export default function Ingest() {
  const [files, setFiles] = useState({})
  const [result, setResult] = useState(null)

  const mutation = useMutation({
    mutationFn: ({ sourceType, file }) => uploadFile(sourceType, file),
    onSuccess: setResult,
  })

  function upload(sourceType) {
    if (!files[sourceType]) return
    mutation.mutate({ sourceType, file: files[sourceType] })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950">Ingest Data</h1>
        <p className="mt-1 text-sm text-slate-500">Upload CSV exports from source systems.</p>
      </div>

      {mutation.isError ? (
        <div className="rounded-md bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
          {mutation.error.response?.data?.detail || "Upload failed."}
        </div>
      ) : null}

      {result ? (
        <div className="rounded-md bg-green-50 px-4 py-3 text-sm text-green-800">
          Uploaded batch <span className="font-semibold">{result.batch_id}</span>. Rows ingested: {result.row_count}. Errors: {result.error_count}. Status: {result.status}.
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-3">
        {sources.map(({ title, sourceType, description, sample, icon: Icon }) => (
          <section key={sourceType} className="rounded-lg bg-white p-5 shadow-sm ring-1 ring-slate-200">
            <div className="mb-4 flex items-center gap-3">
              <div className="rounded-lg bg-green-50 p-2 text-green-700">
                <Icon className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-bold text-slate-950">{title}</h2>
            </div>
            <p className="min-h-20 text-sm leading-6 text-slate-600">{description}</p>
            <div className="mt-4 text-sm">
              <span className="font-semibold text-slate-700">Sample:</span>{" "}
              <a className="text-blue-600 hover:underline" href={`/sample_data/${sample}`} target="_blank" rel="noreferrer">{sample}</a>
            </div>
            <input
              type="file"
              accept=".csv"
              onChange={(event) => setFiles((current) => ({ ...current, [sourceType]: event.target.files?.[0] }))}
              className="mt-5 block w-full text-sm text-slate-700 file:mr-4 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-slate-700 hover:file:bg-slate-200"
            />
            <button
              type="button"
              onClick={() => upload(sourceType)}
              disabled={!files[sourceType] || mutation.isPending}
              className="mt-4 w-full rounded-md bg-green-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {mutation.isPending ? "Uploading..." : "Upload"}
            </button>
          </section>
        ))}
      </div>
    </div>
  )
}
