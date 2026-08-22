(function (app) {
  "use strict";

  function redrawTables() {
    window.requestAnimationFrame(function () {
      app.tables.forEach(function (entry) {
        if (entry && entry.table) entry.table.redraw(true);
      });
    });
  }

  document.addEventListener("click", function (event) {
    const nav = event.target.closest(".nav-item");
    if (nav) window.setTimeout(redrawTables, 80);

    const sidebarToggle = event.target.closest("#sidebar-toggle");
    if (sidebarToggle) document.documentElement.classList.toggle("sidebar-open");
    if (event.target.closest("#sidebar-overlay")) document.documentElement.classList.remove("sidebar-open");

    const themeToggle = event.target.closest("#theme-toggle");
    if (themeToggle) {
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem("dashwork-theme", next); } catch (_error) { /* optional preference */ }
      redrawTables();
    }
  });

  try {
    const stored = localStorage.getItem("dashwork-theme");
    if (stored === "dark") document.documentElement.dataset.theme = "dark";
  } catch (_error) { /* optional preference */ }

  window.addEventListener("resize", redrawTables, { passive: true });
})(window.DashApp);
