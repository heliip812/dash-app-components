# Dashwork: reusable Dash application foundation

Dashwork is a generic, single-URL analytical workstation and component sandbox for Plotly Dash. It is designed for large static pandas DataFrames, Python-side transformation and aggregation, MIT-licensed Tabulator tables, reusable Plotly figures, and UI development that does not collapse into giant callback, CSS, or JavaScript files.

It contains five always-mounted views:

- **Overview** — generic metrics, cross-filter controls, two charts, and recent records.
- **Table Lab** — standard, hierarchical, selection-detail, and large-data tables.
- **Pivot Lab** — configurable pandas pivoting rendered as both Tabulator and Plotly.
- **Visualisation Lab** — reusable line, bar, scatter, and heatmap builders.
- **Component Gallery** — independent specimens for buttons, forms, cards, feedback, modal, tables, and charts.

No AG Grid, Dash AG Grid, Dash Pages, route-based views, commercial grid, paid UI kit, or Dash Enterprise feature is used.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:8050/`. The WSGI entry point is `app:server`:

```bash
gunicorn app:server
```

The first startup generates `data/sample/sample_records.parquet` deterministically when it is absent. Subsequent starts read that Parquet file once per Python worker.

## Architecture

```text
dash-app-components/
├── app.py                         # development and WSGI entry point
├── requirements.txt
├── assets/
│   ├── css/
│   │   ├── global/                # tokens, reset, typography, layout, utilities
│   │   ├── components/            # one reusable component family per file
│   │   ├── views/                 # view-only placement/polish
│   │   └── vendor/                # narrow Tabulator/Plotly overrides
│   └── js/
│       ├── global/                # generic formatting and browser events
│       ├── components/            # Tabulator bridge, formatters, events, chevrons
│       └── views/                 # minimal view-only browser behaviour
├── data/sample/                   # generated deterministic Parquet data
├── scripts/                       # explicit sample-data generation
├── src/
│   ├── app_factory.py             # composition root and injected services
│   ├── callbacks/                 # explicit callback registration
│   ├── components/                # reusable Python UI factories
│   ├── data/                      # loaders, registry, cache, bootstrap
│   ├── figures/                   # reusable Plotly builders
│   ├── layout/                    # shell, sidebar, topbar
│   ├── navigation/                # state-based navigation config/callback
│   ├── services/                  # workflow/orchestration layers
│   ├── transformations/           # pure pandas transformations
│   ├── utils/                     # IDs, paths, validation, formatting, timing
│   └── views/                     # layout/callback/config per mounted view
└── tests/                          # data, transformation, component, callback, app tests
```

The app factory is the composition root. It owns one `DataFrameRegistry`, constructs services around it, builds the shell once, and injects the services into view layouts and callback registration. This avoids module-level mutable datasets while making the process lifetime explicit.

## Data flow

```text
Data source
    ↓
CSV / Parquet / Feather loader
    ↓
DataFrameRegistry (process-local, loaded once)
    ↓
DataFrameService / PivotService
    ↓
pure transformation
    ↓
structured, compact result
    ├── TableService → Tabulator config
    └── figure builder → Plotly figure
                    ↓
                thin callback
                    ↓
                    UI
```

Browser state is intentionally small:

```text
Browser UI state
    ↓
dcc.Store
    ↓
active view, compact table config, selected records, filters

Large DataFrame
    ↓
server-side DataFrameRegistry
    ↓
never stored in dcc.Store
```

The table-config stores contain only browser-bound result slices, not the registry DataFrame. The 75,000-row demonstration table filters and sorts on the server, caps transfer at 2,500 records, then lets Tabulator paginate and virtually render that compact result.

## Single-page navigation

Dash Pages and `dcc.Location` are deliberately absent. The sidebar buttons update `dcc.Store(id="active-view")`; the navigation callback changes only the active view class, active nav class, title, and eyebrow. Every view remains mounted:

```text
One Dash app at /
├── Sidebar buttons
├── Topbar
└── Workspace
    ├── Overview            .app-view--active
    ├── Table Lab           .app-view
    ├── Pivot Lab           .app-view
    ├── Visualisation Lab   .app-view
    └── Component Gallery   .app-view
```

CSS applies `display: none` to `.app-view` and `display: block` to `.app-view--active`. Switching views does not alter the URL and does not rebuild a layout through one giant `content.children` callback. When a hidden view becomes active, a small browser event requests a Tabulator redraw so column widths remain correct.

## DataFrame loading and registry

`src/data/loaders/` provides explicit CSV, Parquet, Feather, and suffix-dispatching loaders. Parquet is the primary demonstration format because it preserves useful types and supports column projection and compact storage.

`DataFrameRegistry` is thread-safe and returns the registered DataFrame object without copying it. Consumers must treat that object as immutable. Transformations create derived selections only when necessary. Metadata records rows, columns, memory size, source, registration time, and app-specific attributes.

The default registry is process-local. This keeps local development simple and dependency-free. With multiple Gunicorn workers, each worker loads its own copy; use memory mapping, a shared analytical database, or an external cache only when deployment scale warrants the extra infrastructure.

## Transformations

Pure functions live under `src/transformations/` and contain no Dash imports:

- `filter_dataframe(...)` — `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `contains`, `in`, and `between`.
- `sort_dataframe(...)` — stable multi-column sorting.
- `select_columns(...)` — validated projection.
- `group_dataframe(...)` — group and named aggregation to a regular frame.
- `aggregate_dataframe(...)` — whole-frame aggregation to one row.
- `pivot_dataframe(...)` — pandas pivot with `sum`, `mean`, `count`, `min`, and `max`.
- `build_hierarchy(...)` — multi-level group recursion to nested `_children` records.
- `flatten_hierarchy(...)` — depth-annotated flat records for export or tests.

Callbacks translate UI state into service requests. Services orchestrate transformations. Neither callbacks nor services define HTML layout.

## Pivot architecture

`PivotRequest` contains dataset ID, row dimensions, column dimensions, value, aggregation, and lightweight filter configuration. `PivotService` filters the registry frame, calls `pivot_dataframe`, caches the compact result in a bounded in-process cache, and returns a `PivotResult` with both a table frame and numeric matrix. The result is presentation-neutral: Pivot Lab sends it to both `TableService` and either the bar or heatmap figure builder.

## Hierarchy and expandable rows

`build_hierarchy` recursively groups any sequence of dimension columns. Each node receives a stable path ID, label, depth, record count, requested aggregates, and optional `_children`. Tabulator Data Tree reads that structure directly.

`tree_table_options()` enables `dataTree`, chooses `_children`, sets indentation, controls initial expansion by level, and asks the JavaScript bridge to substitute original chevron elements. Tree filtering, sorting, selection, expansion, collapse, and level-specific styling are provided by the free Tabulator Data Tree module.

## Tabulator integration

Tabulator 6.3.1 is pinned from the official UNPKG distribution. Python creates only structured data, columns, and options. `assets/js/components/tabulator_factory.js` resolves named formatter tokens such as `dash:percentage`, creates or updates the table, and retains an instance registry. Data-only updates use `replaceData`; changed column/options signatures rebuild the relevant table only.

Selection events call Dash's client-side `set_props` API to update the corresponding lightweight selection store. The Table Lab callback then retrieves the selected stable record ID from the server registry and updates metadata, related records, and a Plotly chart.

Implemented table capabilities:

- sorting, header filtering, column resizing, frozen columns, pagination, and selection;
- numeric, integer, percentage, date, status-badge, signed, and currency-like formatters;
- positive/negative styling and reusable status tones;
- local virtual rendering for capped large results;
- nested `_children`, multiple tree levels, custom chevrons, indentation, and level styling;
- selection-to-detail and selection-to-chart interaction;
- table option and column composition without inline JavaScript strings.

### Add a formatter

1. Add a named function to `assets/js/components/table_formatters.js`.
2. Reference it as `formatter="dash:yourName"` in a Python column builder.
3. Add component tests for the emitted structured configuration.

### Add a column builder

Add one focused function to `src/components/tables/column_builders.py`, compose it from `_column`, and return JSON-safe Tabulator configuration only. Add a test in `tests/components/`.

## Plotly figures

`src/figures/` contains generic `build_line_figure`, `build_bar_figure`, `build_scatter_figure`, and `build_heatmap_figure` functions plus shared layout/formatting. `VisualisationService` prepares small grouped or sampled frames and calls these builders. Callbacks do not contain large Plotly construction blocks.

## CSS, JavaScript, and Python boundaries

- `assets/css/global/` owns tokens, reset, typography, app layout, and utilities.
- `assets/css/components/` owns reusable component selectors.
- `assets/css/views/` owns only view-specific layout adjustments.
- `assets/css/vendor/` owns narrow overrides of external libraries.
- `assets/js/global/` owns generic browser helpers, formatting, theme, responsive shell events.
- `assets/js/components/` owns Tabulator creation, named formatters, chevrons, table events, modal, and tooltip helpers.
- `assets/js/views/` remains intentionally tiny and contains no DataFrame logic.
- `src/components/` contains reusable Dash component factories.
- `src/views/<view>/` contains only that view's config, layout, and callback wiring.

CSS Cascade Layers establish deterministic reset/token/layout/component/view ordering even though Dash recursively discovers assets. Vendor overrides are intentionally unlayered so they can override the external Tabulator stylesheet loaded before local assets.

## Extension recipes

### Add a view

1. Create `src/views/<name>/{config.py,layout.py,callbacks.py}`.
2. Add one `NavItem` in `src/navigation/config.py`.
3. Mount the layout in `src/layout/app_shell.py`.
4. Register its callbacks and table bridge IDs in `src/callbacks/register.py`.
5. Add only unique placement rules in `assets/css/views/<name>.css`.

### Add a reusable component

Add a focused module under the appropriate `src/components/` family, define stable BEM-style classes, and style the component in one matching file under `assets/css/components/`. Demonstrate it independently in Component Gallery before composing it into a view.

### Add a transformation

Add a pure function under `src/transformations/`, validate requested columns, avoid mutation of the input frame, export it from `src/transformations/__init__.py`, and add focused tests.

### Add a figure builder

Add a small presentation-only module in `src/figures/`, reuse `apply_base_layout`, define an empty-data path, export it from `src/figures/__init__.py`, and call it from a service.

### Add view-specific JavaScript

Only add `assets/js/views/<name>.js` when behaviour cannot reasonably live in Dash or a reusable component module. Core filtering, aggregation, pivoting, and hierarchy construction stay in Python.

Search for `APPLICATION-SPECIFIC FUNCTION GOES HERE` to find the intended extension seams.

## Performance choices

- generate/read Parquet once and retain the DataFrame server-side;
- use categorical dtypes for repeating dimensions;
- filter before grouping or pivoting;
- cache compact pivot results, not arbitrary full-frame copies;
- use stable `record_id` and hierarchy path IDs;
- project columns and cap rows before browser transfer;
- let Tabulator paginate and virtually render browser-bound slices;
- use `replaceData` for data-only updates instead of rebuilding a table;
- sample the scatter plot and aggregate line/bar/heatmap inputs;
- provide `timer(...)` for lightweight performance logging;
- avoid Redis, Celery, or a database in the default local setup.

## Dependencies and licences

Every required feature is available free of charge in the listed open-source package. No paid or enterprise-only API is called.

| Dependency | Purpose | Licence | Free functionality used |
|---|---|---|---|
| Dash | reactive Python web application | MIT | layouts, callbacks, stores, client-side callbacks, assets |
| Plotly.py / Plotly.js | line, bar, scatter, heatmap | MIT | all chart builders in this project |
| pandas | filtering, grouping, aggregation, pivoting | BSD-3-Clause | all server-side DataFrame work |
| NumPy | deterministic synthetic sample generation | BSD-3-Clause | random generator and numeric arrays |
| PyArrow | Parquet and Feather IO | Apache-2.0 | full local file loading/writing |
| Tabulator 6.3.1 | interactive tables and Data Tree | MIT | sorting, filtering, pagination, virtual DOM, selection, formatting, tree rows |
| Gunicorn | optional production WSGI server | MIT | standard process serving |
| pytest | test runner | MIT | repository test suite |

Tabulator is loaded from a pinned CDN URL rather than an npm/Python wrapper. For offline or air-gapped deployment, vendor the official `tabulator.min.js` and `tabulator.min.css` distribution into `assets/vendor/` and replace the two constants in `src/app_factory.py`; retain Tabulator's MIT licence notice.

## Open-source design research and attribution

The following upstream repositories and their documentation were inspected before implementation:

- [Tabulator](https://github.com/tabulator-tables/tabulator) — MIT. Data Tree `_children`, custom expand/collapse elements, events, selection, filtering, pagination, and Virtual DOM concepts informed the thin bridge.
- [Plotly Dash](https://github.com/plotly/dash) — MIT. Declarative components, explicit callbacks, asset discovery, and client-side callback patterns informed application wiring.
- [Dash Sample Apps](https://github.com/plotly/dash-sample-apps) — MIT. Cross-filtering and analytical layout composition were reviewed at a pattern level.
- [Gentelella](https://github.com/ColorlibHQ/gentelella) — MIT. Its separated dashboard shell, sidebar, cards, tables, and form families informed component taxonomy.
- [AdminLTE](https://github.com/ColorlibHQ/AdminLTE) — MIT. Its consistent app shell and reusable admin-component vocabulary informed information density and navigation grouping.

No source code or theme stylesheet was copied from those repositories. The implementation is original. The specific adapted concepts are public APIs and high-level patterns: Tabulator's documented `_children` record shape and configuration names; Dash's documented assets and client-side callback mechanisms; and the general sidebar/topbar/workspace composition common to the inspected MIT admin templates.

## Tests

Run:

```bash
pytest -q
```

The suite covers CSV and Parquet loading, format dispatch, registry identity and replacement rules, filtering operators, stable sorting, projection, grouping, aggregation, all required pivot aggregations, hierarchy construction and flattening, numeric formatters, column builders, option composition, service orchestration, state navigation, always-mounted views, absence of `dcc.Location`, Tabulator bridge registration, load-once metadata, and asset segregation.

## Limitations

- The default registry and pivot cache are per Python process, not shared across Gunicorn workers.
- The browser needs network access to UNPKG for Tabulator unless its official distribution is vendored locally.
- Large-table filtering demonstrates server-side filtering with a capped result, not a remote-pagination HTTP endpoint.
- The thin bridge is intentionally not a compiled React component, so it uses a paired Dash store and client-side `set_props` for selection events.
- End-to-end browser tests are not part of the pytest suite; use a browser automation layer for release smoke tests.

## Recommended next steps

1. Replace synthetic sample generation at the documented service/data seam.
2. Vendor pinned Tabulator assets if offline reliability or strict CSP is required.
3. Add a server-side page request model if a view must navigate tens of millions of records.
4. Add deployment-specific cache/storage only after profiling shows the process-local design is insufficient.
5. Add Playwright smoke tests for view switching, tree chevrons, selection-to-chart, and mobile sidebar behaviour.
