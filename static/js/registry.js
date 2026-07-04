// ------------------------------
// Widget Registry
// ------------------------------
// A module ships its own JS (modules/<id>/widget.js, see core/loader.py's
// optional widget.js convention) and calls registerWidget() to plug its
// updater into the scheduler in widgets.js, instead of needing
// static/js/widgets.js edited for every new widget. Loaded first so both
// widgets.js's built-in updaters and any module's own widget.js can call
// registerWidget() regardless of load order between them.
const WIDGET_UPDATERS = {};

function registerWidget(id, updater) {
    WIDGET_UPDATERS[id] = updater;
}
