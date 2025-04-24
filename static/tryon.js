
  // Image Preview on Form Submit
  document.getElementById('tryon-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const fileInput = document.getElementById('user-image');
    const preview = document.getElementById('generated-image');

    if (fileInput.files && fileInput.files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        preview.src = e.target.result;
      };
      reader.readAsDataURL(fileInput.files[0]);
    }
  });

  // Fetch and update clothing options based on selected category
  async function fetchOptions() {
    const category = document.getElementById("category").value;

    try {
      const response = await fetch(`/update_options?category=${category}`);
      const data = await response.json();

      const parts = ["shirt", "pants", "jacket", "hat"];
      parts.forEach(part => {
        updateSelect(`${part}_color`, data.color_options);
        updateSelect(`${part}_pattern`, data.pattern_options);
        updateSelect(`${part}_type`, data.type_options);
      });

    } catch (error) {
      console.error("Error loading options:", error);
    }
  }

  // Update a specific select dropdown with options
  function updateSelect(id, options) {
    const select = document.getElementById(id);
    select.innerHTML = "";
    options.forEach(opt => {
      const option = document.createElement("option");
      option.value = opt;
      option.text = opt;
      select.appendChild(option);
    });
  }

  // Show/hide style sections based on selected clothing items
  function updateStyleSections() {
    const change = document.getElementById("change").value;

    document.getElementById("shirt-style").style.display = change.includes("Shirt") ? "block" : "none";
    document.getElementById("pants-style").style.display = change.includes("Pants") ? "block" : "none";
    document.getElementById("jacket-style").style.display = change.includes("Jacket") ? "block" : "none";
    document.getElementById("hat-style").style.display = change.includes("Hat") ? "block" : "none";
  }

  // Initialize when page loads
  window.addEventListener("load", () => {
    fetchOptions();
    updateStyleSections();
  });
