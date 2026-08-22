(function (app) {
  "use strict";

  function resolveColumns(columns) {
    return (columns || []).map(function (source) {
      const column = app.helpers.deepClone(source);
      if (Array.isArray(column.columns)) column.columns = resolveColumns(column.columns);
      if (typeof column.formatter === "string" && column.formatter.indexOf("dash:") === 0) {
        const formatter = app.formatters[column.formatter.slice(5)];
        if (formatter) column.formatter = formatter;
      }
      return column;
    });
  }

  function resolveOptions(source) {
    const options = app.helpers.deepClone(source || {});
    if (options.dataTreeToggleStyle === "chevron") {
      options.dataTreeExpandElement = app.chevrons.expand;
      options.dataTreeCollapseElement = app.chevrons.collapse;
      delete options.dataTreeToggleStyle;
    }
    return options;
  }

  function signature(config) {
    return JSON.stringify({ columns: config.columns || [], options: config.options || {} });
  }

  function create(config) {
    const host = document.getElementById(config.hostId);
    if (!host || !window.Tabulator) return null;
    host.replaceChildren();
    const options = resolveOptions(config.options);
    options.data = config.data || [];
    options.columns = resolveColumns(config.columns);
    const table = new window.Tabulator(host, options);
    app.tableEvents.bind(table, config);
    const entry = { table: table, signature: signature(config) };
    app.tables.set(config.hostId, entry);
    return entry;
  }

  function upsert(config) {
    if (!config || !config.hostId) return "Tabulator configuration missing";
    const existing = app.tables.get(config.hostId);
    if (!existing) {
      const created = create(config);
      return created ? "Interactive data table ready" : "Waiting for Tabulator";
    }
    if (existing.signature !== signature(config)) {
      existing.table.destroy();
      app.tables.delete(config.hostId);
      create(config);
      return "Interactive data table reconfigured";
    }
    existing.table.replaceData(config.data || []).then(function () {
      existing.table.redraw(true);
    });
    return "Interactive data table updated";
  }

  window.dash_clientside = Object.assign({}, window.dash_clientside, {
    dashApp: Object.assign({}, (window.dash_clientside || {}).dashApp, {
      syncTabulator: function (config) {
        if (!window.Tabulator) {
          window.setTimeout(function () { upsert(config); }, 150);
          return "Loading interactive table";
        }
        return upsert(config);
      },
    }),
  });
})(window.DashApp);
