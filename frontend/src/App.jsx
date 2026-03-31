import { useState } from "react";
import Login from "./Login";
import Upload from "./Upload";
import Query from "./Query";
import Audits from "./Audits";
import UserManagement from "./UserManagement";

function App() {
  const [token, setToken] = useState("");
  const [role, setRole] = useState("");
  const [username, setUsername] = useState("");
  const [activeTab, setActiveTab] = useState("upload");

  const logout = () => { setToken(""); setRole(""); setUsername(""); };

  if (!token) return <Login setToken={setToken} setRole={setRole} setUsername={setUsername} />;

  return (
    <div style={{
      display: "flex", height: "100vh", background: "var(--bg-primary)",
      fontFamily: "Inter, -apple-system, sans-serif"
    }}>
      {/* Sidebar */}
      <div style={{
        width: "260px", background: "var(--bg-secondary)", borderRight: "1px solid var(--border)",
        display: "flex", flexDirection: "column", padding: "20px", flexShrink: 0
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "28px" }}>
          <div style={{
            width: "36px", height: "36px", borderRadius: "10px", background: "var(--accent-light)",
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: "18px"
          }}>🔐</div>
          <div>
            <div style={{ fontWeight: "700", fontSize: "15px", color: "var(--text-primary)" }}>Secure RAG</div>
            <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Banking Platform</div>
          </div>
        </div>

        <div style={{
          padding: "8px 12px", borderRadius: "8px",
          background: role === "admin" ? "var(--admin-light)" : "var(--accent-light)",
          border: `1px solid ${role === "admin" ? "rgba(59,130,246,0.3)" : "rgba(108,99,255,0.3)"}`,
          marginBottom: "20px"
        }}>
          <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "2px" }}>Signed in as</div>
          <div style={{ fontSize: "13px", fontWeight: "600", color: role === "admin" ? "#60a5fa" : "var(--accent)" }}>
            {role === "admin" ? (username === "admin" ? "👑 Master Admin" : "⚙️ Administrator") : "👤 User"}
          </div>
        </div>

        {role === "admin" ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "10px", fontWeight: "600", textTransform: "uppercase", letterSpacing: "0.5px" }}>Menu</div>
            
            <button onClick={() => setActiveTab("upload")} style={{
              padding: "10px", border: "none", borderRadius: "8px", cursor: "pointer", textAlign: "left", fontSize: "13px", fontWeight: "600",
              background: activeTab === "upload" ? "rgba(255,255,255,0.1)" : "transparent", color: "var(--text-primary)"
            }}>📚 Knowledge Base</button>
            
            {username === "admin" && (
              <>
                <button onClick={() => setActiveTab("users")} style={{
                  padding: "10px", border: "none", borderRadius: "8px", cursor: "pointer", textAlign: "left", fontSize: "13px", fontWeight: "600",
                  background: activeTab === "users" ? "rgba(255,255,255,0.1)" : "transparent", color: "var(--text-primary)"
                }}>👥 User Management</button>
                <button onClick={() => setActiveTab("audits")} style={{
                  padding: "10px", border: "none", borderRadius: "8px", cursor: "pointer", textAlign: "left", fontSize: "13px", fontWeight: "600",
                  background: activeTab === "audits" ? "rgba(255,255,255,0.1)" : "transparent", color: "var(--text-primary)"
                }}>📊 SIEM Audit Logs</button>
              </>
            )}
          </div>
        ) : (
          <div>
            <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "10px", fontWeight: "600", textTransform: "uppercase", letterSpacing: "0.5px" }}>How it works</div>
            {["🔒 Documents are scanned for threats", "🧹 Content is sanitized", "🔐 PII is pseudonymized", "🧠 Stored in secure vector DB"].map(tip => (
              <div key={tip} style={{ fontSize: "12px", color: "var(--text-secondary)", marginBottom: "8px" }}>{tip}</div>
            ))}
          </div>
        )}

        <div style={{ marginTop: "auto" }}>
          <button onClick={logout} style={{
            width: "100%", padding: "10px", border: "1px solid var(--border)",
            borderRadius: "8px", background: "transparent", color: "var(--text-secondary)",
            cursor: "pointer", fontSize: "13px", fontWeight: "600",
            transition: "all 0.2s"
          }}
            onMouseOver={e => { e.target.style.background = "var(--danger-light)"; e.target.style.color = "#f87171"; e.target.style.borderColor = "rgba(239,68,68,0.3)"; }}
            onMouseOut={e => { e.target.style.background = "transparent"; e.target.style.color = "var(--text-secondary)"; e.target.style.borderColor = "var(--border)"; }}
          >Sign Out</button>
        </div>
      </div>

      {/* Main content */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        {/* Header */}
        <div style={{
          padding: "18px 28px", borderBottom: "1px solid var(--border)",
          background: "var(--bg-secondary)", display: "flex", alignItems: "center", justifyContent: "space-between"
        }}>
          <h2 style={{ fontSize: "16px", fontWeight: "600", color: "var(--text-primary)", margin: 0 }}>
            {role === "admin" ? "⚙️ Admin Knowledge Base Dashboard" : "💬 Secure Banking Assistant"}
          </h2>
          <span style={{
            fontSize: "12px", padding: "4px 10px", borderRadius: "20px",
            background: role === "admin" ? "var(--admin-light)" : "var(--accent-light)",
            color: role === "admin" ? "#60a5fa" : "var(--accent)",
            border: `1px solid ${role === "admin" ? "rgba(59,130,246,0.3)" : "rgba(108,99,255,0.3)"}`
          }}>
            {role === "admin" ? "Admin Access" : "User Access"}
          </span>
        </div>

        {/* Body */}
        <div style={{ flex: 1, padding: "28px", overflowY: "auto", display: "flex", flexDirection: "column" }}>
          {role === "admin" ? (
            <div style={{ maxWidth: "900px", margin: "0 auto", width: "100%" }}>
              {activeTab === "upload" && (
                <>
                  <p style={{ color: "var(--text-secondary)", marginBottom: "24px", fontSize: "14px" }}>
                    Upload banking policy documents, guidelines, or reference material below. Once uploaded, documents are sanitized, PII-anonymized, and indexed into the global knowledge base that all users can query.
                  </p>
                  <Upload token={token} />
                </>
              )}
              {activeTab === "users" && username === "admin" && <UserManagement token={token} />}
              {activeTab === "audits" && username === "admin" && <Audits token={token} />}
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", height: "100%", maxWidth: "760px", margin: "0 auto", width: "100%" }}>
              <div style={{ marginBottom: "20px" }}>
                <p style={{ color: "var(--text-secondary)", fontSize: "13px" }}>
                  You can also upload your own documents below — they are stored in your private vault.
                </p>
                <div style={{ marginTop: "12px" }}>
                  <Upload token={token} />
                </div>
              </div>
              <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: "300px" }}>
                <Query token={token} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;