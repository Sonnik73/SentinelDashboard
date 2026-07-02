# Release Checklist — v2.0

This checklist tracks the public release audit. Update it as each item is completed.

---

## Stage A — Documentation

- [x] README.md
- [x] docs/INSTALL.md
- [x] docs/DEVELOPMENT.md
- [x] docs/ENGINEERING.md
- [x] docs/ARCHITECTURE.md
- [x] docs/MODULES.md
- [x] docs/ROADMAP.md
- [x] docs/RELEASE_CHECKLIST.md (this file)

## Stage B — Repository Cleanup

- [x] Review examples/example_widget/ for accuracy against the current module convention (found and fixed: missing widget template, inaccurate install instructions)
- [x] LICENSE present and correct (MIT)
- [x] CHANGELOG.md kept in sync with VERSION
- [x] VERSION file kept in sync with commits
- [x] .gitignore covers .venv, __pycache__, runtime data cache, local config
- [ ] Remove any leftover dead code or unused files found during Stage C

## Stage C — Code Audit

- [ ] Python — review all modules for consistency with ENGINEERING.md principles
- [ ] JavaScript — review static/js/*.js for consistency (vanilla JS only, no leftover dead code)
- [ ] Known candidate: `create_view()` in modules/views/service.py is implemented but not wired to any API endpoint — decide whether to expose it or remove it
- [ ] Confirm the `system` module's special-cased wiring (no service.py/api.py of its own) is intentional and documented, or refactor to match the standard module convention
- [ ] The `refresh` field in every module's manifest.json is not read anywhere in the frontend — refresh intervals are hardcoded per-widget in static/js/widgets.js instead. Decide whether to wire manifest refresh values into the frontend or remove the unused field from manifests

## Stage D — UX Audit

- [ ] Fresh install on a clean Raspberry Pi, following INSTALL.md start to finish
- [ ] Settings drawer — all actions work as expected
- [ ] Layout editor — save, span editing, row packing
- [ ] Offline behavior — disconnect network, confirm weather/rss fall back to cache correctly
- [ ] Error handling — invalid config, missing data files, unreachable hosts

## Stage E — Release

- [ ] `git status` clean — no untracked files that should be committed or ignored
- [ ] All documentation cross-references verified (no broken links between docs)
- [ ] examples/example_widget/ tested end-to-end as a new-module template
- [ ] Final version bump to `2.0.0`
- [ ] Release tag created and pushed (`git tag v2.0.0 && git push --tags`)

---

Update this file as each box is checked. When every item above is checked, SentinelDashboard v2.0 is ready for public release.
