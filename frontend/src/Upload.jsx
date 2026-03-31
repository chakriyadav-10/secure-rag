import axios from "axios";
import { useState } from "react";

export default function Upload({ token }) {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const upload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    setStatus(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const res = await axios.post(`${API_URL}/upload`, form, {
        params: { token }
      });
      if (res.data.error) {
        setStatus({ type: "error", msg: res.data.error });
      } else {
        const piiCount = Object.values(res.data.pii_detected || {}).flat().length;
        setStatus({ type: "success", msg: `✅ "${file.name}" stored securely. ${piiCount} PII entities pseudonymized.` });
      }
    } catch (e) {
      setStatus({ type: "error", msg: "Upload failed: " + e.message });
    } finally {
      setLoading(false);
      e.target.value = "";
    }
  };

  return (
    <div>
      <label style={{
        display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
        padding: "32px", border: "2px dashed var(--border)", borderRadius: "14px",
        cursor: "pointer", background: "var(--bg-secondary)", transition: "border-color 0.2s",
        textAlign: "center"
      }}
        onMouseOver={e => e.currentTarget.style.borderColor = "var(--accent)"}
        onMouseOut={e => e.currentTarget.style.borderColor = "var(--border)"}
      >
        <span style={{ fontSize: "32px", marginBottom: "10px" }}>{loading ? "⏳" : "📄"}</span>
        <span style={{ fontSize: "14px", fontWeight: "600", color: "var(--text-primary)", marginBottom: "4px" }}>
          {loading ? "Processing & securing document..." : "Click to upload a document"}
        </span>
        <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
          {loading ? "Applying threat detection, sanitization & pseudonymization" : "Supports PDF and TXT files"}
        </span>
        <input type="file" onChange={upload} style={{ display: "none" }} accept=".pdf,.txt" />
      </label>
      {status && (
        <div style={{
          marginTop: "14px", padding: "12px 16px", borderRadius: "10px", fontSize: "13px",
          background: status.type === "success" ? "rgba(34,197,94,0.1)" : "rgba(239,68,68,0.12)",
          border: `1px solid ${status.type === "success" ? "rgba(34,197,94,0.3)" : "rgba(239,68,68,0.3)"}`,
          color: status.type === "success" ? "#4ade80" : "#f87171"
        }}>
          {status.msg}
        </div>
      )}
    </div>
  );
}