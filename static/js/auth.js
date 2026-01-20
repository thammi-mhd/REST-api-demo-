const API_BASE_URL = "http://127.0.0.1:5000/api/v1";

// REGISTER FORM HANDLER
const registerForm = document.getElementById("registerForm");

if (registerForm) {
  const registerBtn = registerForm.querySelector("button[type='submit']");
  const inputs = registerForm.querySelectorAll("input");

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const messageBox = document.getElementById("message");

    // Get form values
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm_password").value;

    console.log("Register form submitted");
    console.log("Name:", name);
    console.log("Email:", email);
    console.log("Password:", password ? "***" : "empty");
    console.log("Confirm:", confirmPassword ? "***" : "empty");

    // Validate passwords match
    if (password !== confirmPassword) {
      messageBox.innerText = "Passwords do not match";
      messageBox.className = "message-box error";
      messageBox.style.display = "block";
      // Auto-focus on confirm password field
      document.getElementById("confirm_password").focus();
      return;
    }

    // Validate fields are not empty
    if (!name || !email || !password) {
      messageBox.innerText = "All fields are required";
      messageBox.className = "message-box error";
      messageBox.style.display = "block";
      return;
    }

    // Validate password length
    if (password.length < 6) {
      messageBox.innerText = "Password must be at least 6 characters";
      messageBox.className = "message-box error";
      messageBox.style.display = "block";
      document.getElementById("password").focus();
      return;
    }

    // Validate email format
    if (!email.includes("@") || !email.includes(".")) {
      messageBox.innerText = "Please enter a valid email";
      messageBox.className = "message-box error";
      messageBox.style.display = "block";
      document.getElementById("email").focus();
      return;
    }

    // Disable form during submission
    inputs.forEach((input) => (input.disabled = true));
    registerBtn.disabled = true;
    const originalText = registerBtn.innerText;
    registerBtn.innerText = "Creating Account...";

    try {
      const payload = { name, email, password };
      console.log("Sending payload:", payload);

      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await response.json();
      console.log("Response status:", response.status);
      console.log("Response:", result);

      if (response.ok) {
        messageBox.innerText = "success " + result.message;
        messageBox.className = "message-box success";
      } else {
        messageBox.innerText =
          "something went wrong " + (result.message || "Registration failed");
        messageBox.className = "message-box error";
      }
      messageBox.style.display = "block";

      if (response.ok) {
        // Redirect after 2 seconds on success
        setTimeout(() => {
          window.location.href = "/login";
        }, 2000);
      } else {
        // Re-enable form on error
        inputs.forEach((input) => (input.disabled = false));
        registerBtn.disabled = false;
        registerBtn.innerText = originalText;
      }
    } catch (error) {
      console.error("Fetch error:", error);
      messageBox.innerText =
        "Network error. Please check your connection and try again.";
      messageBox.className = "message-box error";
      messageBox.style.display = "block";

      // Re-enable form on error
      inputs.forEach((input) => (input.disabled = false));
      registerBtn.disabled = false;
      registerBtn.innerText = originalText;
    }
  });
}

// ===============================
// LOGIN FORM HANDLER
// ===============================
const loginForm = document.getElementById("loginForm");

if (loginForm) {
  const loginBtn = loginForm.querySelector("button[type='submit']");
  const inputs = loginForm.querySelectorAll("input");

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const messageBox = document.getElementById("message");

    // Get form values
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    console.log("Login form submitted");
    console.log("Email:", email);
    console.log("Password:", password ? "***" : "empty");

    // Validate fields are not empty
    if (!email || !password) {
      messageBox.innerText = "Email and password are required";
      messageBox.className = "message-box error";
      messageBox.style.display = "block";
      if (!email) document.getElementById("email").focus();
      else if (!password) document.getElementById("password").focus();
      return;
    }

    // Validate email format
    if (!email.includes("@") || !email.includes(".")) {
      messageBox.innerText = "Please enter a valid email";
      messageBox.className = "message-box error";
      messageBox.style.display = "block";
      document.getElementById("email").focus();
      return;
    }

    // Disable form during submission
    inputs.forEach((input) => (input.disabled = true));
    loginBtn.disabled = true;
    const originalText = loginBtn.innerText;
    loginBtn.innerText = "Signing In...";

    try {
      const payload = { email, password };
      console.log("Sending payload:", payload);

      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await response.json();
      console.log("Response status:", response.status);
      console.log("Response:", result);

      if (response.ok) {
        messageBox.innerText = "success " + result.message;
        messageBox.className = "message-box success";
      } else {
        messageBox.innerText = "error " + (result.message || "Login failed");
        messageBox.className = "message-box error";
      }
      messageBox.style.display = "block";

      if (response.ok) {
        // Store token securely in localStorage
        localStorage.setItem("token", result.token);
        localStorage.setItem("role", result.role);
        console.log("Token stored in localStorage");
        console.log("Role stored:", result.role);

        // Redirect after 1.5 seconds on success
        setTimeout(() => {
          window.location.href = "/dashboard";
        }, 1500);
      } else {
        // Re-enable form on error
        inputs.forEach((input) => (input.disabled = false));
        loginBtn.disabled = false;
        loginBtn.innerText = originalText;
        // Auto-focus on first field for retry
        document.getElementById("email").focus();
      }
    } catch (error) {
      console.error("Fetch error:", error);
      messageBox.innerText =
        "Network error. Please check your connection and try again.";
      messageBox.className = "message-box error";
      messageBox.style.display = "block";

      // Re-enable form on error
      inputs.forEach((input) => (input.disabled = false));
      loginBtn.disabled = false;
      loginBtn.innerText = originalText;
    }
  });
}

// AUTH HEADER HELPER
function getAuthHeaders() {
  const token = localStorage.getItem("token");

  if (!token) {
    window.location.href = "/login";
    return {};
  }

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}
