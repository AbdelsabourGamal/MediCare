var loader_script =
  '<div id="pre-loader">' +
  '<div class="spinner-border text-primary" role="status">' +
  '<span class="sr-only">Loading...</span>' +
  "</div>" +
  "</div>";
window.start_loader = function () {
  if ($("body>#pre-loader").length <= 0) {
    $("body").append(loader_script);
  }
};
window.end_loader = function () {
  var loader = $("body>#pre-loader");
  if (loader.length > 0) {
    loader.remove();
  }
};

// Navbar Slider

document.addEventListener("DOMContentLoaded", function () {
  const mobileBtn = document.getElementById("mobile_btn");
  const menuWrapper = document.querySelector(".main-menu-wrapper");
  const menuClose = document.getElementById("menu_close");

  // Show menu on mobile button click
  mobileBtn.addEventListener("click", function (e) {
    e.stopPropagation(); // prevent bubbling
    menuWrapper.classList.add("menu-visible");
  });

  // Close menu on close icon click
  menuClose.addEventListener("click", function () {
    menuWrapper.classList.remove("menu-visible");
  });

  // Close menu when clicking outside
  document.addEventListener("click", function (e) {
    if (
      menuWrapper.classList.contains("menu-visible") &&
      !menuWrapper.contains(e.target) &&
      !mobileBtn.contains(e.target)
    ) {
      menuWrapper.classList.remove("menu-visible");
    }
  });

  // Remove class on window resize > 992px
  window.addEventListener("resize", function () {
    if (window.innerWidth > 992) {
      menuWrapper.classList.remove("menu-visible");
    }
  });
});

// Active Link

document.addEventListener("DOMContentLoaded", function () {
  const currentPath = window.location.pathname.replace(/\/+$/, "");
  const links = document.querySelectorAll(".sidebar li a");

  links.forEach((link) => {
    const href = link.getAttribute("href");
    if (!href) return;

    const temp = document.createElement("a");
    temp.href = href;

    if (!temp.pathname) return;

    const linkPath = temp.pathname.replace(/\/+$/, "");

    if (linkPath === currentPath) {
      const li = link.closest("li");
      if (li) {
        li.classList.add("active");
      }
    }
  });
});

// Table Tabs Handling
document.querySelectorAll(".tab-trigger").forEach((trigger) => {
  trigger.addEventListener("click", function () {
    const targetId = this.getAttribute("data-pat-tab");

    // Hide all tab panes
    document.querySelectorAll(".tab-pane").forEach((tab) => {
      tab.classList.remove("show", "active");
    });

    // Show the selected tab pane
    const target = document.getElementById(targetId);
    if (target) {
      target.classList.add("show", "active");
    }
  });
});

// Show Password
function showPass() {
  var x = document.getElementById("myInput");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}

// Dynamic Medicine and Test Entry Management Script

document.addEventListener("DOMContentLoaded", function () {
  // Function to create a new medicine entry
  function createMedicineEntry() {
    const medicineEntry = document.createElement("div");
    medicineEntry.className = "medicine-entry";
    medicineEntry.innerHTML = `
    <div class="row">
        <div class="col-12">
            <div class="row">
                <!-- Medicine Fields -->
                <div class="col-12 col-md-6 col-lg-3 form-group">
                    <label>Medicine Name</label>
                    <input type="text" class="form-control" name="medicine_name" required />
                </div>

                <div class="col-12 col-md-6 col-lg-3 form-group">
                    <label>Quantity</label>
                    <input type="text" class="form-control" name="quantity" required />
                </div>

                <div class="col-12 col-md-6 col-lg-3 form-group">
                    <label>Frequency</label>
                    <input type="text" class="form-control" name="frequency" required />
                </div>

                <div class="col-12 col-md-6 col-lg-3 form-group">
                    <label>Relation with meal</label>
                    <input type="text" class="form-control" name="relation_with_meal" />
                </div>

                <div class="col-12 col-md-6 col-lg-6 form-group">
                    <label>Duration</label>
                    <input type="text" class="form-control" name="duration" required />
                </div>

                <div class="col-12 col-md-6 col-lg-6 form-group">
                    <label>Instruction</label>
                    <input type="text" class="form-control" name="instruction" />
                </div>
            </div>
        </div>

        <!-- Delete Button -->
        <div class="col-12 col-md-2 col-lg-1 d-flex align-items-end">
            <button type="button" class="btn btn-danger btn-block delete-item">
                <i class="far fa-trash-alt"></i>
            </button>
        </div>
    </div>
`;
    return medicineEntry;
  }

  // Function to create a new test entry
  function createTestEntry() {
    const testEntry = document.createElement("div");
    testEntry.className = "test-entry";
    testEntry.innerHTML = `
    <div class="row">
        <div class="col-12">
            <div class="row">
                <!-- Test Fields -->
                <div class="col-12 col-md-5 col-lg-5 form-group">
                    <label>Test Name</label>
                    <input type="text" class="form-control" name="test_name" required />
                </div>

                <div class="col-12 col-md-5 col-lg-5 form-group">
                    <label>Description</label>
                    <input type="text" class="form-control" name="description" />
                </div>

                <div class="col-12 col-md-2 col-lg-2 form-group">
                    <label>ID</label>
                    <input type="number" class="form-control" name="id" min="0" />
                </div>
            </div>
        </div>

        <!-- Delete Button -->
        <div class="col-12 col-md-2 col-lg-1">
            <button type="button" class="btn btn-danger btn-block delete-item">
                <i class="far fa-trash-alt"></i>
            </button>
        </div>
    </div>
`;
    return testEntry;
  }

  // Add Medicine Entry
  const addMedicineBtn = document.querySelector(".add-medicine .add-item");
  if (addMedicineBtn) {
    addMedicineBtn.addEventListener("click", function () {
      const medicineSection = document.querySelector(
        ".medicine-section .card-body"
      );
      const addMedicineDiv = document.querySelector(".add-medicine");
      const newMedicineEntry = createMedicineEntry();

      // Insert the new entry before the "Add Medicine" button
      medicineSection.insertBefore(newMedicineEntry, addMedicineDiv);
    });
  }

  // Add Test Entry
  const addTestBtn = document.querySelector(".add-test .add-item");
  if (addTestBtn) {
    addTestBtn.addEventListener("click", function () {
      const testSection = document.querySelector(".test-section .card-body");
      const addTestDiv = document.querySelector(".add-test");
      const newTestEntry = createTestEntry();

      // Insert the new entry before the "Add Test" button
      testSection.insertBefore(newTestEntry, addTestDiv);
    });
  }

  // Delete Entry (using event delegation for dynamically added elements)
  document.addEventListener("click", function (e) {
    if (e.target.closest(".delete-item")) {
      const deleteBtn = e.target.closest(".delete-item");
      const entryToDelete = deleteBtn.closest(".medicine-entry, .test-entry");

      if (entryToDelete) {
        // Check if this is a medicine or test entry
        const isMedicineEntry =
          entryToDelete.classList.contains("medicine-entry");
        const isTestEntry = entryToDelete.classList.contains("test-entry");

        // Count remaining entries of the same type
        let remainingEntries;
        if (isMedicineEntry) {
          remainingEntries =
            document.querySelectorAll(".medicine-entry").length;
        } else if (isTestEntry) {
          remainingEntries = document.querySelectorAll(".test-entry").length;
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
