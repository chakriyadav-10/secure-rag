import React, { useState, useEffect } from "react";

function UserManagement({ token }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const fetchUsers = () => {
    fetch(`${API_URL}/users?token=${token}`)
      .then(res => res.json())
      .then(data => {
        if (data.users) setUsers(data.users);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchUsers();
  }, [token]);

  const promoteUser = (username) => {
    fetch(`${API_URL}/users/${username}/promote?token=${token}`, {
      method: "POST"
    })
    .then(res => res.json())
    .then(data => {
      if (data.msg) {
        alert(data.msg);
        fetchUsers(); // Refresh list
      } else if (data.error) {
        alert(data.error);
      }
    });
  };

  const demoteUser = (username) => {
    fetch(`${API_URL}/users/${username}/demote?token=${token}`, {
      method: "POST"
    })
    .then(res => res.json())
    .then(data => {
      if (data.msg) {
        alert(data.msg);
        fetchUsers(); // Refresh list
      } else if (data.error) {
        alert(data.error);
      }
    });
  };

  if (loading) return <div style={{ color: "var(--text-muted)", fontSize: "14px" }}>Loading users...</div>;

  return (
    <div style={{
      background: "var(--bg-primary)", padding: "20px", borderRadius: "12px",
      border: "1px solid var(--border)", boxShadow: "0 4px 6px rgba(0,0,0,0.02)", width: "100%", marginTop: "24px"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <h3 style={{ fontSize: "15px", fontWeight: "600", color: "var(--text-primary)", margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
          <span>👥</span> User Management (Master Admin)
        </h3>
      </div>
      
      {users.length === 0 ? (
        <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>No users found.</p>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px", textAlign: "left" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--text-muted)" }}>
                <th style={{ padding: "10px 8px", fontWeight: "600" }}>Username</th>
                <th style={{ padding: "10px 8px", fontWeight: "600" }}>Role</th>
                <th style={{ padding: "10px 8px", fontWeight: "600" }}>Status</th>
                <th style={{ padding: "10px 8px", fontWeight: "600" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u, idx) => (
                <tr key={idx} style={{ borderBottom: "1px solid var(--border)" }}>
                  <td style={{ padding: "10px 8px", color: "var(--text-primary)", fontWeight: "500" }}>{u.username}</td>
                  <td style={{ padding: "10px 8px" }}>
                    <span style={{
                      padding: "4px 8px", borderRadius: "4px", fontSize: "11px", fontWeight: "600",
                      background: u.role === "admin" ? "var(--admin-light)" : "var(--accent-light)",
                      color: u.role === "admin" ? "#60a5fa" : "var(--accent)"
                    }}>
                      {u.role.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: "10px 8px" }}>
                    <span style={{
                      padding: "4px 8px", borderRadius: "4px", fontSize: "11px", fontWeight: "600",
                      background: u.is_blocked ? "var(--danger-light)" : "var(--success-light)",
                      color: u.is_blocked ? "#ef4444" : "#10b981"
                    }}>
                      {u.is_blocked ? "BLOCKED" : "ACTIVE"}
                    </span>
                  </td>
                  <td style={{ padding: "10px 8px" }}>
                    {u.role !== "admin" && !u.is_blocked && (
                      <button 
                        onClick={() => promoteUser(u.username)}
                        style={{
                          background: "linear-gradient(135deg, #10b981, #059669)",
                          color: "white", padding: "4px 10px", borderRadius: "6px",
                          border: "none", fontSize: "11px", fontWeight: "600", cursor: "pointer"
                        }}
                      >
                        Promote to Admin ⬆️
                      </button>
                    )}
                    {u.role === "admin" && !u.is_master && !u.is_blocked && (
                      <button 
                        onClick={() => demoteUser(u.username)}
                        style={{
                          background: "linear-gradient(135deg, #ef4444, #dc2626)",
                          color: "white", padding: "4px 10px", borderRadius: "6px",
                          border: "none", fontSize: "11px", fontWeight: "600", cursor: "pointer"
                        }}
                      >
                        Demote to User ⬇️
                      </button>
                    )}
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

export default UserManagement;
