(function () {
  "use strict";
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;
    const close = document.querySelector(".modal:not([hidden]) [id$='close-modal']");
    if (close) close.click();
  });
})();
