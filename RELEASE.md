# Automated Release Process

This repository uses GitHub Actions to automatically release new versions when changes are merged to the `main` branch.

## How It Works

The release workflow (`.github/workflows/release.yml`) automatically:

1. **Bumps the version** in `pyproject.toml` based on commit message keywords
2. **Runs tests** to ensure quality
3. **Builds the package** (creates wheel and tar.gz files)
4. **Publishes to PyPI** using the configured API token
5. **Creates a GitHub Release** with auto-generated release notes and attaches the build artifacts

## Setup Requirements

### 1. PyPI API Token

You need to configure a PyPI API token as a repository secret:

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token (scope: entire account or specific to `lets-debug-helper`)
3. Copy the token (starts with `pypi-`)
4. In your GitHub repository, go to **Settings → Secrets and variables → Actions**
5. Create a new repository secret named `PYPI_API_TOKEN`
6. Paste your PyPI token as the value

### 2. GitHub Token

The workflow uses `GITHUB_TOKEN` which is automatically provided by GitHub Actions. No additional setup required.

## Version Bump Control

The workflow determines which part of the version to bump based on your commit message:

- **Patch version** (default): `1.5.16` → `1.5.17`
  - Used for bug fixes and minor changes
  - Any commit without special keywords
  
- **Minor version**: `1.5.16` → `1.6.0`
  - Used for new features that are backward compatible
  - Include `[minor]` anywhere in your commit message or PR title
  
- **Major version**: `1.5.16` → `2.0.0`
  - Used for breaking changes
  - Include `[major]` anywhere in your commit message or PR title

### Examples:

```bash
# Patch release (default)
git commit -m "fix: resolve issue with domain validation"

# Minor release
git commit -m "feat: add support for wildcard domains [minor]"

# Major release
git commit -m "feat!: redesign API structure [major]"
```

## Skipping a Release

If you want to merge changes to main without triggering a release, include `[skip release]` in your commit message:

```bash
git commit -m "docs: update README [skip release]"
```

## Workflow Triggers

The release workflow runs on:
- ✅ Pushes to `main` branch (typically from merged PRs)
- ❌ Changes to documentation files (`.md`), `LICENSE`, or `.github/**` (except the release workflow itself)
- ❌ Commits containing `[skip release]`

## Manual Release Process (Legacy)

If you need to create a release manually, you can still use the Makefile commands:

```bash
# Bump version (patch, minor, or major)
make bump_py_version WHL_VERSION=patch

# Package the application
make package

# Publish to PyPI
make publish

# Create GitHub release
make gh-release

# Or do all at once
make full-release WHL_VERSION=patch
```

## Monitoring Releases

1. **GitHub Actions**: View workflow runs at https://github.com/jediknight112/lets-debug-helper/actions
2. **PyPI Releases**: Check https://pypi.org/project/lets-debug-helper/
3. **GitHub Releases**: View at https://github.com/jediknight112/lets-debug-helper/releases

## Troubleshooting

### Release workflow failed at "Publish to PyPI"

- Verify your `PYPI_API_TOKEN` secret is correctly set
- Check that the token has permissions for the `lets-debug-helper` package
- Ensure the version number doesn't already exist on PyPI

### Release workflow failed at "Create GitHub Release"

- Check that the release tag doesn't already exist
- Verify the `GITHUB_TOKEN` has sufficient permissions

### Version bump commit creates infinite loop

- The workflow includes `[skip ci]` in the version bump commit to prevent this
- Ensure you're using the latest version of the workflow

## Best Practices

1. **Use Pull Requests**: Merge changes via PRs rather than direct pushes to main
2. **Meaningful Commits**: Write clear commit messages that explain the changes
3. **Test Before Merging**: The CI workflow should pass before merging
4. **Version Keywords**: Use `[major]` or `[minor]` keywords when appropriate
5. **Review Release Notes**: GitHub auto-generates release notes from commits and PRs
