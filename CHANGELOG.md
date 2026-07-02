# SentinelDashboard Changelog

Все значимые изменения проекта фиксируются здесь.

---

## v1.3.0

### Added
- New docs/RELEASE_CHECKLIST.md tracking the 5-stage release audit (Documentation, Repository Cleanup, Code Audit, UX Audit, Release)

### Milestone
- Stage A (Documentation) of the v2.0 Release Candidate Audit is complete: README, INSTALL, DEVELOPMENT, ENGINEERING, ARCHITECTURE, MODULES, ROADMAP, and RELEASE_CHECKLIST have all been rewritten and verified against the actual codebase

---

## v1.2.9

### Fixed
- ROADMAP.md no longer lists already-shipped features (Widget Manifest System, Automatic Module Discovery, Birthdays Widget) under the unreleased Version 2.0 section
- Added missing Modular API Architecture to Completed

---

## v1.2.8

### Added
- New docs/MODULES.md: documents every module (system, weather, rss, network, birthdays), the view system, and the offline caching mechanism
- Flagged create_view() in modules/views/service.py as implemented but unused (candidate for code audit stage)

---

## v1.2.7

### Added
- Documented the Module System in ARCHITECTURE.md (automatic discovery, convention over configuration, API auto-loading)

### Fixed
- core/ and modules/ file lists in ARCHITECTURE.md now match the actual codebase (loader, module_api, system.py, birthdays module, system module)
- Layout Engine description no longer implies it belongs to an unreleased v2
- cameras widget flagged as placeholder (template only, not yet implemented)

---

## v1.2.6

### Added
- ENGINEERING.md principle 11: No Build Systems (fixes reference from DEVELOPMENT.md)

### Fixed
- Unwrapped check.py command now in a proper bash code fence

---

## v1.2.5

### Changed
- Rewrote DEVELOPMENT.md with proper markdown structure
- Documented tools/check.py behavior (Python syntax, JSON config, optional API checks)
- Established versioned commit convention (vX.Y.Z in commit message)

---

## v1.2.4

### Changed
- Split frontend settings logic and app bootstrap into separate modules

---

## v1.2.3

### Changed
- Split frontend widget updaters into a dedicated module

---

## v1.2.2

### Added
- Frontend API helper module (static/js/api.js)

---

## v1.2.1

### Added
- Module SDK example (examples/example_widget)

### Changed
- Cleaned cached bytecode from repository

---

## v1.2.0

### Changed
- Completed modular API architecture (core/module_api.py)

---

## v1.1.3

### Added
- Automatic module API discovery

---

## v1.1.2

### Added
- Manifest driven widget rendering

---

## v1.1.1

### Changed
- Stabilized self-describing module contract

---

## v1.1.0

### Added
- Core module loader (core/loader.py)

---

## v1.0.9

### Changed
- Strengthened module manifest validation

---

## v1.0.8

### Added
- Birthdays widget MVP

---

## v1.0.7

### Added
- Widget manifest foundation

---

## v1.0.6

### Added
- Layout Editor save action
- Live span preview in Settings Drawer
- Automatic row packing for dashboard widgets
- View layout saving through API

### Changed
- View Editor now uses layout as the main state model
- Improved resilience of project checks for external API timeouts

### Fixed
- Restored live data updates after layout editor refactor
- Added weather error reporting when falling back to cache

---

## v1.0.0

### Added
- First stable release
- Modular dashboard architecture
- System, Weather, RSS and Network widgets
- Dashboard Views Engine
- Settings Drawer
- View Editor state model
- Live Preview Engine
- Shareable dashboard views
- Project documentation

### Changed
- Stabilized project structure
- Cleaned unused architecture files
- Added Road to Stability documentation

---
## v0.9.4

### Added
- Settings Drawer action panel
- View Editor state model
- Current view status indicator
- Copy view link button foundation

### Fixed
- Restored dashboard auto update after View Editor changes

---

## v0.8.2 (In Progress)

### Added
- VERSION file
- Project identity

---

## v0.8.1

### Added
- Ping latency
- Raspberry Pi IP
- Automatic interface detection
- Compact Network Widget

---

## v0.8.0

### Added
- Network Widget
- Router monitoring
- Internet monitoring

---

## v0.7.1

### Fixed
- Dashboard auto update

---

## v0.7.0

### Added
- RSS Widget

---

## v0.6.0

### Added
- Configuration system
- Widget Engine

---

## v0.5.1

### Added
- Infrastructure Core

---

## v0.5.0

### Added
- Weather Widget
- Offline cache

---

## v0.4.0

### Added
- Progress bars

---

## v0.3.1

### Changed
- Project architecture refactoring
