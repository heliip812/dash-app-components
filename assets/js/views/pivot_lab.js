(function () {
  "use strict";
  document.addEventListener("dashwork:tree-toggle", function () {
    document.documentElement.classList.add("tree-interaction-ready");
  }, { once: true });
})();
