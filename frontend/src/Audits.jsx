import React, { useState, useEffect } from "react";

function Audits({ token }) {
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
    fetch(`${API_URL}/audits?token=${token}`)
      .then(res => res.json())
      .then(data => {
        if (data.audits) setAudits(data.audits);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [token]);

  if (loading) return <div style={{ color: "var(--text-muted)", fontSize: "14px" }}>Loading audit logs...</div>;

  return (
    <div style={{
      background: "var(--bg-primary)", padding: "20px", borderRadius: "12px",
      border: "1px solid var(--border)", boxShadow: "0 4px 6px rgba(0,0,0,0.02)", width: "100%", marginTop: "24px"
    }}>
      <h3 style={{ fontSize: "15px", fontWeight: "600", color: "var(--text-primary)", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
        <span>📊</span> Security Audit Logs (SIEM)
      </h3>
      
      {audits.length === 0 ? (
        <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>No audit logs found.</p>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px", textAlign: "left" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--text-muted)" }}>
                <th style={{ padding: "10px 8px", fontWeight: "600" }}>Timestamp</th>
                <th style={{ padding: "10px 8px", fontWeight: "600" }}>User</th>
                <th style={{ padding: "10px 8px", fontWeight: "600" }}>Action</th>
                <th style={{ padding: "10px 8px", fontWeight: "600" }}>Status</th>
                <th style={{ padding: "10px 8px", fontWeight: "600" }}>Details</th>
              </tr>
            </thead>
            <tbody>
              {audits.map((log, idx) => (
                <tr key={idx} style={{ borderBottom: "1px solid var(--border)" }}>
                  <td style={{ padding: "10px 8px", color: "var(--text-secondary)", whiteSpace: "nowrap" }}>
                    {new Date(log.timestamp.endsWith('Z') ? log.timestamp : log.timestamp + 'Z').toLocaleString()}
                  </td>
                  <td style={{ padding: "10px 8px", color: "var(--text-primary)", fontWeight: "500" }}>{log.username}</td>
                  <td style={{ padding: "10px 8px", color: "var(--text-secondary)" }}>{log.action}</td>
                  <td style={{ padding: "10px 8px" }}>
                    <span style={{
                      padding: "4px 8px", borderRadius: "4px", fontSize: "11px", fontWeight: "600",
                      background: log.status === "BLOCKED" ? "var(--danger-light)" : "var(--success-light)",
                      color: log.status === "BLOCKED" ? "#ef4444" : "#10b981"
                    }}>
                      {log.status}
                    </span>
                  </td>
                  <td style={{ padding: "10px 8px", color: "var(--text-secondary)", maxWidth: "250px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={log.details}>
                    {log.details}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Audits;
