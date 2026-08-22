(function (app) {
  "use strict";

  app.helpers.escapeHtml = function (value) {
    const element = document.createElement("span");
    element.textContent = value == null ? "" : String(value);
    return element.innerHTML;
  };

  app.helpers.deepClone = function (value) {
    return value == null ? value : JSON.parse(JSON.stringify(value));
  };
})(window.DashApp);
