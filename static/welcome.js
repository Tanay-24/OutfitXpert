// ===== TRY-ON CATEGORY =====
document.getElementById("tryonLink").addEventListener("click", function (e) {
  e.preventDefault();
  document.querySelector(".tryon-category").scrollIntoView({ behavior: 'smooth' });
});

// ===== USER LOGIN LOGIC =====
function loginUser(email, password) {
  fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  })
    .then(res => res.json())
    .then(data => {
      if (data.username) {
        const profile = document.querySelector(".user-profile");
        const usernameEl = profile.querySelector(".username");
        const avatar = profile.querySelector("img");

        // Set username text
        usernameEl.textContent = data.username;
        profile.setAttribute("data-username", data.username);

        // Optional profile image
        if (data.profileImageURL) {
          avatar.src = data.profileImageURL;
        }

        // Toggle dropdown on click
        profile.addEventListener("click", function () {
          this.classList.toggle("show-dropdown");
        });

        // Add logout button event
        const logoutBtn = document.getElementById("logoutBtn");
        if (logoutBtn) {
          logoutBtn.addEventListener("click", function () {
            fetch("/logout")
              .then(() => {
                window.location.href = "index.html"; // Redirect after logout
              })
              .catch(err => {
                console.error("Logout failed", err);
              });
          });
        }
      } else if (data.error) {
        console.error("Login error:", data.error);
      }
    })
    .catch(err => {
      console.error("Login failed", err);
    });
}
const profile = document.querySelector(".user-profile");
profile.addEventListener("click", function (e) {
  e.stopPropagation(); // Prevent other click handlers from interfering
  this.classList.toggle("show-dropdown");
});

// Optional: hide dropdown when clicking outside
document.addEventListener("click", function () {
  profile.classList.remove("show-dropdown");
});
