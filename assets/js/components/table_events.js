(function (app) {
  "use strict";

  app.tableEvents.bind = function (table, config) {
    const host = document.getElementById(config.hostId);
    const selectionId = host && host.dataset.selectionId;
    table.on("rowSelectionChanged", function (data) {
      if (selectionId && window.dash_clientside && window.dash_clientside.set_props) {
        window.dash_clientside.set_props(selectionId, { data: data || [] });
      }
      document.dispatchEvent(new CustomEvent("dashwork:table-selection", {
        detail: { tableId: config.hostId, rows: data || [] },
      }));
    });
    table.on("dataTreeRowExpanded", function (row) {
      document.dispatchEvent(new CustomEvent("dashwork:tree-toggle", {
        detail: { tableId: config.hostId, row: row.getData(), expanded: true },
      }));
    });
    table.on("dataTreeRowCollapsed", function (row) {
      document.dispatchEvent(new CustomEvent("dashwork:tree-toggle", {
        detail: { tableId: config.hostId, row: row.getData(), expanded: false },
      }));
    });
  };
})(window.DashApp);
