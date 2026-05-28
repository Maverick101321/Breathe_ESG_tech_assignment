import { useState } from "react"
import { Leaf } from "lucide-react"
import { useMutation } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"
import { login } from "../api/auth"

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const mutation = useMutation({
    mutationFn: () => login(email, password),
    onSuccess: (response) => {
      localStorage.setItem("esg_token", response.data.token)
      localStorage.setItem("esg_email", email)
      navigate("/dashboard", { replace: true })
    },
  })

  function handleSubmit(event) {
    event.preventDefault()
    mutation.mutate()
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <div className="mb-8 flex items-center gap-3">
          <div className="rounded-lg bg-green-50 p-2 text-green-700">
            <Leaf className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-950">Breathe ESG</h1>
            <p className="text-sm text-slate-500">Sign in to continue</p>
          </div>
        </div>

        {mutation.isError ? (
          <div className="mb-4 rounded-md bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
            Unable to sign in. Check your email and password.
          </div>
        ) : null}

        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block">
            <span className="text-sm font-semibold text-slate-700">Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100"
              required
            />
          </label>
          <label className="block">
            <span className="text-sm font-semibold text-slate-700">Password</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100"
              required
            />
          </label>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full rounded-md bg-green-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {mutation.isPending ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  )
}
