# Example Widget Module

This is a minimal SentinelDashboard module example.

To install it:

1. Copy this folder to `modules/example`
2. Copy `example.html` from this folder to `templates/widgets/example.html`
3. Restart SentinelDashboard
4. Open `/api/example` to see the raw JSON response
5. Add the `example` widget to a view — this renders `templates/widgets/example.html`, but it only shows a static "Loading..." placeholder at this point

Required files:

- `manifest.json`
- `example.html` (widget template — must be copied to `templates/widgets/`, not left in the module folder; see [Module System](../../docs/ARCHITECTURE.md#module-system))

Optional files:

- `service.py`
- `api.py`
- `widget.js` (see below — this one, unlike the others, stays in the module folder)
- static assets

## Loading live data into the widget

This folder's `widget.js` already does it — copy it alongside the other files (`modules/example/widget.js`, no relocation needed, unlike `example.html`) and it's auto-served at `/modules/example/widget.js` and auto-included by the dashboard page. It fetches `/api/example` and writes into `#example-content`, then calls `registerWidget("example", updateExample)` to plug into the update scheduler — see [Plugin Architecture](../../docs/ARCHITECTURE.md#plugin-architecture) for how that scheduler picks it up, and `modules/cameras/widget.js` for a more involved real example.

(The older way still works too: add the same kind of function directly to `static/js/widgets.js` and call `registerWidget()` there instead — useful for a widget you consider a core, built-in part of the dashboard rather than a self-contained plugin.)

The refresh interval doesn't need to be set manually either way: it's read from the `refresh` field in `manifest.json` (seconds) via `/api/widgets` and passed to `setInterval` automatically.
