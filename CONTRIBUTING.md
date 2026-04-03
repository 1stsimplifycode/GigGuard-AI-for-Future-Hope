# Contributing to ARIA-Gig / GigGuard

## Development Setup

1. Fork and clone the repo
2. Follow [DEPLOYMENT.md](docs/DEPLOYMENT.md) for local setup
3. Create a branch: `git checkout -b feature/your-feature`

## Branch Naming
- `feature/` — new features
- `fix/` — bug fixes
- `docs/` — documentation only
- `test/` — adding tests

## Commit Style (Conventional Commits)
```
feat: add geopolitical stress simulation
fix: correct causation score clamping
docs: update API reference for /assess
test: add T4 payout tier edge case
```

## Pull Request Checklist
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Frontend builds: `npm run build`
- [ ] No hardcoded secrets
- [ ] Updated docs if API changed

## Code Standards
- Python: PEP 8, type hints on all functions
- JavaScript: ESLint clean, no console.log in production
- All risk model changes must include test coverage

## Architecture Decisions
Core insurance logic lives in `backend/services/risk_engine.py`.
Changes to the Causation Model, Workability Index, or Payout Tiers
must be reviewed carefully — they affect financial payouts.
