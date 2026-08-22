(function (app) {
  "use strict";

  function numericCell(cell, params, decimals) {
    const value = Number(cell.getValue());
    if (!Number.isFinite(value)) return "—";
    const element = cell.getElement();
    element.classList.toggle("cell-value--negative", value < 0);
    element.classList.toggle("cell-value--positive", value > 0);
    return app.formatValue.number(value, decimals);
  }

  app.formatters.integer = function (cell) {
    return numericCell(cell, {}, 0);
  };

  app.formatters.decimal = function (cell, params) {
    return numericCell(cell, params, Number(params.decimals == null ? 2 : params.decimals));
  };

  app.formatters.percentage = function (cell, params) {
    const value = Number(cell.getValue());
    if (!Number.isFinite(value)) return "—";
    cell.getElement().classList.toggle("cell-value--negative", value < 0);
    cell.getElement().classList.toggle("cell-value--positive", value >= 0);
    return app.formatValue.number(value * 100, Number(params.decimals == null ? 1 : params.decimals)) + "%";
  };

  app.formatters.currency = function (cell, params) {
    const value = Number(cell.getValue());
    if (!Number.isFinite(value)) return "—";
    return app.helpers.escapeHtml(params.symbol || "¤") + app.formatValue.number(value, 2);
  };

  app.formatters.date = function (cell) {
    return app.formatValue.date(cell.getValue());
  };

  app.formatters.statusBadge = function (cell) {
    const raw = cell.getValue() == null ? "Unknown" : String(cell.getValue());
    const tone = {
      active: "positive",
      complete: "positive",
      pending: "warning",
      review: "info",
      paused: "danger",
    }[raw.toLowerCase()] || "neutral";
    return '<span class="table-status table-status--' + tone + '"><span></span>' + app.helpers.escapeHtml(raw) + "</span>";
  };

  app.formatters.signed = function (cell, params) {
    const value = Number(cell.getValue());
    if (!Number.isFinite(value)) return "—";
    return (value > 0 ? "+" : "") + app.formatValue.number(value, Number(params.decimals || 1));
  };
})(window.DashApp);
