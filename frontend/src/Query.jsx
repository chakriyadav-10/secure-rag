import axios from "axios";
import { useState, useRef, useEffect } from "react";

export default function Query({ token }) {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hello! I can answer banking-related questions using the secure knowledge base. What would you like to know?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
    axios.get(`${API_URL}/sessions`, { params: { token } })
      .then(res => {
        if (res.data.sessions) setSessions(res.data.sessions);
      })
      .catch(err => console.error("Failed to load sessions", err));
  }, [token]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadSession = (sessionId) => {
    setActiveSessionId(sessionId);
    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
    axios.get(`${API_URL}/chats`, { params: { token, session_id: sessionId } })
      .then(res => {
        if (res.data.chats) {
          const history = [];
          res.data.chats.forEach(chat => {
            history.push({ role: "user", text: chat.query });
            history.push({ role: "assistant", text: chat.answer, source: chat.source });
          });
          setMessages([
            { role: "assistant", text: "Welcome back! Here is your saved chat history." },
            ...history
          ]);
        }
      })
      .catch(err => console.error("Failed to load chat history", err));
  };

  const startNewChat = () => {
    setActiveSessionId(null);
    setMessages([{ role: "assistant", text: "Hello! I can answer banking-related questions using the secure knowledge base. What would you like to know?" }]);
  };

  const ask = async () => {
    if (!input.trim() || loading) return;
    const question = input.trim();
    setInput("");
    
    let currentSession = activeSessionId;
    let isNewSession = false;
    if (!currentSession) {
      currentSession = Date.now().toString() + Math.random().toString(36).substr(2, 5);
      setActiveSessionId(currentSession);
      isNewSession = true;
    }

    setMessages(prev => [...prev, { role: "user", text: question }]);
    setLoading(true);

    if (isNewSession) {
      setSessions(prev => [{ _id: currentSession, title: question }, ...prev]);
    }

    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const res = await axios.post(`${API_URL}/query`, null, {
        params: { q: question, token, session_id: currentSession }
      });
      setMessages(prev => [...prev, {
        role: "assistant",
        text: res.data.answer || res.data.error,
        source: res.data.source || ""
      }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: "assistant", text: "Error: " + e.message, source: "" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", height: "100%", overflow: "hidden", margin: "0 -20px -20px -20px" }}>
      
      {/* Sidebar Area */}
      <div style={{
        width: "260px", background: "var(--bg-secondary)", borderRight: "1px solid var(--border)",
        display: "flex", flexDirection: "column", padding: "20px 16px"
      }}>
        <button onClick={startNewChat} style={{
          padding: "12px", background: "var(--accent)", color: "white",
          border: "none", borderRadius: "10px", cursor: "pointer",
          fontWeight: "600", fontSize: "14px", marginBottom: "24px",
          display: "flex", alignItems: "center", justifyContent: "center", gap: "8px",
          boxShadow: "0 4px 12px rgba(108, 99, 255, 0.2)"
        }}>
          <span>➕</span> New Chat
        </button>
        <div style={{ fontSize: "12px", fontWeight: "700", color: "var(--text-muted)", marginBottom: "16px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
          Recent Sessions
        </div>
        <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "4px" }}>
          {sessions.map(s => (
            <button key={s._id} onClick={() => loadSession(s._id)} style={{
              padding: "12px 14px", background: activeSessionId === s._id ? "var(--bg-tertiary)" : "transparent",
              border: "1px solid", borderColor: activeSessionId === s._id ? "var(--border)" : "transparent",
              borderRadius: "8px", cursor: "pointer", textAlign: "left",
              color: activeSessionId === s._id ? "var(--text-primary)" : "var(--text-secondary)",
              fontSize: "14px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
              transition: "all 0.2s"
            }}>
              💬 {s.title}
            </button>
          ))}
          {sessions.length === 0 && <div style={{ fontSize: "13px", color: "var(--text-muted)", textAlign: "center", marginTop: "20px" }}>No past history</div>}
        </div>
      </div>

      {/* Main Chat Area */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: "0 24px" }}>
        <div style={{
          flex: 1, overflowY: "auto", padding: "24px 0",
          display: "flex", flexDirection: "column", gap: "16px"
        }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start", flexDirection: "column", alignItems: msg.role === "user" ? "flex-end" : "flex-start" }}>
              <div style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start" }}>
                {msg.role === "assistant" && (
                  <div style={{
                    width: "32px", height: "32px", borderRadius: "50%",
                    background: "var(--accent-light)", display: "flex", alignItems: "center",
                    justifyContent: "center", marginRight: "10px", flexShrink: 0, fontSize: "16px"
                  }}>🤖</div>
                )}
                <div style={{
                  maxWidth: "75%", padding: "12px 16px",
                  borderRadius: msg.role === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
                  background: msg.role === "user" ? "var(--accent)" : "var(--bg-tertiary)",
                  color: "var(--text-primary)", fontSize: "14px", lineHeight: "1.8",
                  border: msg.role === "assistant" ? "1px solid var(--border)" : "none"
                }}>
                  {msg.role === "assistant"
                    ? msg.text.split("\n").map((raw, j) => {
                        const line = raw.replace(/\*\*/g, ""); 
                        if (line.startsWith("💡")) return <div key={j} style={{ marginTop: "10px", padding: "8px 12px", background: "rgba(108,99,255,0.1)", borderRadius: "8px", borderLeft: "3px solid var(--accent)", fontSize: "13px", fontWeight: "500" }}>{line}</div>;
                        if (line.startsWith("#### ")) return <div key={j} style={{ fontWeight: "700", fontSize: "13px", color: "var(--accent)", marginTop: "8px", marginBottom: "2px" }}>{line.slice(5)}</div>;
                        if (line.startsWith("### ")) return <div key={j} style={{ fontWeight: "700", fontSize: "14px", marginTop: "10px", marginBottom: "4px", color: "var(--text-primary)" }}>{line.slice(4)}</div>;
                        if (line.startsWith("## ")) return <div key={j} style={{ fontWeight: "700", fontSize: "15px", marginTop: "10px", marginBottom: "4px" }}>{line.slice(3)}</div>;
                        if (line.startsWith("# ")) return <div key={j} style={{ fontWeight: "700", fontSize: "16px", marginTop: "8px", marginBottom: "4px" }}>{line.slice(2)}</div>;
                        if (/^\d+\./.test(line)) return <div key={j} style={{ marginLeft: "12px", marginBottom: "2px" }}>{line}</div>;
                        if (line.startsWith("* ")) return <div key={j} style={{ marginLeft: "12px", marginBottom: "2px" }}>• {line.slice(2)}</div>;
                        if (line.startsWith("- ") || line.startsWith("• ")) return <div key={j} style={{ marginLeft: "12px", marginBottom: "2px" }}>{line}</div>;
                        if (line === "") return <br key={j} />;
                        return <div key={j}>{line}</div>;
                      })
                    : msg.text}
                </div>
              </div>
              {msg.role === "assistant" && msg.source && (
                <div style={{
                  marginLeft: "42px", marginTop: "5px",
                  fontSize: "11px", color: "var(--text-muted)",
                  background: "var(--bg-secondary)", border: "1px solid var(--border)",
                  borderRadius: "20px", padding: "2px 10px", display: "inline-block"
                }}>{msg.source}</div>
              )}
            </div>
          ))}
          {loading && (
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <div style={{
                width: "32px", height: "32px", borderRadius: "50%",
                background: "var(--accent-light)", display: "flex",
                alignItems: "center", justifyContent: "center", fontSize: "16px"
              }}>🤖</div>
              <div style={{
                background: "var(--bg-tertiary)", border: "1px solid var(--border)",
                padding: "12px 18px", borderRadius: "18px 18px 18px 4px",
                color: "var(--text-muted)", fontSize: "14px"
              }}>Thinking...</div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div style={{
          padding: "16px 0", borderTop: "1px solid var(--border)",
          display: "flex", gap: "10px", alignItems: "flex-end", marginBottom: "8px"
        }}>
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(); } }}
            placeholder="Ask anything about banking... (Enter to send, Shift+Enter for new line)"
            rows={1}
            style={{
              flex: 1, padding: "14px 16px", resize: "none",
              background: "var(--bg-secondary)", border: "1px solid var(--border)",
              borderRadius: "12px", color: "var(--text-primary)", fontSize: "14px",
              outline: "none", lineHeight: "1.5", maxHeight: "120px", overflowY: "auto",
              fontFamily: "inherit", transition: "border 0.2s"
            }}
            onFocus={e => e.target.style.borderColor = "var(--accent)"}
            onBlur={e => e.target.style.borderColor = "var(--border)"}
          />
          <button onClick={ask} disabled={loading} style={{
            padding: "14px 18px", border: "none", borderRadius: "12px",
            background: loading ? "var(--bg-secondary)" : "var(--accent)",
            cursor: loading ? "not-allowed" : "pointer",
            fontSize: "18px", color: "white", transition: "all 0.2s",
            boxShadow: loading ? "none" : "0 4px 12px rgba(108, 99, 255, 0.2)"
          }}>➤</button>
        </div>
      </div>
    </div>
  );
}