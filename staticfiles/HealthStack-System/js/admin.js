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

// Dynamic Departments, Services, and Specialization Management Script

document.addEventListener("DOMContentLoaded", function () {
  // Function to create a new department entry
  function createDepartmentEntry() {
    const departmentEntry = document.createElement("div");
    departmentEntry.className = "row form-row department-cont";
    departmentEntry.innerHTML = `
      <div class="col-12 col-md-10 col-lg-10">
          <div class="form-group">
              <input type="text" class="form-control" name="department" placeholder="Add new department" />
          </div>
      </div>
      <div class="col-12 col-md-2 col-lg-2">
          <a href="#" class="btn btn-danger trash-btn">
              <i class="far fa-trash-alt"></i>
          </a>
      </div>
  `;
    return departmentEntry;
  }

  // Function to create a new service entry
  function createServiceEntry() {
    const serviceEntry = document.createElement("div");
    serviceEntry.className = "row form-row service-cont";
    serviceEntry.innerHTML = `
      <div class="col-12 col-md-10 col-lg-10">
          <div class="form-group">
              <input type="text" class="form-control" name="service" placeholder="Add new service" />
          </div>
      </div>
      <div class="col-12 col-md-2 col-lg-2">
          <a href="#" class="btn btn-danger trash-btn">
              <i class="far fa-trash-alt"></i>
          </a>
      </div>
  `;
    return serviceEntry;
  }

  // Function to create a new specialization entry
  function createSpecializationEntry() {
    const specializationEntry = document.createElement("div");
    specializationEntry.className = "row form-row specialization-cont";
    specializationEntry.innerHTML = `
      <div class="col-12 col-md-10 col-lg-10">
          <div class="form-group">
              <input type="text" class="form-control" name="specialization" placeholder="Add new specialization" />
          </div>
      </div>
      <div class="col-12 col-md-2 col-lg-2">
          <a href="#" class="btn btn-danger trash-btn">
              <i class="far fa-trash-alt"></i>
          </a>
      </div>
  `;
    return specializationEntry;
  }

  // Add Department Entry
  const addDepartmentBtn = document.querySelector(".add-department");
  if (addDepartmentBtn) {
    addDepartmentBtn.addEventListener("click", function (e) {
      e.preventDefault();
      const departmentInfo = document.querySelector(".department-info");
      const newDepartmentEntry = createDepartmentEntry();
      departmentInfo.appendChild(newDepartmentEntry);
    });
  }

  // Add Service Entry
  const addServiceBtn = document.querySelector(".add-service");
  if (addServiceBtn) {
    addServiceBtn.addEventListener("click", function (e) {
      e.preventDefault();
      const serviceInfo = document.querySelector(".service-info");
      const newServiceEntry = createServiceEntry();
      serviceInfo.appendChild(newServiceEntry);
    });
  }

  // Add Specialization Entry
  const addSpecializationBtn = document.querySelector(".add-specialization");
  if (addSpecializationBtn) {
    addSpecializationBtn.addEventListener("click", function (e) {
      e.preventDefault();
      const specializationInfo = document.querySelector(".specialization-info");
      const newSpecializationEntry = createSpecializationEntry();
      specializationInfo.appendChild(newSpecializationEntry);
    });
  }

  // Delete Entry (using event delegation for dynamically added elements)
  document.addEventListener("click", function (e) {
    if (e.target.closest(".trash-btn")) {
      e.preventDefault();
      const trashBtn = e.target.closest(".trash-btn");
      const entryToDelete = trashBtn.closest(
        ".department-cont, .service-cont, .specialization-cont"
      );

      if (entryToDelete) {
        // Check which type of entry this is
        const isDepartmentEntry =
          entryToDelete.classList.contains("department-cont");
        const isServiceEntry = entryToDelete.classList.contains("service-cont");
        const isSpecializationEntry = entryToDelete.classList.contains(
          "specialization-cont"
        );

        // Count remaining entries of the same type
        let remainingEntries;
        if (isDepartmentEntry) {
          remainingEntries =
            document.querySelectorAll(".department-cont").length;
        } else if (isServiceEntry) {
          remainingEntries = document.querySelectorAll(".service-cont").length;
        } else if (isSpecializationEntry) {
          remainingEntries = document.querySelectorAll(
            ".specialization-cont"
          ).length;
        }

        // Only allow deletion if there will be at least 1 entry remaining
        if (remainingEntries > 1) {
          entryToDelete.remove();
        } else {
          alert("At least one entry must remain.");
        }
      }
    }
  });
});
