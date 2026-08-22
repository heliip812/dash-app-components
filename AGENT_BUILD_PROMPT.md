# Agent brief: build a connector-driven analytical Dash application

Use this file as the implementation prompt for another coding agent. The agent
must build the application foundation from scratch in the target repository;
it must not assume that a reusable architecture, component library, connector
layer, or data pipeline already exists. Replace the placeholders in **Project
inputs** when those details are known. If a placeholder is not filled in, the
agent should make a conservative, reversible assumption and document it.

## Project inputs

- Target repository: [TARGET REPOSITORY]
- Optional architectural reference:
  https://github.com/heliip812/dash-app-components
- Application/domain name: [APPLICATION NAME]
- Primary users: [USER TYPES]
- Expected data size: [ROWS / FILE COUNT / TOTAL SIZE]
- AWS region: [AWS REGION]
- S3 locations: [BUCKETS AND PREFIXES — DO NOT PUT CREDENTIALS HERE]
- S3 partition layout: [FOR EXAMPLE year/month/day/customer]
- Refresh model: [ON STARTUP / MANUAL / SCHEDULED / TTL]
- Required datasets and schemas: [DATASET NAMES, KEYS, IMPORTANT COLUMNS]
- Required calculations: [DERIVED COLUMNS, FORMULAS, BUSINESS RULES]
- Required aggregations: [GROUPINGS, MEASURES, AGGREGATION FUNCTIONS]
- Required hierarchies: [FOR EXAMPLE region > country > account]
- Required visualizations: [LINE / BAR / SCATTER / HEATMAP / OTHER]
- Required filters: [DATE, CATEGORY, STATUS, SEARCH, ETC.]
- Deployment target: [LOCAL / CONTAINER / CLOUD PLATFORM]

## Your role

Act as a senior Python, data-platform, and Plotly Dash engineer. Build a new,
reusable, connector-driven analytical application foundation in the target
repository. Produce working code, tests, documentation, sample data, and a
verified UI. Do not deliver only a proposal or illustrative snippets.

Before changing code:

1. Inspect the target repository for instructions, starter files, dependencies,
   and tests. Do not assume they exist.
2. If starter tests exist, run them and record the baseline. If the repository
   is empty, state that clearly.
3. Design and create the app factory, DataFrame registry, connector interface,
   services, transformations, figure builders, reusable UI components,
   Tabulator integration, single-URL navigation, assets, and test structure.
4. Create a deterministic local Parquet dataset so the complete foundation is
   demonstrable without external credentials.
5. Identify assumptions, risks, and any genuinely blocking missing details.

Ask questions only when the answer would materially change the architecture,
security model, or correctness. Otherwise proceed with documented assumptions.

## Outcome

Build an application in which users can:

- configure or select one of several data-source connectors;
- load Parquet datasets from S3 efficiently and securely;
- inspect dataset metadata, schema, source version, and load status;
- filter, select, sort, calculate, group, aggregate, and pivot data;
- create reusable Plotly visualizations from compact derived results;
- explore expandable multi-level hierarchies with parent and child rows;
- cross-filter between controls, tables, charts, and detail panels;
- refresh or invalidate data without restarting the entire application;
- understand errors and data freshness without seeing secrets or stack traces.

The result must remain a reusable foundation. Do not hard-code the whole
application around one bucket, schema, metric, or dashboard.

## Non-negotiable architecture

Keep these boundaries explicit:

~~~text
Data source
  -> connector
  -> load request and source metadata
  -> server-side DataFrame registry
  -> pure transformations
  -> application services
  -> compact table or figure model
  -> thin Dash callback
  -> UI
~~~

Responsibilities:

- **Connectors** retrieve data and source metadata. They do not build UI or
  contain business calculations.
- **Registry/cache** owns process-local datasets and load metadata. Large
  DataFrames stay server-side.
- **Transformations** are pure, testable pandas functions with no Dash imports.
- **Services** validate requests and orchestrate connectors, registry access,
  transformations, caching, tables, and figures.
- **Callbacks** translate UI state into typed service requests and return small
  results. They do not contain large pandas or Plotly implementations.
- **Components and views** define layout and presentation. They do not fetch S3
  data directly.
- **JavaScript** is limited to reusable browser behavior such as the Tabulator
  bridge, formatters, selection events, chevrons, and redraw behavior.

Do not store a full DataFrame, credentials, or large record arrays in
dcc.Store. Browser stores may contain only small UI state, filters, request
descriptors, selected stable IDs, and capped display results.

## Required foundation structure

Create a strongly segregated structure similar to the following. Small naming
adjustments are acceptable when they improve consistency, but do not collapse
these responsibilities into giant files:

~~~text
project/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── assets/
│   ├── css/
│   │   ├── global/
│   │   ├── components/
│   │   ├── views/
│   │   └── vendor/
│   └── js/
│       ├── global/
│       ├── components/
│       └── views/
├── data/
│   └── sample/
├── scripts/
│   └── generate_sample_data.py
├── src/
│   ├── app_factory.py
│   ├── callbacks/
│   ├── connectors/
│   ├── components/
│   │   ├── cards/
│   │   ├── charts/
│   │   ├── controls/
│   │   ├── feedback/
│   │   └── tables/
│   ├── data/
│   │   ├── cache/
│   │   └── loaders/
│   ├── figures/
│   ├── layout/
│   ├── navigation/
│   ├── services/
│   ├── transformations/
│   ├── utils/
│   └── views/
│       ├── data_sources/
│       ├── overview/
│       ├── analysis/
│       ├── hierarchy_explorer/
│       ├── visualisation_lab/
│       └── component_gallery/
└── tests/
    ├── callbacks/
    ├── components/
    ├── connectors/
    ├── data/
    ├── services/
    ├── transformations/
    └── integration/
~~~

The app factory is the composition root. It must construct connector and
dataset registries, caches, services, the application shell, view layouts, and
callback registration explicitly. Avoid import-time network calls and mutable
module-level datasets.

Build the generic component foundation before composing domain views. It should
include reusable controls, metric cards, panels, feedback/empty/loading/error
states, Plotly graph containers, standard Tabulator tables, expandable tree
tables, detail panels, tooltips, and modal behavior.

## Connector layer

Create a connector package, for example:

~~~text
src/connectors/
├── __init__.py
├── base.py
├── models.py
├── registry.py
├── local_parquet.py
└── s3_parquet.py
~~~

Define a small interface or Protocol rather than coupling services directly to
AWS. It should support the following concepts, with names adapted to the
repository's conventions:

- connector identity and display metadata;
- connection validation or a lightweight health check;
- dataset discovery when the source supports it;
- a typed load request;
- loading a dataset;
- schema and source metadata;
- clear, typed connector errors.

A load request should be serializable and should be able to express:

- dataset or logical source ID;
- URI, bucket/key, or registered source name;
- selected columns;
- partition filters;
- safe predicate filters where supported;
- optional row limit for preview;
- refresh or cache policy.

A load result should include:

- the DataFrame or an explicit registry handoff;
- source URI without credentials;
- row and column counts;
- schema or dtype summary;
- object version, ETag, last-modified value, or equivalent source fingerprint;
- load timestamp and duration;
- warnings such as schema reconciliation or partial reads.

Register connectors by stable ID through a connector registry or dependency
injection. Adding a future SQL, API, local-file, or warehouse connector must
not require rewriting S3-specific logic throughout the application.

Provide a local Parquet connector or test fixture that implements the same
interface. The complete application and test suite must run without AWS
credentials.

## S3 and Parquet requirements

Implement an S3 Parquet connector using a minimal, open-source dependency set.
Prefer PyArrow's dataset and filesystem capabilities where practical. Use
boto3 or s3fs only when it provides a clear required capability; explain the
choice and licence in the README.

The S3 implementation must:

- accept s3://bucket/key and registered bucket/prefix configurations;
- use the standard AWS credential provider chain;
- support IAM roles, environment-based local development, and named profiles
  where appropriate;
- never hard-code or commit access keys, secret keys, session tokens, or
  presigned URLs;
- never expose credentials in logs, callback outputs, browser stores, errors,
  or cache keys;
- support column projection;
- use partition pruning and predicate pushdown where supported;
- avoid downloading an entire dataset merely to inspect its schema;
- handle a single Parquet object and a partitioned Parquet dataset;
- define behavior for missing objects, access denied, empty datasets, corrupt
  files, mixed schemas, network timeouts, and credential expiry;
- normalize and validate source configuration before access;
- return actionable user-facing errors and retain technical causes for logs.

Do not silently fall back from a failed production S3 source to sample data.
Mock or demo modes must be explicit.

Include an .env.example or configuration example containing variable names and
safe placeholders only. Keep non-secret dataset configuration separate from
secret resolution.

## Dataset registry, caching, and freshness

Create one central DataFrameRegistry and route dataset ownership through it
rather than creating unrelated global DataFrames.

Each registered dataset should have:

- a stable logical dataset ID;
- connector and source identity;
- source fingerprint or version;
- loaded-at timestamp;
- row count, column count, and memory size;
- schema metadata;
- optional refresh deadline;
- load warnings and status.

Treat registered DataFrames as immutable. Transformations may create compact
derived frames, but callbacks and services must not mutate a registered source
in place.

### Required staged cache design

Implement caching in explicit stages rather than using one unbounded dictionary:

~~~text
Stage 0: source metadata
  connector + dataset -> schema, ETag/version, last modified, partitions

Stage 1: loaded working DataFrame
  normalized load request + source fingerprint -> registered immutable frame

Stage 2: reusable transformation result
  dataset generation + access scope + filters + calculation version
    -> compact filtered/calculated frame when reuse justifies its memory cost

Stage 3: grouped hierarchy prefixes
  Stage 2 key + hierarchy prefix + aggregation specification
    -> flat grouped DataFrame for one hierarchy depth

Stage 4: final presentation result
  dataset generation + access scope + filters + calculations
  + ordered hierarchy levels + measures + tree options
    -> nested _children tree and compact Tabulator configuration
~~~

Stage 1 is the most important cache: loading the same S3 object or partitioned
dataset must not happen again merely because a user changes views, reorders
hierarchy levels, expands a row, or chooses another visualization.

Stage 2 is optional and must be bounded. Do not cache every arbitrary filter
combination if that can duplicate large portions of the source DataFrame.
Prefer caching compact calculated columns, commonly reused filtered working
sets, and aggregation results.

Stages 3 and 4 should be bounded LRU/TTL caches because their results are much
smaller than the source data and are likely to be reused when users return to
a view or repeat a selection.

### Cache-key correctness

Create deterministic, typed cache-key builders. Do not build keys by calling
str on arbitrary dictionaries.

A key must include every input that can change the result, including:

- connector ID and logical dataset ID;
- source fingerprint, version, ETag, or registry generation;
- projected source columns and partition predicates for a load;
- server-derived authorization or tenant scope;
- normalized analytical filters;
- calculation-registry version and selected calculations;
- ordered hierarchy levels;
- measure source columns, output names, and aggregation operations;
- null, observed-category, sorting, top-N, subtotal, and limit semantics;
- initial tree materialization or lazy-loading parameters when they affect data.

Preserve the order of hierarchy levels in the final tree key. The sequences
region -> country and country -> region are different presentation results.
Only canonicalize inputs whose semantics are genuinely order-independent.

Hash a canonical JSON-safe representation when a shorter key is required. Use
stable serialization with explicit field names, sorted mapping keys, and
preserved sequence order.

Never include:

- AWS credentials or session tokens;
- presigned URLs;
- authorization headers;
- raw sensitive record values;
- mutable Python object identities;
- browser-supplied authorization scope.

### User and view state

The browser may store only a compact selection descriptor such as:

~~~python
{
    "dataset_id": "sales",
    "levels": ["region", "country", "customer"],
    "measures": [
        {"output": "revenue", "column": "revenue", "operation": "sum"}
    ],
    "filters": [
        {"field": "year", "operator": "eq", "value": 2026}
    ],
    "request_fingerprint": "safe-result-key",
}
~~~

Do not store the source DataFrame or a large hierarchy tree in per-user browser
state merely to avoid recomputation.

When a user activates a view:

1. derive the effective request from the view selection;
2. derive access scope on the server from the authenticated principal;
3. check the final result cache;
4. if it misses, check reusable prefix/aggregation caches;
5. build only the missing results;
6. return the compact table or figure configuration;
7. remember only the small request fingerprint for that view/session.

Hiding and showing a view with an unchanged request must not reload S3 or
rebuild the same hierarchy. Expanding and collapsing already materialized
nodes is client-side Tabulator behavior and must not call the connector.

Do not include the view ID in a data-result cache key unless the view actually
changes analytical semantics. This allows Overview, Hierarchy Explorer, and a
linked chart to share the same compact aggregation result.

Results may be shared between users only when their server-derived data-access
scope is identical. If row-level security, tenant filtering, or user-specific
permissions affect the data, that scope must be part of every derived-result
key. Never trust a tenant or role value supplied only by dcc.Store.

### Loading and refresh behavior

Use a single-flight or per-key lock so concurrent requests for the same missing
dataset or hierarchy result trigger one build while the others wait for that
result. Do not hold one global lock during unrelated loads.

Refresh must be atomic:

1. inspect the remote source fingerprint;
2. load and validate the new data into a temporary object;
3. only after validation succeeds, register it as a new dataset generation;
4. make new requests use the new generation immediately;
5. let old generation keys expire or evict safely;
6. keep the known-good generation if refresh fails.

Do not clear every cache entry on every UI change. Generation-based keys make
source invalidation precise and avoid races with in-flight requests.

Support:

- explicit user refresh where permitted;
- optional TTL/freshness checks;
- source-version comparison before expensive reloads;
- manual invalidation by dataset ID;
- bounded stale-result behavior only when explicitly configured and disclosed;
- cache hit, miss, build, wait, eviction, refresh, and failure metrics.

### Memory and deployment rules

Every cache must have a documented maximum size, item count, TTL, and eviction
policy. Record approximate DataFrame and serialized-result sizes. Avoid keeping
multiple full-frame copies for different users.

The default implementation may use a thread-safe process-local registry and
bounded process-local result caches. Document that multiple Gunicorn workers
do not share Python memory. For multi-worker or multi-instance deployment,
choose deliberately among:

- accepting one loaded DataFrame per worker while sharing only compact results;
- sticky routing when appropriate;
- an approved shared cache for compact serialized results;
- a shared analytical store when the data no longer fits the process-local
  model.

Do not put multi-gigabyte pandas DataFrames into a generic remote key/value
cache. Do not introduce Redis, Celery, a database, or distributed compute
unless the deployment and measured scale require it. If a shared backend is
added, document serialization, compression, security, licence, failure
behavior, and maximum payload size.

## Calculation and transformation layer

Keep calculations configuration-driven and composable, while using explicit
Python callables for application-specific rules.

Implement pure operations for:

- validated column selection and renaming;
- typed filters, including equality, membership, ranges, dates, and text;
- stable single- and multi-column sorting;
- derived columns;
- groupby with named aggregations;
- whole-dataset aggregations;
- pivot tables;
- null handling;
- safe division and percentage calculations;
- hierarchy construction;
- compact record selection and detail lookup.

Do not use eval, exec, raw user-supplied Python expressions, or arbitrary
callable imports from UI input. Use allow-listed operations and validated
specifications.

Define typed request/result models for important workflows. For example, an
aggregation request should describe dimensions, named measures, filters, sort
order, and result limits. A service should validate that requested columns
exist and that aggregation functions are compatible with their dtypes.

Make domain-specific formulas easy to find. Put them in a dedicated module or
calculation registry and mark the intended extension seam clearly. Do not mix
them into generic grouping, filtering, callbacks, or chart code.

## Aggregations and groupby

The groupby pipeline must support:

- zero, one, or multiple dimensions;
- multiple named measures in one request;
- at least sum, mean, median, min, max, count, size, nunique, first, and last
  where compatible;
- deterministic column naming;
- sorting and top-N after aggregation;
- optional subtotal or total rows when requested;
- empty inputs and all-null groups;
- categorical dimensions and observed-group behavior;
- date-period grouping when specified;
- clear validation failures for unknown columns or functions.

Return regular DataFrames with predictable columns, not hard-to-consume
MultiIndex results, unless a pivot result explicitly requires matrix form.

## Expandable hierarchy

Build hierarchy data on the server from an ordered list of dimensions, for
example region -> country -> account.

Each node should contain:

- a stable path-based ID;
- label and hierarchy level;
- dimension values for its path;
- record count;
- requested aggregated measures;
- optional parent ID;
- nested _children only when children exist.

Requirements:

- use Tabulator's free MIT-licensed Data Tree functionality;
- support any reasonable number of hierarchy levels;
- display expand/collapse chevrons and indentation;
- allow a configurable initial expansion depth;
- format parent, intermediate, leaf, subtotal, and total rows distinctly;
- preserve stable selection identity across redraws;
- support selection-to-detail and selection-to-chart interactions;
- define filtering semantics: whether filters are applied before hierarchy
  construction, and make that behavior visible to users;
- avoid sending uncapped raw datasets to the browser.

If lazy-loading child nodes is necessary for the stated scale, design an
explicit server request protocol. Otherwise prefer a capped, fully materialized
tree for simpler behavior.

### Fast hierarchy construction and caching

For interactive hierarchy selection, do not repeatedly scan the source once
for every parent node. Build flat grouped results once per selected prefix:

~~~text
Selected levels: region -> country -> customer

Prefix 1: groupby(region)
Prefix 2: groupby(region, country)
Prefix 3: groupby(region, country, customer)
~~~

Cache each compact prefix result, then assemble the nested _children structure
by stable parent paths. This usually performs better than recursively slicing
the DataFrame and running a new groupby separately inside every parent.

The hierarchy service should:

1. get the immutable registered source by dataset generation;
2. project only hierarchy, filter, and measure dependency columns;
3. apply validated filters once;
4. apply row-level calculations once;
5. look up or build each grouped prefix;
6. calculate post-aggregation measures from unrounded components;
7. assemble nodes and stable IDs without rescanning the source;
8. cache the final nested tree by the complete ordered request;
9. return a capped Tabulator configuration.

If the same request is made again, return Stage 4 immediately. If the user
changes only the final hierarchy level, reuse matching earlier prefix results.
If the user revisits a prior selection, it should also be a cache hit until TTL,
eviction, access-scope change, or source-generation change.

For configured, frequently used additive metrics, consider a reusable
fine-grained aggregate base rather than precomputing every hierarchy
combination. Roll up only when mathematically valid:

- sum, count, size, min, and max can normally be combined;
- mean can be recomputed from cached sum and count;
- weighted averages require their explicit numerator and denominator;
- median and exact quantiles cannot generally be combined from child medians;
- nunique cannot generally be summed across overlapping child groups;
- first and last require a defined ordering.

Never trade correctness for a cache hit. If a measure is not roll-up safe,
compute it from the appropriate filtered source or a valid metric-specific
intermediate.

Expansion state is UI state, not analytical data. Do not create a new hierarchy
cache entry merely because a user opens or closes a chevron. Initial expansion
depth may be part of the table-configuration key, but it should not invalidate
the underlying grouped prefix or hierarchy-data cache.

## Visualization layer

Create generic Plotly figure builders under src/figures. Add figure types only
through small, focused builder modules.

Each builder should:

- accept presentation-ready compact data rather than loading a source;
- share common theme, layout, typography, margins, hover formatting, and empty
  states;
- support a stable color strategy;
- handle missing and empty data;
- avoid constructing figures inside callbacks;
- keep traces bounded through grouping, sampling, binning, or limits;
- return a valid figure for error-free empty states.

At minimum support reusable line, grouped/stacked bar, scatter, and heatmap
workflows. Add other chart types only if required by Project inputs.

Cross-filtering should pass stable IDs or compact filter descriptors back to a
service. Clearly indicate active filters and provide a reset action.

## Application views

Preserve the single-URL, always-mounted navigation model. Do not introduce Dash
Pages, dcc.Location routing, redirects, or one giant callback that returns
whole layouts.

Create focused views such as:

- **Data Sources** — connector status, dataset selection, source metadata,
  column projection, load/refresh controls, and safe error feedback.
- **Overview** — key metrics and a small number of cross-filtered charts.
- **Analysis** — filters, calculation choices, groupby dimensions, measures,
  aggregation controls, and result preview.
- **Hierarchy Explorer** — expandable Tabulator tree, selection detail, and a
  linked chart.
- **Visualization Lab** — configurable chart examples using service results.
- **Component Gallery** — reusable independent UI specimens.

Every view should keep config, layout, callbacks, and view-only CSS separated.
Shared behavior belongs in components or services.

## Performance expectations

- Load a source once per effective cache key, not once per callback.
- Reuse the registered source across views and user hierarchy selections when
  source generation and access scope are unchanged.
- Project columns and prune partitions as early as possible.
- Filter before expensive groupby, pivot, hierarchy, or figure work.
- Cache compact reusable prefix aggregations and final hierarchy results with
  bounded size and generation-based invalidation.
- Use per-key single-flight builds to prevent duplicate concurrent groupbys.
- Returning to the same view and unchanged selection should be a result-cache
  hit; expanding a materialized row should require no Python recomputation.
- Avoid unnecessary full-frame copies.
- Use stable IDs rather than serializing whole selected rows.
- Cap browser-bound records and chart points.
- Let Tabulator handle pagination and virtual rendering for capped results.
- Time connector loads and major transformations with structured logs.
- Expose useful, non-sensitive metadata such as duration, rows, source version,
  cache hit/miss, and freshness.

Do not claim a performance target without measuring it. Add a repeatable smoke
benchmark for the expected data scale when Project inputs provide one.

## Security and operational behavior

- Use least-privilege IAM guidance: normally s3:ListBucket for approved prefixes
  and s3:GetObject for approved objects.
- Validate bucket, prefix, dataset, columns, operations, and limits.
- Do not accept arbitrary server filesystem paths from browser input.
- Do not log raw credentials, authorization headers, full presigned URLs, or
  sensitive record values.
- Make debug mode opt-in and disabled in production instructions.
- Separate user-facing errors from technical logs.
- Treat all external schemas and object contents as untrusted input.
- Document timeout, retry, and backoff behavior; retry only safe read actions.
- Keep audit-friendly source and transformation metadata without storing
  secrets.

If authentication or user-level authorization is needed but unspecified,
design a clean boundary and document it; do not invent a weak production auth
system.

## Dependencies

Use only dependencies whose required functionality is free and open source.
Prefer MIT, BSD, or Apache-2.0 licences.

Do not use:

- AG Grid or Dash AG Grid;
- enterprise-only or commercially licensed grid features;
- paid dashboard/UI packages;
- Dash Enterprise-only features;
- a large infrastructure dependency without demonstrated need.

For every significant new dependency, document:

- version constraint;
- purpose;
- licence;
- why the standard library and already selected foundation dependencies were
  insufficient;
- confirmation that the used features are available without payment.

## Testing

Add focused tests for:

### Connectors

- connector registration and lookup;
- typed request normalization and validation;
- local Parquet loading;
- mocked S3 single-object and partitioned-dataset loading;
- column projection and partition/predicate filters;
- missing object, access denied, empty dataset, corrupt Parquet, schema
  mismatch, and expired/absent credentials;
- secret redaction from exceptions and logs.

Use mocks, dependency injection, temporary local Parquet files, or an
appropriate lightweight AWS test double. Unit tests must not require live AWS
access or incur cloud cost.

### Transformations and services

- every supported filter and aggregation;
- multi-measure groupby with predictable columns;
- nulls, empty data, incompatible dtypes, and unknown columns;
- derived calculations, safe division, and application-specific formulas;
- pivot and hierarchy results;
- stable hierarchy IDs and correct aggregate rollups;
- staged cache-key correctness, hits, TTL/eviction, and generation invalidation;
- repeated identical hierarchy requests return the cached final result;
- changing hierarchy order changes the tree key;
- changing only a final level reuses eligible prefix aggregations;
- hiding and reopening an unchanged view does not reload or regroup;
- expanding/collapsing a materialized row does not call Python or S3;
- source refresh creates a new generation and does not serve stale trees;
- a failed refresh preserves the prior known-good generation;
- concurrent identical misses perform one load or hierarchy build;
- authorization scopes cannot reuse each other's cached results;
- credentials and sensitive values never appear in cache keys;
- cache limits and eviction prevent unbounded memory growth;
- source lineage propagation into results.

### UI and architecture

- app creation without AWS credentials using explicit local/demo configuration;
- views remain mounted and navigation changes visibility state only;
- callbacks call services rather than connectors directly;
- no full DataFrame is placed in dcc.Store;
- table and figure empty/error states;
- selection-to-detail and cross-filter behavior;
- Tabulator tree configuration and bridge registration.

Run all applicable starter tests as well as the complete new test suite. Perform
a browser smoke test of the main workflow and check the console for errors.

## Documentation and configuration deliverables

Update or create:

- README setup instructions for local and S3-backed modes;
- configuration reference with safe examples;
- .env.example containing no secrets;
- connector extension guide;
- calculation/aggregation extension guide;
- hierarchy and visualization extension guide;
- dependency and licence table;
- IAM permissions example scoped to placeholder resources;
- known limitations and multi-worker caching behavior;
- staged cache architecture, key fields, TTLs, size limits, eviction, refresh,
  generation invalidation, single-flight behavior, and access-scope isolation;
- troubleshooting for credentials, permissions, schemas, and Parquet errors.

Include a short architecture diagram and at least one end-to-end data-flow
example:

~~~text
S3 Parquet
  -> S3ParquetConnector
  -> DataFrameRegistry
  -> filter
  -> derived calculations
  -> groupby / aggregation
  -> hierarchy or figure service
  -> Tabulator / Plotly
~~~

## Implementation workflow

1. Inspect the target repository and record whether it is empty or contains
   starter constraints.
2. Write a concise plan and create the clean foundation structure.
3. Implement one vertical slice first:
   local Parquet -> registry -> aggregation -> figure/table -> tested view.
4. Add the S3 connector behind the same interface.
5. Add the immutable registry and staged, bounded cache infrastructure.
6. Add calculations, grouped-prefix caching, pivot, and hierarchy capabilities.
7. Wire thin callbacks and user-facing loading/error/freshness/cache states.
8. Add unit, integration, concurrency, architecture, and browser smoke tests.
9. Measure cold load, cold hierarchy build, prefix reuse, and warm result hits
   with representative data.
10. Update documentation and dependency licences.
11. Run the full verification suite and summarize exactly what changed.

Prefer small modules and explicit composition. If starter code exists, either
integrate it into the new architecture or retire it deliberately with tests;
do not leave parallel legacy and new architectures in the repository.

## Acceptance criteria

The work is complete only when all of the following are true:

1. The app runs locally without AWS credentials in an explicit local/demo mode.
2. An S3 Parquet connector exists behind a reusable connector interface.
3. AWS credentials use the standard provider chain and never enter source,
   browser state, cache keys, or logs.
4. S3 loading supports projection and uses pruning/pushdown where available.
5. Large DataFrames remain server-side in the registry.
6. Connector, transformation, service, callback, and view responsibilities are
   clearly separated.
7. Calculations and allow-listed groupby aggregations are reusable and tested.
8. Plotly figures consume compact service results and have empty states.
9. Expandable multi-level hierarchy works through Tabulator Data Tree with
   stable IDs, chevrons, rollups, and selection behavior.
10. Cross-filtering passes compact IDs or filter descriptors.
11. Refresh, cache invalidation, freshness, source version, and errors are
    visible and behave predictably.
12. Identical hierarchy selections reuse cached results, compatible hierarchy
    changes reuse grouped prefixes, and expand/collapse does not reload data.
13. Cache keys isolate authorization scopes and source generations without
    containing credentials or sensitive records.
14. Every cache is bounded and concurrent identical misses are single-flight.
15. Existing tests still pass and new edge cases are covered.
16. A browser smoke test confirms the principal workflow and no console errors.
17. Documentation explains setup, extension points, security, licences, and
    operational limitations.
18. No paid, enterprise-only, or proprietary dependency is required.

## Final handoff format

At completion, report:

- the implemented data flow;
- files and modules added or changed;
- assumptions made;
- exact connector and AWS behavior;
- calculations and aggregations supported;
- hierarchy and visualization behavior;
- caching and refresh semantics;
- test commands and results;
- browser verification performed;
- performance measurements;
- security and licence notes;
- known limitations and recommended next steps.

Do not describe work as complete if a required path is mocked, untested, or
only documented. Clearly distinguish production-ready behavior from fixtures
and future work.
