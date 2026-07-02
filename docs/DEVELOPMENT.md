# Development Rules

## Core principles

- One completed unit of work = one commit
- Small, safe, reviewable patches
- Design before code: think through the architecture before writing it
- Every commit must pass the project check before landing

## Coding style

- **Python** — simple, explicit, minimal dependencies, small focused modules
- **JavaScript** — vanilla JS only, no frameworks, no build step, files grouped by responsibility

See [ENGINEERING.md](ENGINEERING.md) for the full philosophy (no Node.js / Webpack / build systems).

## Before every commit

Run the project's check script:

```bash
python tools/check.py
```

This validates:

- **Python syntax** — every `.py` file is compiled to catch errors early
- **Configuration files** — `config/dashboard.json`, all `modules/*/manifest.json`, and `config/views/*.json` are validated as JSON
- **API endpoints** (optional) — if the FastAPI server is already running on `127.0.0.1:8000`, it also checks `/api/info`, `/api/system`, `/api/network` (required) and `/api/weather`, `/api/rss` (optional, since they depend on external services)

If the server isn't running, the API checks are skipped with a warning — this is expected, not a failure.

## Versioning and commits

Every commit bumps the project version and carries it in the commit message:

```
vX.Y.Z Short description
```

Examples from the project history:

- `v1.2.4 Split frontend settings and bootstrap`
- `v1.1.0 Add core module loader`
- `v1.0.0 First stable release`

Guidelines for bumping:

- **Patch** (`v1.2.3` → `v1.2.4`) — small change, fix, or single completed step
- **Minor** (`v1.1.3` → `v1.2.0`) — a meaningful feature or milestone is complete
- **Major** (`v1.x.x` → `v2.0.0`) — breaking change or a full release stage (e.g. public v2.0)

## Git workflow

```bash
# 1. Update the VERSION file with the new version number
echo "1.2.5" > VERSION

# 2. Run checks
python tools/check.py

# 3. Commit with the version in the message
git add .
git commit -m "v1.2.5 Short description"
git push
```

One feature → Bump version → Validation → Commit → Push
