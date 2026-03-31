import axios from "axios";
import { useState, useRef, useEffect } from "react";

export default function Query({ token }) {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hello! I can answer banking-related questions using the secure knowledge base. What would you like to know?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const ask = async () => {
    if (!input.trim() || loading) return;
    const question = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", text: question }]);
    setLoading(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const res = await axios.post(`${API_URL}/query`, null, {
        params: { q: question, token }
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
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{
        flex: 1, overflowY: "auto", padding: "20px 0",
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
                      const line = raw.replace(/\*\*/g, ""); // strip inline bold
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
        padding: "16px 0 4px", borderTop: "1px solid var(--border)",
        display: "flex", gap: "10px", alignItems: "flex-end"
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
            fontFamily: "inherit"
          }}
          onFocus={e => e.target.style.borderColor = "var(--accent)"}
          onBlur={e => e.target.style.borderColor = "var(--border)"}
        />
        <button onClick={ask} disabled={loading} style={{
          padding: "14px 18px", border: "none", borderRadius: "12px",
          background: loading ? "var(--bg-secondary)" : "var(--accent)",
          cursor: loading ? "not-allowed" : "pointer",
          fontSize: "18px", color: "white", transition: "all 0.2s"
        }}>➤</button>
      </div>
    </div>
  );
}