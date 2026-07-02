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
- static assets

## Loading live data into the widget

Unlike the backend (which auto-discovers modules), the frontend is **not** automatic. To make the widget display live data:

1. Add an `update` function to `static/js/widgets.js` that fetches `/api/example` and writes into `#example-content` (see `updateBirthdays()` in that file for a minimal pattern)
2. Call it once and register it with `setInterval` at the bottom of `static/js/widgets.js`

Note: the `refresh` value in `manifest.json` is not currently read by the frontend — refresh intervals are set manually in `static/js/widgets.js`. This is a known gap, tracked in [RELEASE_CHECKLIST.md](../../docs/RELEASE_CHECKLIST.md).
