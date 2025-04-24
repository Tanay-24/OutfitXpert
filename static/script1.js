// ===== HERO SECTION =====
const container = document.getElementById('heroContainer');
    const totalSlides = 4;
    let currentIndex = 0;

    function goToSlide(index) {
        container.style.transition = 'transform 0.6s ease-in-out';
        container.style.transform = `translateX(-${index * 100}%)`;
    }

    // Auto-slide every 4 seconds (looping like marquee)
    setInterval(() => {
        currentIndex++;
        if (currentIndex >= totalSlides) {
            // Temporarily disable transition to jump to start
            container.style.transition = 'none';
            container.style.transform = `translateX(0%)`;
            currentIndex = 1;

            // Trigger reflow to apply jump before resuming sliding
            void container.offsetWidth;

            // Resume smooth sliding to second block
            container.style.transition = 'transform 0.6s ease-in-out';
            container.style.transform = `translateX(-${currentIndex * 100}%)`;
        } else {
            goToSlide(currentIndex);
        }
    }, 4000);

document.addEventListener("DOMContentLoaded", () => {
    const getStartedBtn = document.querySelector(".cta-button");
    const loginModal = document.getElementById("loginModal");
    const closeLogin = document.getElementById("closeLogin");
    const loginTab = document.getElementById("loginTab");
    const signupTab = document.getElementById("signupTab");
    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");

    getStartedBtn.addEventListener("click", () => {
        loginModal.style.display = "flex";
    });

    closeLogin.addEventListener("click", () => {
        loginModal.style.display = "none";
    });

    window.addEventListener("click", (e) => {
        if (e.target === loginModal) {
            loginModal.style.display = "none";
        }
    });

    loginTab.addEventListener("click", () => {
        loginTab.classList.add("active");
        signupTab.classList.remove("active");
        loginForm.style.display = "block";
        signupForm.style.display = "none";
    });

    signupTab.addEventListener("click", () => {
        signupTab.classList.add("active");
        loginTab.classList.remove("active");
        signupForm.style.display = "block";
        loginForm.style.display = "none";
    });
});

// === Auth Google signup ===
window.addEventListener("DOMContentLoaded", async () => {
    const hash = window.location.hash;
    if (hash.includes("access_token")) {
        const params = new URLSearchParams(hash.substring(1));
        const access_token = params.get("access_token");

        try {
            const response = await fetch("/finalize_google_login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ access_token }),
            });
            const data = await response.json();
            if (!response.ok) {
                console.error("Login failed:", data.error);
            } else {
                console.log(data.message);  // You can show a success message here
            }
        } catch (err) {
            console.error("Error finalizing Google login:", err);
        }

        // Clean up URL
        history.replaceState(null, "", window.location.pathname);
    }
});

// ===== Login / Sign-Up Modal =====
loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();
    const errorMsg = document.getElementById("loginError");

    if (!email || !password) {
        errorMsg.textContent = "Please fill in all fields.";
        errorMsg.style.display = "block";
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });
        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            loginModal.style.display = "none";
            window.location.href = "/welcome";  // Redirect to welcome page after login
        } else {
            errorMsg.textContent = data.error || "Login failed.";
            errorMsg.style.display = "block";
        }
    } catch (err) {
        errorMsg.textContent = "Something went wrong.";
        errorMsg.style.display = "block";
    }
});

// ====== Signup form ======
signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("signupEmail").value.trim();
    const password = document.getElementById("signupPassword").value.trim();
    const full_name = document.getElementById("signupName").value.trim();  // Assuming you have a full name input field
    const errorMsg = document.getElementById("signupError");

    if (!email || !password || !full_name) {
        errorMsg.textContent = "All fields are required.";
        errorMsg.style.display = "block";
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password, full_name }),  // Include full_name in the request
        });
        const data = await response.json();

        if (response.ok) {
            alert("Signup successful! Please verify your email from your Gmail account.");
            loginModal.style.display = "none";
            window.location.href = "/welcome";  // Redirect to welcome page after signup
        } else {
            errorMsg.textContent = data.error || "Signup failed.";
            errorMsg.style.display = "block";
        }
    } catch (err) {
        errorMsg.textContent = "Something went wrong.";
        errorMsg.style.display = "block";
    }
});

// ===== TESTIMONIAL CAROUSEL =====
const cards = document.querySelectorAll('.card');
const dots = document.querySelectorAll('.dot');
let current = 0;

function showCard(index) {
  cards.forEach((card, i) => {
    card.classList.toggle('active', i === index);
    dots[i].classList.toggle('active', i === index);
  });
}

dots.forEach((dot, i) => {
  dot.addEventListener('click', () => {
    current = i;
    showCard(current);
  });
});

showCard(current); // Initial load

// ===== IMAGE UPLOAD PREVIEW =====
const fileInput = document.querySelector('input[type="file"]');
const previewContainer = document.querySelector(".image-preview");

fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            previewContainer.innerHTML = `<img src="${event.target.result}" alt="Preview" />`;
        };
        reader.readAsDataURL(file);
    }
});

// ===== SCROLL REVEAL ANIMATIONS =====
ScrollReveal().reveal('.section', {
    delay: 200,
    distance: '50px',
    origin: 'bottom',
    easing: 'ease-in-out'
});

// ===== Blocking to back page ====
document.addEventListener('DOMContentLoaded', function () {
    // Check if the user is logged in (e.g., by checking session storage or cookies)
    const user = sessionStorage.getItem("user_id");

    if (!user) {
        // Redirect to the login page if no user is found in session storage
        window.location.href = "/index.html";  // Or your actual login page URL
    }
});

document.addEventListener('DOMContentLoaded', function () {
    // When the user is logged out, prevent navigating back using browser's back button
    if (!sessionStorage.getItem("user_id")) {
        history.pushState(null, null, location.href); // Block back navigation
        window.onpopstate = function () {
            history.go(1);  // Prevent going back to the previous page
        };
    }
});
