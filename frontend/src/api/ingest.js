import client from "./client"

export function getBatches() {
  return client.get("/api/ingest/batches/").then((response) => response.data)
}

export function getBatch(batchId) {
  return client.get(`/api/ingest/batches/${batchId}/`).then((response) => response.data)
}

export function uploadFile(sourceType, file) {
  const formData = new FormData()
  formData.append("source_type", sourceType)
  formData.append("file", file)
  return client.post("/api/ingest/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }).then((response) => response.data)
}
