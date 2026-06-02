(function () {
  "use strict";

  function copyUPI(upiId) {
    if (!navigator.clipboard) return;
    navigator.clipboard.writeText(upiId).then(function () {
      var toast = document.getElementById("toast");
      if (toast) {
        toast.textContent = "✓ UPI ID copied!";
        toast.classList.add("show");
        setTimeout(function () {
          toast.classList.remove("show");
        }, 2500);
      }
    });
  }

  function initCopyButtons() {
    document.querySelectorAll("[data-copy-upi]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        copyUPI(btn.getAttribute("data-copy-upi"));
      });
    });
  }

  function initMobileNav() {
    var toggle = document.querySelector(".nav-toggle");
    var links = document.querySelector(".nav-links");
    if (!toggle || !links) return;
    toggle.addEventListener("click", function () {
      links.classList.toggle("open");
    });
  }

  function initWhatsAppWidget() {
    var toggle = document.getElementById("wa-widget-toggle");
    var popup = document.getElementById("wa-popup");
    var closeBtn = document.getElementById("wa-popup-close");
    if (!toggle || !popup) return;

    toggle.addEventListener("click", function () {
      popup.hidden = !popup.hidden;
    });
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        popup.hidden = true;
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    initCopyButtons();
    initMobileNav();
    initWhatsAppWidget();
  });
})();
