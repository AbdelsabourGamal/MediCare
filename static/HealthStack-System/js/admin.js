// ---- Admin Scripts ----

// Password visibility toggle
function togglePassword() {
  const passwordInput = document.getElementById("password");
  const showPasswordCheckbox = document.getElementById("show-password");

  if (showPasswordCheckbox.checked) {
    passwordInput.type = "text";
  } else {
    passwordInput.type = "password";
  }
}

// Navbar + Sidebar Handling :
const toggleBtn = document.getElementById("toggle_btn");
const mobileBtn = document.getElementById("mobile_btn");
const sidebar = document.getElementById("sidebar");
const mainContent = document.getElementById("mainContent");
const userDropdown = document.getElementById("userDropdown");
const userDropdownMenu = document.getElementById("userDropdownMenu");
const sidebarOverlay = document.getElementById("sidebarOverlay");


// Desktop sidebar toggle
toggleBtn.addEventListener("click", () => {
  sidebar.classList.toggle("collapsed");
});

// Mobile sidebar toggle
mobileBtn.addEventListener("click", () => {
  sidebar.classList.toggle("mobile-show");
  sidebarOverlay.classList.toggle("show");
});

// Close mobile sidebar when overlay is clicked
sidebarOverlay.addEventListener("click", () => {
  sidebar.classList.remove("mobile-show");
  sidebarOverlay.classList.remove("show");
});

// User dropdown toggle
userDropdown.addEventListener("click", (e) => {
  e.preventDefault();
  userDropdownMenu.classList.toggle("show");
});

// Close user dropdown when clicking outside
document.addEventListener("click", (e) => {
  if (!userDropdown.contains(e.target)) {
    userDropdownMenu.classList.remove("show");
  }
});

// Submenu toggles
document.querySelectorAll(".submenu > a").forEach((item) => {
  item.addEventListener("click", (e) => {
    e.preventDefault();
    const submenu = item.parentElement;
    const isCollapsed = sidebar.classList.contains("collapsed");

    // Don't open submenus when sidebar is collapsed
    if (isCollapsed) return;

    submenu.classList.toggle("open");

    // Close other open submenus
    document.querySelectorAll(".submenu").forEach((otherSubmenu) => {
      if (otherSubmenu !== submenu) {
        otherSubmenu.classList.remove("open");
      }
    });
  });
});

// Handle window resize
window.addEventListener("resize", () => {
  if (window.innerWidth > 768) {
    sidebar.classList.remove("mobile-show");
    sidebarOverlay.classList.remove("show");
  }
});

// Close mobile menu when window becomes large
const mediaQuery = window.matchMedia("(min-width: 769px)");
mediaQuery.addEventListener("change", (e) => {
  if (e.matches) {
    sidebar.classList.remove("mobile-show");
    sidebarOverlay.classList.remove("show");
  }
});

// Sidebar Active Link
