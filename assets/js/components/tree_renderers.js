(function (app) {
  "use strict";
  app.tree = app.tree || {};
  app.tree.isParent = function (rowData) {
    return Array.isArray(rowData && rowData._children) && rowData._children.length > 0;
  };
})(window.DashApp);
