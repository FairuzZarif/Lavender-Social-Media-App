function getCSRFToken() {
    const cookieValue = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];

    return cookieValue || null;
}

document.addEventListener("DOMContentLoaded", () => {
    // Get CSRF token from the cookie
    const csrfToken = getCSRFToken();
    console.log("CSRF Token:", csrfToken);

    refreshToken();  // Refresh token when app loads

    // Handle signup form submission
    const signupForm = document.getElementById("signup-form");
    if (signupForm) {
        signupForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();
            const confirmPassword = document.getElementById("confirm-password").value.trim();
            const errorMessage = document.getElementById("error-message");

            if (!username || !password) {
                errorMessage.textContent = "Username and password cannot be empty!";
                errorMessage.style.visibility = 'visible';
                console.error("Username or password is missing!"); // Debug log
                return;
            }

            console.log("Signup Request Data:", { username, password, confirmPassword });

            const csrfToken = getCSRFToken();
            console.log("CSRF Token Used:", csrfToken);

            const response = await fetch("/api/signup/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({ username, password, confirm_password: confirmPassword }),
            });

            const data = await response.json();
            console.log("Signup API Response:", data);

            if (response.status === 201) {
                localStorage.setItem("access_token", data.access);
                localStorage.setItem("refresh_token", data.refresh);
                window.location.href = "/home/"; // Redirect to home after successful signup
            } else {
                errorMessage.textContent = data.error;
                errorMessage.style.visibility = 'visible';
            }
        });
    }

    // Handle login form submission
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const username = document.getElementById("login-username").value;
            const password = document.getElementById("login-password").value;
            const errorMessage = document.getElementById("error-message");

            // Send POST request to login API
            const response = await fetch("/api/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,  // Add CSRF token here
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();

            if (response.status === 200) {
                // If login is successful, store JWT tokens and author_id in localStorage
                localStorage.setItem("access_token", data.access);
                localStorage.setItem("refresh_token", data.refresh);
                localStorage.setItem("author_id", data.author_id);  // Save the author_id here

                // Redirect to homepage
                window.location.href = "/home/";
            } else {
                errorMessage.textContent = data.error;
                errorMessage.style.visibility = 'visible';
            }
        });
    }
});

// Refresh token function to update the access token
async function refreshToken() {
    const refresh = localStorage.getItem("refresh_token");
    if (!refresh) return;

    const csrfToken = getCSRFToken();  // Get CSRF Token here

    const response = await fetch("/api/token/refresh/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,  // Now it's defined
        },
        body: JSON.stringify({ refresh }),
    });

    const data = await response.json();
    if (response.status === 200) {
        localStorage.setItem("access_token", data.access);
    } else {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login/"; // Redirect to login if refresh fails
    }
}
