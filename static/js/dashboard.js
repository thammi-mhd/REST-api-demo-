const token = localStorage.getItem("token");
const role = localStorage.getItem("role");

// Redirect to login if auth data is missing
if (!token || !role) {
  window.location.href = "/login";
}

// Decode JWT payload (used only for UI info)
function decodeToken(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload;
  } catch (e) {
    console.error("Invalid token");
    logout();
    return null;
  }
}

const payload = decodeToken(token);
if (!payload) {
  logout();
}

// Extract user info from token
const userId = parseInt(payload.sub) || null;
const userName = payload.name || payload.email || "User";
const userEmail = payload.email || "User";
const userRole = payload.role || "user";

// Debug logs during development
console.log("Decoded token payload:", payload);
console.log("User ID:", userId);
console.log("User Name:", userName);
console.log("User email:", userEmail);
console.log("User role:", userRole);

// Update UI with user info
document.getElementById("welcome").innerText = `Welcome, ${userName}`;
document.getElementById("userRole").innerText = `Role: ${userRole}`;

// Show admin panel only for admin users
if (userRole && userRole.toLowerCase() === "admin") {
  document.getElementById("adminPanel").style.display = "block";
} else {
  document.getElementById("adminPanel").style.display = "none";
}

// Helper for authenticated API requests
function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

// Clear auth data and redirect
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  window.location.href = "/login";
}

// Create a new task
async function createTask() {
  const title = document.getElementById("taskTitle").value.trim();
  const description = document.getElementById("taskDesc").value.trim();
  const msg = document.getElementById("taskMessage");

  if (!title) {
    msg.textContent = "⚠️ Task title is required";
    msg.style.color = "#dc2626";
    msg.style.fontWeight = "600";
    setTimeout(() => (msg.textContent = ""), 4000);
    return;
  }

  try {
    const res = await fetch("/api/v1/tasks", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ title, description }),
    });

    const data = await res.json();

    if (!res.ok) {
      msg.textContent = "❌ " + (data.message || "Error creating task");
      msg.style.color = "#dc2626";
      msg.style.fontWeight = "600";
      setTimeout(() => (msg.textContent = ""), 4000);
      return;
    }

    msg.textContent = "✅ Task added successfully!";
    msg.style.color = "#22c55e";
    msg.style.fontWeight = "600";

    document.getElementById("taskTitle").value = "";
    document.getElementById("taskDesc").value = "";

    setTimeout(() => (msg.textContent = ""), 3000);
    loadTasks();
  } catch (error) {
    msg.textContent = "❌ Network error. Please try again.";
    msg.style.color = "#dc2626";
    msg.style.fontWeight = "600";
    setTimeout(() => (msg.textContent = ""), 4000);
  }
}

// Fetch tasks for current user
async function loadTasks() {
  try {
    const res = await fetch("/api/v1/tasks", {
      headers: authHeaders(),
    });

    if (res.status === 401) {
      logout();
      return;
    }

    const tasks = await res.json();
    const list = document.getElementById("taskList");
    list.innerHTML = "";

    if (!tasks.length) {
      list.innerHTML =
        "<li style='text-align: center; color: #9ca3af; padding: 20px;'>✨ No tasks yet. Create one to get started!</li>";
      return;
    }

    tasks.forEach((t) => {
      const li = document.createElement("li");
      li.style.display = "flex";
      li.style.justifyContent = "space-between";
      li.style.alignItems = "center";

      const content = document.createElement("div");
      content.innerHTML = `<strong>${t.title}</strong>${
        t.description
          ? `<br><small style="color: #6b7280;">${t.description}</small>`
          : ""
      }`;

      li.appendChild(content);

      const deleteBtn = document.createElement("button");
      deleteBtn.innerHTML = "🗑️";
      deleteBtn.style.background = "none";
      deleteBtn.style.border = "none";
      deleteBtn.style.cursor = "pointer";
      deleteBtn.style.fontSize = "1.2rem";
      deleteBtn.onclick = () => deleteTask(t.id);

      li.appendChild(deleteBtn);
      list.appendChild(li);
    });
  } catch (error) {
    console.error("Error loading tasks:", error);
  }
}

// Delete a task
async function deleteTask(taskId) {
  if (!confirm("Delete this task?")) {
    return;
  }

  try {
    const res = await fetch(`/api/v1/tasks/${taskId}`, {
      method: "DELETE",
      headers: authHeaders(),
    });

    if (!res.ok) {
      alert("Error deleting task");
      return;
    }

    loadTasks();
  } catch (error) {
    console.error("Error deleting task:", error);
  }
}

// Load all users (admin only)
async function loadUsers() {
  try {
    const res = await fetch("/api/v1/admin/users", {
      headers: authHeaders(),
    });

    if (res.status === 401 || res.status === 403) {
      alert("You do not have permission to view this");
      return;
    }

    const users = await res.json();
    const tbody = document.getElementById("userList");
    const adminMsg = document.getElementById("adminMessage");

    tbody.innerHTML = "";
    adminMsg.textContent = "";

    if (!users.length) {
      tbody.innerHTML =
        "<tr><td colspan='5' style='text-align: center; padding: 20px; color: #9ca3af;'>No users found</td></tr>";
      return;
    }

    document.getElementById("totalUsers").innerText = users.length;

    users.forEach((u) => {
      const tr = document.createElement("tr");
      const roleColor = u.role === "admin" ? "#ef4444" : "#22c55e";
      const roleLabel = u.role === "admin" ? "👑 Admin" : "👤 User";

      tr.innerHTML = `
        <td style="padding: 12px;">${u.id}</td>
        <td style="padding: 12px; font-weight: 600;">${u.name || "N/A"}</td>
        <td style="padding: 12px;">${u.email}</td>
        <td style="padding: 12px;">
          <span style="background: ${roleColor}; color: white; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
            ${roleLabel}
          </span>
        </td>
        <td style="padding: 12px;">
          <button onclick="deleteUser(${u.id})" style="background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.9rem;">🗑️ Delete</button>
        </td>
      `;

      tbody.appendChild(tr);
    });
  } catch (error) {
    document.getElementById("adminMessage").textContent =
      "❌ Error loading users: " + error.message;
    document.getElementById("adminMessage").style.color = "#dc2626";
  }
}

// Delete a user (admin)
async function deleteUser(userId) {
  if (!confirm("Are you sure you want to delete this user?")) {
    return;
  }

  try {
    const res = await fetch(`/api/v1/admin/users/${userId}`, {
      method: "DELETE",
      headers: authHeaders(),
    });

    const data = await res.json();

    if (!res.ok) {
      alert("❌ Error: " + data.message);
      return;
    }

    document.getElementById("adminMessage").textContent =
      "✅ User deleted successfully";
    document.getElementById("adminMessage").style.color = "#22c55e";
    document.getElementById("adminMessage").style.fontWeight = "600";

    setTimeout(() => loadUsers(), 1000);
  } catch (error) {
    alert("❌ Error deleting user: " + error.message);
  }
}

// Delete all users (admin)
async function deleteAllUsers() {
  if (
    !confirm("⚠️ WARNING: This will delete ALL users. Are you absolutely sure?")
  ) {
    return;
  }

  if (!confirm("🔴 This action cannot be undone. Type 'DELETE' to confirm.")) {
    return;
  }

  try {
    const res = await fetch("/api/v1/admin/users/delete-all", {
      method: "DELETE",
      headers: authHeaders(),
    });

    const data = await res.json();

    if (!res.ok) {
      alert("❌ Error: " + data.message);
      return;
    }

    document.getElementById("adminMessage").textContent =
      "✅ All users deleted successfully";
    document.getElementById("adminMessage").style.color = "#22c55e";
    document.getElementById("adminMessage").style.fontWeight = "600";

    setTimeout(() => loadUsers(), 1000);
  } catch (error) {
    alert("❌ Error deleting all users: " + error.message);
  }
}

// Initial load
document.addEventListener("DOMContentLoaded", () => {
  loadTasks();
});
