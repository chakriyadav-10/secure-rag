import axios from "axios";
import { useState, useEffect } from "react";

export default function Login({ setToken, setRole, setIsMaster }) {
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [errorType, setErrorType] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [usernameStatus, setUsernameStatus] = useState(null);
  const [checkingUser, setCheckingUser] = useState(false);

  useEffect(() => {
    if (!isRegistering || user.length === 0) {
      setUsernameStatus(null);
      return;
    }
    
    if (user.length < 3) {
      setUsernameStatus({ available: false, msg: "Too short" });
      return;
    }

    setCheckingUser(true);
    const timeoutId = setTimeout(() => {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      axios.get(`${API_URL}/check-username`, { params: { username: user } })
        .then(res => setUsernameStatus(res.data))
        .finally(() => setCheckingUser(false));
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [user, isRegistering]);

  const authenticate = async () => {
    if (!user || !pass) return;
    
    if (isRegistering && usernameStatus && !usernameStatus.available) {
      setError(`Cannot complete registration: Username ${usernameStatus.msg.toLowerCase()}`);
      setErrorType("error");
      return;
    }

    setLoading(true);
    setError("");
    setErrorType("");
    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      if (isRegistering) {
        await axios.post(`${API_URL}/register`, null, {
          params: { username: user, password: pass, role: "user" }
        });
        setError("✅ Account created! You can now log in.");
        setErrorType("success");
        setIsRegistering(false);
      } else {
        const res = await axios.post(`${API_URL}/login`, null, {
          params: { username: user, password: pass }
        });
        setToken(res.data.token);
        if (setRole && res.data.role) setRole(res.data.role);
        if (setIsMaster !== undefined) setIsMaster(res.data.is_master);
      }
    } catch (e) {
      const msg = e.response?.data?.error || e.message || "";
      if (msg.toLowerCase().includes("invalid") || e.response?.status === 401) {
        setError("❌ Account not found or wrong password.");
        setErrorType("notfound");
      } else {
        setError("❌ " + msg);
        setErrorType("error");
      }
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e) => { if (e.key === "Enter") authenticate(); };

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center",
      justifyContent: "center", background: "var(--bg-primary)", padding: "20px"
    }}>
      <div style={{
        width: "100%", maxWidth: "400px",
        background: "var(--bg-card)", borderRadius: "16px",
        border: "1px solid var(--border)", padding: "40px",
        boxShadow: "0 25px 60px rgba(0,0,0,0.5)"
      }}>
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <div style={{
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            width: "52px", height: "52px", borderRadius: "14px",
            background: "var(--accent-light)", marginBottom: "16px"
          }}>
            <span style={{ fontSize: "24px" }}>🔐</span>
          </div>
          <h1 style={{ fontSize: "22px", fontWeight: "700", color: "var(--text-primary)" }}>
            Secure RAG
          </h1>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "4px" }}>
            Banking Intelligence Platform
          </p>
        </div>

        <div style={{
          display: "flex", background: "var(--bg-secondary)", borderRadius: "10px",
          padding: "4px", marginBottom: "28px"
        }}>
          {["Login", "Register"].map(tab => (
            <button key={tab} onClick={() => setIsRegistering(tab === "Register")} style={{
              flex: 1, padding: "9px", border: "none", borderRadius: "8px", cursor: "pointer",
              fontWeight: "600", fontSize: "14px", transition: "all 0.2s",
              background: (tab === "Register") === isRegistering ? "var(--accent)" : "transparent",
              color: (tab === "Register") === isRegistering ? "white" : "var(--text-secondary)"
            }}>{tab}</button>
          ))}
        </div>

        {[
          { placeholder: "Username", value: user, setter: setUser, type: "text", isUsername: true },
          { placeholder: "Password", value: pass, setter: setPass, type: showPassword ? "text" : "password", isPassword: true }
        ].map(field => (
          <div key={field.placeholder} style={{ marginBottom: "14px", position: "relative" }}>
            <input
              type={field.type}
              placeholder={field.placeholder}
              value={field.value}
              onChange={e => field.setter(e.target.value)}
              onKeyDown={onKeyDown}
              style={{
                width: "100%", padding: "13px 16px",
                background: "var(--bg-secondary)", border: "1px solid var(--border)",
                borderRadius: "10px", color: "var(--text-primary)", fontSize: "14px",
                outline: "none", transition: "border 0.2s"
              }}
              onFocus={e => e.target.style.borderColor = "var(--accent)"}
              onBlur={e => e.target.style.borderColor = "var(--border)"}
            />
            {field.isPassword && (
              <span 
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: "absolute", right: "12px", top: "14px",
                  cursor: "pointer", fontSize: "16px", color: "var(--text-muted)"
                }}
              >
                {showPassword ? "🙈" : "👁️"}
              </span>
            )}
            {field.isUsername && isRegistering && user.length > 0 && (
              <div style={{ marginTop: "6px", fontSize: "12px", display: "flex", alignItems: "center", gap: "6px", color: usernameStatus?.available ? "#4ade80" : "#f87171" }}>
                {checkingUser ? (
                  <span style={{ color: "var(--text-muted)" }}>⏳ Checking...</span>
                ) : (
                  <>
                    <span>{usernameStatus?.available ? "✅" : "❌"}</span>
                    <span>{usernameStatus?.available ? "Username is available!" : `Username ${usernameStatus?.msg?.toLowerCase() || "taken"}`}</span>
                  </>
                )}
              </div>
            )}
          </div>
        ))}

        {error && (
          <div style={{
            padding: "10px 14px", borderRadius: "8px", marginBottom: "12px",
            fontSize: "13px", background: errorType === "success" ? "rgba(34,197,94,0.1)" : "rgba(239,68,68,0.1)",
            border: `1px solid ${errorType === "success" ? "rgba(34,197,94,0.3)" : "rgba(239,68,68,0.3)"}`,
            color: errorType === "success" ? "#4ade80" : "#f87171"
          }}>
            {error}
            {errorType === "notfound" && (
              <span>
                {" "}Don't have an account?{" "}
                <span onClick={() => { setIsRegistering(true); setError(""); }}
                  style={{ textDecoration: "underline", cursor: "pointer", fontWeight: "600" }}>
                  Register here
                </span>
              </span>
            )}
          </div>
        )}

        <button onClick={authenticate} disabled={loading} style={{
          width: "100%", padding: "13px", marginTop: "8px",
          background: loading ? "var(--text-muted)" : "var(--accent)",
          color: "white", border: "none", borderRadius: "10px",
          fontSize: "15px", fontWeight: "600", cursor: loading ? "not-allowed" : "pointer",
          transition: "background 0.2s",
        }}>
          {loading ? "Please wait..." : isRegistering ? "Create Account" : "Sign In"}
        </button>

      </div>
    </div>
  );
}