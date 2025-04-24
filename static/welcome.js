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
        profile.addEventListener("click", function (e) {
          e.stopPropagation(); // Prevent click from closing dropdown immediately
          this.classList.toggle("show-dropdown");
        });

        // Add logout button event
        const logoutBtn = document.getElementById("logoutBtn");
        if (logoutBtn) {
          logoutBtn.addEventListener("click", function () {
            fetch("/logout")
              .then(() => {
                window.location.href = "/templates/index.html"; // Redirect to /templates/index.html after logout
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

// ===== USER PROFILE DROPDOWN TOGGLE =====
document.addEventListener('DOMContentLoaded', function () {
  const userProfile = document.querySelector(".user-profile");
  const dropdownMenu = document.querySelector(".dropdown-menu");
  
  // Toggle the dropdown when clicking on the user profile
  userProfile.addEventListener("click", function (e) {
    e.stopPropagation(); // Prevent other click handlers from interfering
    dropdownMenu.style.display = dropdownMenu.style.display === "flex" ? "none" : "flex";
  });

  // Close dropdown when clicking outside the user profile
  document.addEventListener("click", function (e) {
    if (!userProfile.contains(e.target)) {
      dropdownMenu.style.display = "none";
    }
  });

  // Handle logout button click
  document.addEventListener('DOMContentLoaded', function () {
    const logoutBtn = document.getElementById('logoutBtn');
    const logoutForm = logoutBtn.closest('form');  // Get the form that wraps the button

    // Event listener to handle form submission
    logoutForm.addEventListener('submit', function (e) {
        e.preventDefault();  // Prevent the default form submission

        // You can add any additional actions you want before logging out
        console.log("Logging out...");

        // Clear session storage to ensure user cannot go back after logout
        sessionStorage.clear();  // Clears the session storage

        // Manually submit the form to log out
        logoutForm.submit();
    });
}); 
});
