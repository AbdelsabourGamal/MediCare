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

// Hospital Carousel

const hospitalCarousel = document.querySelector("#hospitalCarousel");
const carousel = new bootstrap.Carousel(hospitalCarousel, {
  interval: 2000,
  ride: "carousel",
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
