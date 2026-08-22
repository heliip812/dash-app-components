(function () {
  "use strict";
  document.addEventListener("dashwork:table-selection", function (event) {
    if (event.detail.tableId === "standard-table") {
      document.body.dataset.lastSelectedTable = "standard-table";
    }
  });
})();
