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

// ======Signup form======
signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("signupEmail").value.trim();
    const password = document.getElementById("signupPassword").value.trim();
    const full_name = document.getElementById("signupFullName").value.trim();  // Assuming you have a full name input field
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
document.addEventListener("DOMContentLoaded", () => {
    const testimonials = document.querySelectorAll(".testimonial-card");
    const prevBtn = document.querySelector(".prev-arrow");
    const nextBtn = document.querySelector(".next-arrow");
    let currentIndex = 0;

    // Show testimonial
    const showTestimonial = (index) => {
        testimonials.forEach((testimonial, i) => {
            testimonial.classList.toggle("active", i === index);
        });
    };

    // Auto-rotate every 5s
    let autoSlide = setInterval(() => {
        currentIndex = (currentIndex + 1) % testimonials.length;
        showTestimonial(currentIndex);
    }, 5000);

    // Manual navigation
    prevBtn.addEventListener("click", () => {
        clearInterval(autoSlide);
        currentIndex = (currentIndex - 1 + testimonials.length) % testimonials.length;
        showTestimonial(currentIndex);
    });

    nextBtn.addEventListener("click", () => {
        clearInterval(autoSlide);
        currentIndex = (currentIndex + 1) % testimonials.length;
        showTestimonial(currentIndex);
    });

    // Initialize
    showTestimonial(currentIndex);
});

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