# SentinelDashboard Engineering Principles

This document defines the engineering principles of the project.

The goal is simple:

> Keep SentinelDashboard stable, predictable and maintainable while it grows.

---

# 1. Architecture First

Every significant feature starts with architecture.

Implementation follows architecture, not the other way around.

---

# 2. One Completed Module

A finished module is more valuable than several unfinished features.

Prefer completion over quantity.

---

# 3. Small Safe Iterations

Large refactorings are avoided whenever possible.

Development proceeds through small, reviewable patches.

---

# 4. Working Tree

Every commit should leave the project in a working state.

Broken commits are unacceptable.

---

# 5. Validate Everything

Before every commit run:

```bash
python tools/check.py
```

Whenever possible:

- validate Python
- validate JSON
- validate APIs

---

# 6. Documentation Evolves Together

Architecture documentation is part of development.

Code and documentation should never drift apart.

---

# 7. JSON Is the Source of Truth

Views, layouts and configuration are stored in JSON.

The user interface reflects the data model.

---

# 8. Live Preview

Changes should be visible immediately whenever possible.

Fast feedback improves development and usability.

---

# 9. Backward Compatibility

Existing configurations should continue to work after upgrades whenever practical.

Migration is preferred over breaking changes.

---

# 10. Simplicity Wins

Choose the simplest solution that remains maintainable.

Avoid unnecessary complexity.

---

# 11. No Build Systems

SentinelDashboard runs as a single process:

```bash
uvicorn app:app
```

Nothing else.

Do NOT introduce:

- Node.js / npm
- Webpack, Vite, Rollup
- React, Vue, Angular
- Any JavaScript build or bundling step

The frontend is vanilla JavaScript, served directly by FastAPI. This constraint is intentional and one of the project's core values.

---

# Development Cycle

Idea

↓

Architecture

↓

Implementation

↓

Validation

↓

Commit

↓

Documentation

↓

Release

---

# Vision

SentinelDashboard is evolving from a dashboard application into a modular dashboard platform.

Every engineering decision should move the project toward that vision.

