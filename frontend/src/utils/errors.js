// Turn any axios/FastAPI error into a readable string.
// FastAPI sends `detail` as a string for HTTPException but as an ARRAY of objects for
// validation errors (422) - rendering that array in JSX crashes React, so flatten it here.
export function getErrorMessage(err, fallback = "Something went wrong. Please try again.") {
  if (!err) return fallback;
  if (!err.response) {
    return err.code === "ECONNABORTED"
      ? "The request timed out. Please try again."
      : "Cannot reach the server. Make sure the backend is running.";
  }
  const detail = err.response.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const msgs = detail.map((d) => {
      const field = Array.isArray(d.loc) ? d.loc.filter((p) => p !== "body").join(".") : "";
      const msg = String(d.msg || "").replace(/^Value error, /, "");
      return field ? `${field}: ${msg}` : msg;
    });
    return msgs.join(" · ") || fallback;
  }
  return fallback;
}
