# Building a selectable, expandable hierarchy table in Dash

This guide explains how to let a user choose an ordered list of DataFrame
columns, group the data in that order, calculate aggregate values for every
level, and render the result as an expandable Tabulator Data Tree.

It can be given directly to a coding agent as an implementation specification.
The design is generic and should work with local DataFrames, S3 Parquet data,
or any other connector that ultimately registers a pandas DataFrame.

## 1. Mental model

Suppose the source DataFrame contains:

~~~text
region | country | customer | product | revenue | quantity
~~~

The user selects these hierarchy columns in this exact order:

~~~text
1. region
2. country
3. customer
~~~

The server interprets that selection as:

~~~text
group by region
  -> within each region, group by country
       -> within each country, group by customer
~~~

If the user instead selects:

~~~text
1. product
2. region
~~~

the hierarchy becomes:

~~~text
group by product
  -> within each product, group by region
~~~

The selected columns are therefore an **ordered path**, not an unordered set.
Changing the order changes the hierarchy.

At every node, calculate the requested measures from all source rows below that
node. For example:

- revenue = sum;
- quantity = sum;
- record_count = number of source rows.

The final Python result is a nested list of dictionaries. Tabulator recognizes
child rows through the reserved field named _children.

## 2. End-to-end data flow

~~~text
Registered server-side DataFrame
  -> apply active filters
  -> validate selected hierarchy columns
  -> validate measure columns and aggregation functions
  -> recursively group in the selected order
  -> calculate node aggregates
  -> create stable node IDs
  -> emit nested dictionaries with _children
  -> build a compact Tabulator configuration
  -> update the table configuration store
  -> JavaScript bridge calls Tabulator
  -> user expands and collapses rows
~~~

Do not put the full source DataFrame in dcc.Store. Keep it in a server-side
registry and send only the resulting hierarchy tree to the browser.

## 3. User controls

At minimum, the view needs:

- an ordered hierarchy-column selector;
- a measure-column selector;
- an aggregation-function selector;
- optional dataset and filter controls;
- an initial expansion-depth control;
- an Apply or Rebuild button;
- validation and result-size feedback.

### Simple ordered multi-select

Dash's multi-value Dropdown can be used for the first implementation. The
order of values in its value list is the hierarchy order.

~~~python
from dash import dcc, html


def hierarchy_controls(dimension_columns, measure_columns):
    return html.Div(
        [
            dcc.Dropdown(
                id="hierarchy-levels",
                options=[
                    {"label": humanize(column), "value": column}
                    for column in dimension_columns
                ],
                value=dimension_columns[:3],
                multi=True,
                clearable=True,
                placeholder="Choose hierarchy levels in order",
            ),
            dcc.Dropdown(
                id="hierarchy-measure",
                options=[
                    {"label": humanize(column), "value": column}
                    for column in measure_columns
                ],
                value=measure_columns[0] if measure_columns else None,
                clearable=False,
            ),
            dcc.Dropdown(
                id="hierarchy-operation",
                options=[
                    {"label": "Sum", "value": "sum"},
                    {"label": "Average", "value": "mean"},
                    {"label": "Minimum", "value": "min"},
                    {"label": "Maximum", "value": "max"},
                    {"label": "Count", "value": "count"},
                    {"label": "Unique count", "value": "nunique"},
                ],
                value="sum",
                clearable=False,
            ),
            dcc.Dropdown(
                id="hierarchy-expanded-depth",
                options=[
                    {"label": "Collapsed", "value": 0},
                    {"label": "First level", "value": 1},
                    {"label": "First two levels", "value": 2},
                    {"label": "All levels", "value": -1},
                ],
                value=1,
                clearable=False,
            ),
            html.Button("Build hierarchy", id="hierarchy-apply", n_clicks=0),
            html.Div(id="hierarchy-feedback", role="status"),
        ],
        className="hierarchy-controls",
    )
~~~

The helper humanize can turn customer_id into Customer ID for display. The
option value must remain the exact DataFrame column name.

### Better ordering experience

A multi-select makes adding levels simple, but reordering selected values can
be awkward. For a polished application, show two distinct concepts:

~~~text
Available dimensions                  Selected hierarchy
--------------------                  ------------------
region                         ->      1. region       [up] [down] [remove]
country                                2. country      [up] [down] [remove]
customer                               3. customer     [up] [down] [remove]
product
status
~~~

Store the selected hierarchy as an ordered list:

~~~python
["region", "country", "customer"]
~~~

Up/down actions only reorder this small list. The server must still validate
every value against the registered dataset schema. Never trust column names
merely because they came from browser state.

If drag-and-drop is added, keep it as a small reusable browser component. The
canonical result passed to Python remains an ordered list of column names.

## 4. Choosing eligible columns

Do not blindly offer every source column for every purpose. Build column
metadata when the DataFrame is registered.

Recommended classification:

- **dimensions**: strings, categories, booleans, low-cardinality integers,
  date periods, or explicitly configured fields;
- **measures**: numeric columns and explicitly configured calculated measures;
- **identifiers**: stable keys, normally excluded from high-level hierarchy
  choices unless explicitly enabled;
- **hidden/sensitive**: never offered to the UI;
- **unsupported**: nested objects, raw binary values, or unnormalized structures.

Example:

~~~python
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)


def classify_columns(frame, *, hidden=(), identifiers=()):
    hidden = set(hidden)
    identifiers = set(identifiers)
    dimensions = []
    measures = []

    for column in frame.columns:
        if column in hidden:
            continue

        series = frame[column]
        if is_numeric_dtype(series.dtype) and column not in identifiers:
            measures.append(column)

        is_dimension = (
            is_object_dtype(series.dtype)
            or is_categorical_dtype(series.dtype)
            or is_bool_dtype(series.dtype)
            or is_datetime64_any_dtype(series.dtype)
        )
        if is_dimension or column in identifiers:
            dimensions.append(column)

    return dimensions, measures
~~~

For production use, combine dtype inference with explicit dataset
configuration. A numeric code may be a dimension, and a high-cardinality text
field may be unsuitable for a hierarchy.

Useful metadata for each column:

~~~python
{
    "name": "region",
    "label": "Region",
    "role": "dimension",
    "dtype": "category",
    "nullable": False,
    "distinct_count": 8,
    "hierarchy_enabled": True,
    "sensitive": False,
}
~~~

Only send safe display metadata to the browser.

## 5. Typed hierarchy request

Represent the user's choices as one validated request object rather than
passing unrelated callback arguments deep into the application.

~~~python
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class HierarchyRequest:
    dataset_id: str
    levels: tuple[str, ...]
    aggregations: dict[str, tuple[str, str]]
    filters: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    expanded_depth: int = 1
    max_nodes: int = 10_000
~~~

The aggregations mapping uses:

~~~python
{
    "total_revenue": ("revenue", "sum"),
    "average_revenue": ("revenue", "mean"),
    "total_quantity": ("quantity", "sum"),
}
~~~

The mapping key is the output field. The tuple contains the source column and
operation. This supports more than one calculation from the same source
column without ambiguous output names.

Allow-list operations:

~~~python
ALLOWED_AGGREGATIONS = {
    "sum",
    "mean",
    "median",
    "min",
    "max",
    "count",
    "size",
    "nunique",
    "first",
    "last",
}
~~~

Do not use eval or accept arbitrary Python callables from UI input.

## 6. Recursive grouping algorithm

The simplest reliable algorithm groups one level at a time. Each recursive
call receives only the rows beneath the current parent.

~~~python
from collections.abc import Mapping, Sequence
from hashlib import sha1
import json
from typing import Any

import pandas as pd


ALLOWED_AGGREGATIONS = {
    "sum", "mean", "median", "min", "max",
    "count", "size", "nunique", "first", "last",
}


def python_value(value):
    if pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value


def display_label(value):
    return "Unspecified" if pd.isna(value) else str(value)


def stable_node_id(path):
    serialized = json.dumps(path, ensure_ascii=False, separators=(",", ":"))
    return sha1(serialized.encode("utf-8")).hexdigest()


def validate_hierarchy_request(frame, levels, aggregations):
    levels = list(levels)
    if not levels:
        raise ValueError("Choose at least one hierarchy level.")
    if len(levels) != len(set(levels)):
        raise ValueError("A hierarchy column may only be selected once.")

    required = set(levels)
    for output_name, specification in aggregations.items():
        if not output_name:
            raise ValueError("Aggregation output names must not be empty.")
        source_column, operation = specification
        required.add(source_column)
        if operation not in ALLOWED_AGGREGATIONS:
            raise ValueError(f"Unsupported aggregation: {operation}")

    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Unknown columns: {', '.join(missing)}")


def build_hierarchy(
    frame: pd.DataFrame,
    *,
    levels: Sequence[str],
    aggregations: Mapping[str, tuple[str, str]],
    max_nodes: int = 10_000,
) -> list[dict[str, Any]]:
    levels = list(levels)
    aggregations = dict(aggregations)
    validate_hierarchy_request(frame, levels, aggregations)

    node_count = 0

    def visit(
        current: pd.DataFrame,
        depth: int,
        path: tuple[tuple[str, str], ...],
        parent_id: str | None,
    ) -> list[dict[str, Any]]:
        nonlocal node_count

        level_column = levels[depth]
        records = []
        grouped = current.groupby(
            level_column,
            observed=True,
            dropna=False,
            sort=True,
        )

        for raw_value, group in grouped:
            label = display_label(raw_value)
            path_item = (level_column, label)
            node_path = (*path, path_item)
            node_id = stable_node_id(node_path)

            node_count += 1
            if node_count > max_nodes:
                raise ValueError(
                    "The hierarchy is too large. Apply filters, remove a "
                    "high-cardinality level, or increase the configured limit."
                )

            node = {
                "node_id": node_id,
                "parent_id": parent_id,
                "label": label,
                "level": depth,
                "level_column": level_column,
                "record_count": int(len(group)),
            }

            for output_name, (source_column, operation) in aggregations.items():
                node[output_name] = python_value(
                    group[source_column].agg(operation)
                )

            if depth + 1 < len(levels):
                children = visit(group, depth + 1, node_path, node_id)
                if children:
                    node["_children"] = children

            records.append(node)

        return records

    if frame.empty:
        return []

    return visit(frame, 0, tuple(), None)
~~~

Important behavior:

- Filters are applied before this function is called.
- The first selected column is grouped first.
- Aggregates on a parent use every source row beneath that parent.
- Only nodes with children receive _children.
- Final-level nodes are grouped leaves, not individual source records.
- IDs include both column names and values in the path, so equal labels under
  different branches remain distinct.
- The node limit prevents an accidental browser payload explosion.

### Optional raw-record leaves

Sometimes the last grouped level should expand into individual source records.
Make this an explicit option such as include_record_leaves. After the final
grouping level, create compact leaf dictionaries containing a stable record ID
and only the columns required for display.

Do not include raw records automatically. A hierarchy with thousands of groups
can otherwise become a hierarchy with millions of browser rows.

## 7. Example output

For levels region -> country and a total_revenue sum, the nested result should
look like:

~~~json
[
  {
    "node_id": "stable-id-1",
    "parent_id": null,
    "label": "Europe",
    "level": 0,
    "level_column": "region",
    "record_count": 320,
    "total_revenue": 1200000.0,
    "_children": [
      {
        "node_id": "stable-id-2",
        "parent_id": "stable-id-1",
        "label": "France",
        "level": 1,
        "level_column": "country",
        "record_count": 120,
        "total_revenue": 430000.0
      },
      {
        "node_id": "stable-id-3",
        "parent_id": "stable-id-1",
        "label": "Germany",
        "level": 1,
        "level_column": "country",
        "record_count": 200,
        "total_revenue": 770000.0
      }
    ]
  }
]
~~~

Tabulator does not require a separate parent/child relationship lookup when
the nested _children structure is provided.

## 8. Tabulator columns

The first displayed column must be the tree element column. Build the remaining
columns from the requested aggregates.

~~~python
def hierarchy_columns(aggregations):
    columns = [
        {
            "title": "Hierarchy",
            "field": "label",
            "frozen": True,
            "minWidth": 240,
            "headerFilter": "input",
        },
        {
            "title": "Records",
            "field": "record_count",
            "sorter": "number",
            "hozAlign": "right",
            "formatter": "dash:integer",
        },
    ]

    for output_name, (_, operation) in aggregations.items():
        columns.append(
            {
                "title": humanize(output_name),
                "field": output_name,
                "sorter": "number",
                "hozAlign": "right",
                "formatter": "dash:decimal",
                "formatterParams": {"decimals": 2},
                "bottomCalc": "sum" if operation == "sum" else None,
            }
        )

    return columns
~~~

Remove keys whose values are None before sending this configuration if the
table bridge does not already do so.

## 9. Tabulator tree options

The essential options are:

~~~python
def tree_table_options(*, expanded_depth=1):
    if expanded_depth < 0:
        start_expanded = True
    elif expanded_depth == 0:
        start_expanded = False
    else:
        start_expanded = [
            depth < expanded_depth
            for depth in range(max(expanded_depth + 1, 2))
        ]

    return {
        "layout": "fitColumns",
        "height": "500px",
        "index": "node_id",
        "placeholder": "No hierarchy matches the current filters.",
        "pagination": False,
        "selectableRows": 1,
        "selectableRowsPersistence": False,
        "dataTree": True,
        "dataTreeChildField": "_children",
        "dataTreeElementColumn": "label",
        "dataTreeStartExpanded": start_expanded,
        "dataTreeChildIndent": 22,
        "dataTreeSelectPropagate": False,
        "dataTreeToggleStyle": "chevron",
        "columnDefaults": {
            "resizable": True,
            "tooltip": True,
        },
    }
~~~

Confirm the accepted dataTreeStartExpanded forms against the pinned Tabulator
version. A Boolean is the most portable choice. If level-specific expansion
requires a JavaScript function, pass a safe named formatter token through the
reusable bridge rather than putting inline JavaScript strings in Python.

The JavaScript bridge should translate dataTreeToggleStyle into reusable
elements:

~~~javascript
app.chevrons = {
  expand:
    '<span class="tree-chevron tree-chevron--collapsed" aria-hidden="true">›</span>',
  collapse:
    '<span class="tree-chevron tree-chevron--expanded" aria-hidden="true">›</span>',
};

if (options.dataTreeToggleStyle === "chevron") {
  options.dataTreeExpandElement = app.chevrons.expand;
  options.dataTreeCollapseElement = app.chevrons.collapse;
  delete options.dataTreeToggleStyle;
}
~~~

Suggested CSS:

~~~css
.tree-chevron {
  display: inline-block;
  color: var(--color-text-muted);
  font-size: 1.2rem;
  line-height: 1;
  transition: transform 120ms ease;
}

.tree-chevron--expanded {
  transform: rotate(90deg);
}
~~~

## 10. Dash table wrapper

Keep Tabulator behind a reusable Dash component. A simple wrapper contains:

- a dcc.Store with structured table configuration;
- a small dcc.Store for selected rows or stable IDs;
- an empty Div that becomes the Tabulator host;
- data attributes connecting the host to those stores.

~~~python
from dash import dcc, html


def hierarchy_table(table_id, *, hierarchy, columns, options):
    config_id = f"{table_id}-config"
    selection_id = f"{table_id}-selection"

    return html.Div(
        className="table-component",
        children=[
            dcc.Store(
                id=config_id,
                data={
                    "hostId": table_id,
                    "data": hierarchy,
                    "columns": columns,
                    "options": options,
                },
            ),
            dcc.Store(id=selection_id, data=[]),
            html.Div(
                id=table_id,
                className="tabulator-host",
                **{
                    "data-config-id": config_id,
                    "data-selection-id": selection_id,
                    "role": "region",
                    "aria-label": "Expandable hierarchy table",
                },
            ),
        ],
    )
~~~

A client-side callback watches the configuration store and creates or updates
the Tabulator instance. When only data changes, use replaceData and redraw the
table instead of rebuilding the whole Dash layout.

## 11. Service layer

The callback should not access S3, call groupby directly, or assemble Tabulator
options. Put orchestration in a HierarchyService.

~~~python
from dataclasses import dataclass


@dataclass(frozen=True)
class HierarchyResult:
    nodes: list[dict]
    node_count: int
    source_row_count: int
    filtered_row_count: int
    cache_hit: bool


class HierarchyService:
    def __init__(self, dataframes, cache):
        self.dataframes = dataframes
        self.cache = cache

    def build(self, request):
        frame = self.dataframes.get(request.dataset_id)
        filtered = apply_filters(frame, request.filters)

        cache_key = (
            request.dataset_id,
            self.dataframes.version(request.dataset_id),
            request.levels,
            tuple(sorted(request.aggregations.items())),
            normalize_filters(request.filters),
            request.max_nodes,
        )

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        nodes = build_hierarchy(
            filtered,
            levels=request.levels,
            aggregations=request.aggregations,
            max_nodes=request.max_nodes,
        )
        result = HierarchyResult(
            nodes=nodes,
            node_count=count_nodes(nodes),
            source_row_count=len(frame),
            filtered_row_count=len(filtered),
            cache_hit=False,
        )
        self.cache.set(cache_key, result)
        return result
~~~

The real cache implementation should return a result marked cache_hit=True
when appropriate. Include source version or fingerprint so refreshed Parquet
data cannot reuse an obsolete tree.

## 12. Callback wiring

Use the selected list exactly as provided after server-side validation.

~~~python
from dash import Input, Output, State, no_update


@app.callback(
    Output("hierarchy-table-config", "data"),
    Output("hierarchy-feedback", "children"),
    Input("hierarchy-apply", "n_clicks"),
    State("active-dataset", "data"),
    State("hierarchy-levels", "value"),
    State("hierarchy-measure", "value"),
    State("hierarchy-operation", "value"),
    State("hierarchy-expanded-depth", "value"),
    State("active-filters", "data"),
    prevent_initial_call=True,
)
def update_hierarchy(
    _clicks,
    dataset_id,
    levels,
    measure,
    operation,
    expanded_depth,
    filters,
):
    if not levels:
        return no_update, "Choose at least one hierarchy column."
    if not measure:
        return no_update, "Choose a measure column."

    request = HierarchyRequest(
        dataset_id=dataset_id,
        levels=tuple(levels),
        aggregations={
            f"{operation}_{measure}": (measure, operation),
        },
        filters=tuple(filters or ()),
        expanded_depth=int(expanded_depth or 0),
    )

    try:
        result = hierarchy_service.build(request)
        config = table_service.hierarchy_config(
            "hierarchy-table",
            result.nodes,
            aggregations=request.aggregations,
            expanded_depth=request.expanded_depth,
        )
    except UserFacingHierarchyError as error:
        return no_update, str(error)

    message = (
        f"{result.node_count:,} hierarchy nodes from "
        f"{result.filtered_row_count:,} filtered records"
    )
    return config, message
~~~

The actual code should distinguish validation, data-source, and unexpected
errors. Show safe messages in the UI and retain technical stack information in
server logs.

For fast, small datasets, hierarchy controls may update immediately without an
Apply button. For expensive S3-backed or high-cardinality data, an explicit
Apply action prevents a rebuild after every individual selection.

## 13. Selection and linked details

When a user selects a hierarchy node, send only a compact payload:

~~~python
{
    "node_id": "stable-id-2",
    "level": 1,
    "level_column": "country",
    "label": "France",
}
~~~

For precise server lookup, retain the canonical path in a server-side index
keyed by node_id, or include a compact validated path descriptor when it is not
sensitive.

The selection callback can then:

- display node metadata;
- fetch the filtered source rows beneath the node;
- produce a linked chart;
- show a capped detail table;
- add the node path to active cross-filters.

Do not send every source record under the node as the selection event.

## 14. Calculated measures

Derived calculations should happen before grouping when they are row-level:

~~~text
source rows
  -> filters
  -> row-level derived columns
  -> hierarchy groupby
  -> node aggregates
~~~

Examples:

~~~python
frame = frame.assign(
    gross_margin=frame["revenue"] - frame["cost"],
    gross_margin_pct=safe_divide(
        frame["revenue"] - frame["cost"],
        frame["revenue"],
    ),
)
~~~

Aggregate ratios carefully. The correct parent margin percentage is normally:

~~~text
sum(gross margin) / sum(revenue)
~~~

It is usually not:

~~~text
mean(row-level gross margin percentage)
~~~

Support post-aggregation formulas when a metric must be calculated from
aggregated numerators and denominators.

Keep application-specific calculations in a calculation registry or dedicated
module. Do not accept arbitrary formulas from browser input.

## 15. Filtering semantics

Apply filters before building the hierarchy:

~~~text
DataFrame
  -> region/date/status filters
  -> calculated columns
  -> recursive groupby
  -> tree
~~~

This means parent totals, counts, and child lists describe only the currently
filtered dataset. Display that fact in the UI.

If a hierarchy node is converted into a cross-filter, represent it as all path
conditions:

~~~python
[
    {"field": "region", "operator": "eq", "value": "Europe"},
    {"field": "country", "operator": "eq", "value": "France"},
]
~~~

Filtering the already aggregated browser tree is only a presentation filter;
it does not recalculate totals. Do not confuse Tabulator header filtering with
server-side analytical filtering.

## 16. Performance safeguards

Hierarchy size is driven by distinct combinations, not only source row count.
A two-million-row dataset with a few low-cardinality levels can produce a
small tree. A 50,000-row dataset grouped by a unique ID can produce a very
large tree.

Implement:

- server-side source DataFrame registry;
- Parquet column projection for levels, filters, and measure dependencies;
- Parquet partition pruning where possible;
- filters before grouping;
- categorical dtypes for repeated dimensions where beneficial;
- maximum hierarchy depth;
- maximum node count;
- high-cardinality warnings in the column selector;
- a preview of estimated distinct counts;
- result caching keyed by source version, filters, ordered levels, and
  aggregation specifications;
- compact node fields;
- no raw-record leaves unless explicitly requested and capped.

Recommended initial guardrails:

- maximum selected levels: 5 or 6;
- warning when any selected level has more than 5,000 distinct values;
- default maximum tree nodes: 10,000;
- no more than the configured browser payload limit;
- explicit Apply action for expensive builds.

For trees beyond the safe materialized limit, use one of these approaches:

1. require stronger filters;
2. remove a high-cardinality level;
3. show only top-N groups with an Other node;
4. implement explicit server-side lazy child loading.

Do not pretend Tabulator virtual rendering eliminates the cost of serializing
an enormous nested JSON tree.

## 17. Common implementation mistakes

Avoid these:

- treating selected hierarchy columns as a set and losing their order;
- doing one flat groupby across every selected column and expecting automatic
  expandable parents;
- naming the child field children while configuring Tabulator for _children;
- attaching _children: [] to every leaf unnecessarily;
- using labels alone as IDs;
- using Python's randomized hash function for persistent IDs;
- failing when group labels contain slashes or separator characters;
- calculating parent totals from already rounded child display values;
- applying analytical filters only in the browser;
- sending the source DataFrame through dcc.Store;
- allowing arbitrary aggregation function names from the UI;
- rebuilding the entire Dash layout when controls change;
- enabling normal pagination on a nested tree without verifying behavior;
- omitting source version and ordered levels from the cache key;
- offering sensitive or extremely high-cardinality columns without warnings;
- assuming every numeric column is a measure or every text column is a useful
  hierarchy dimension.

## 18. Tests

Add unit tests covering:

### Hierarchy construction

- one-level hierarchy;
- multiple levels;
- selected order changes the tree;
- empty level selection is rejected;
- duplicate levels are rejected;
- unknown columns are rejected;
- unsupported aggregation functions are rejected;
- missing hierarchy values become Unspecified;
- parent record counts equal the rows beneath them;
- parent sums equal the appropriate source-row sums;
- multiple measures and multiple operations work;
- the same label under different parents has a different stable ID;
- IDs remain stable across repeated builds;
- leaves do not contain _children;
- an empty DataFrame returns an empty tree;
- the maximum-node limit fails with an actionable error.

### Service and cache

- filters run before hierarchy aggregation;
- row-level calculations run before aggregation;
- post-aggregation calculations use unrounded values;
- cache keys change when level order changes;
- cache keys change when source version, filter, measure, or operation changes;
- failed builds do not overwrite a previous valid cached result.

### UI and Tabulator

- eligible column options come from safe server-side metadata;
- selected list order reaches the request unchanged;
- the table index is node_id;
- dataTree is enabled;
- dataTreeChildField is _children;
- dataTreeElementColumn matches the hierarchy label column;
- chevron elements are installed by the JavaScript bridge;
- node selection emits only compact state;
- empty, oversized, and invalid hierarchies show useful feedback.

Perform a browser smoke test:

1. select region, country, customer;
2. build the hierarchy;
3. expand a region and then a country;
4. verify parent totals;
5. reorder the levels;
6. verify the tree changes;
7. apply a filter;
8. verify counts and totals recalculate;
9. select a node;
10. verify the linked detail and chart update;
11. check the browser console for errors.

## 19. Completion checklist

The implementation is complete when:

- the user can choose hierarchy columns from schema-derived options;
- the chosen order determines recursive groupby order;
- measures and allow-listed aggregation operations are configurable;
- filters and row calculations run before hierarchy construction;
- every parent contains correct aggregates for all rows beneath it;
- stable path-based IDs identify every node;
- nested children use the exact _children field;
- Tabulator displays chevrons and expandable levels;
- selection drives compact server-side detail or chart requests;
- source DataFrames remain server-side;
- oversized trees are prevented or handled explicitly;
- local tests and a browser workflow both pass;
- the documentation explains how to add dimensions, measures, calculations,
  and hierarchy levels.

## 20. Short prompt for another coding agent

If a shorter handoff is needed, use this:

> Build a reusable expandable hierarchy table for a Plotly Dash application
> using pandas and the free MIT-licensed Tabulator Data Tree feature. Users
> must choose an ordered list of eligible DataFrame columns; that order must
> define the recursive groupby path. They must also choose validated measures
> and allow-listed aggregation operations. Apply active filters and row-level
> calculations before grouping. For each group at every level, emit a node with
> a stable path-based node_id, label, level, record_count, aggregated measures,
> and nested _children only when child groups exist. Keep the full DataFrame in
> a server-side registry and send only a capped hierarchy result to the
> browser. Configure Tabulator with dataTree enabled, _children as the child
> field, label as the tree element column, node_id as the row index, custom
> chevrons, and selectable rows. Put grouping in a pure transformation,
> orchestration and caching in a HierarchyService, Tabulator configuration in a
> TableService, and only request translation in thin Dash callbacks. Add
> validation for unknown/duplicate columns, unsupported operations, null
> groups, high-cardinality selections, maximum depth, and maximum nodes. Test
> ordering, rollups, stable IDs, filtering semantics, cache keys, Tabulator
> options, selection, and the complete expand/collapse browser workflow.
