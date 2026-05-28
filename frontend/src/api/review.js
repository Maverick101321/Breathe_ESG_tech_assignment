import client from "./client"

export function getDashboard() {
  return client.get("/api/review/dashboard/").then((response) => response.data)
}

export function getEntries(params = {}) {
  return client.get("/api/review/entries/", { params }).then((response) => response.data)
}

export function submitReviewAction(entryId, action, reason = "") {
  return client.post(`/api/review/entries/${entryId}/action/`, { action, reason }).then((response) => response.data)
}

export function getAuditLogs(params = {}) {
  return client.get("/api/review/audit/", { params }).then((response) => response.data)
}
