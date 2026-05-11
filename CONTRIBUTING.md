# Contributing

Thanks for taking a look! This project is small enough that contributions are usually quick.

## Dev setup

Requires [Poetry](https://python-poetry.org/) and Python 3.13+.

```bash
git clone https://github.com/jediknight112/lets-debug-helper
cd lets-debug-helper
make setup     # poetry install
```

Run the CLI from the dev environment:

```bash
poetry run lets-debug example.com
```

## Make targets

| Target | What it does |
|---|---|
| `make setup` | Install dependencies via Poetry |
| `make lint` | Run flake8 |
| `make typing` | Run mypy in strict mode |
| `make test` | Run pytest |
| `make coverage` | Run pytest with coverage report |
| `make format` | Reformat code with yapf |

CI runs `lint`, `typing`, and `coverage` on every PR — running them locally before pushing saves a round-trip.

## Pull requests

1. Branch off `main`.
2. Make your change with tests.
3. Make sure `make lint`, `make typing`, and `make test` all pass.
4. Open a PR. CI will run on Python 3.13 and 3.14.

`main` is protected — all changes land via PRs.

## Release process

There are two release paths:

### Manual (for human-authored changes)

After your PR merges to `main`:

1. Go to the repo's **Actions** tab → **Release** workflow → **Run workflow**.
2. Pick a `bump_type` (`patch`, `minor`, or `major`).
3. The workflow will:
   - Bump `pyproject.toml` and commit `chore: bump version to X.Y.Z [skip ci]` to `main`
   - Run tests
   - Build wheel + sdist with Poetry
   - Publish to PyPI
   - Create a matching `vX.Y.Z` GitHub release with auto-generated notes

`pyproject.toml`, the GitHub release tag, and the PyPI version stay in lockstep.

### Automatic (Dependabot only)

When Dependabot's auto-merge lands a dependency PR on `main`, the same release workflow fires automatically with `bump_type=patch`. The author gate (`head_commit.author.name == 'dependabot[bot]'`) ensures it only triggers for Dependabot merges, not regular human PRs.

To suppress the auto-release for a specific Dependabot merge, include `[skip release]` in the merge commit message.

## CI / Dependabot at a glance

- **`.github/workflows/main.yml`** — runs lint, typing, coverage, package build, and an install smoke test on Python 3.13 and 3.14 for every PR and push to `main`.
- **`.github/workflows/release.yml`** — see above.
- **`.github/workflows/dependabot-automation.yaml`** — auto-approves and enables auto-merge on Dependabot PRs that bump minor/patch versions. Major bumps wait for human review.
- **`.github/dependabot.yaml`** — weekly checks for both `pip` and `github-actions` ecosystems; dev/test pip updates and minor/patch action updates are batched into single grouped PRs to reduce noise.
