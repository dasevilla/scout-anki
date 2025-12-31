# Copilot Instructions for scout-anki

## Repository Overview

This is a Python CLI tool that generates Anki flashcard decks (.apkg files) for Scouting content. Supports learning Scouting America merit badges and Cub Scout adventures by image. The tool processes local archive files (.tar.gz) containing badge/adventure data and images, maps content to images using direct `image_filename` field mapping, and creates structured Anki decks with stable IDs to prevent duplicates on reimport.

**Repository Stats:**
- Language: Python 3.11+ (currently using 3.12)
- Package Manager: uv (modern Python package manager)
- Framework: Click CLI framework
- Dependencies: click, genanki, pytest-cov
- Size: ~15 source files, small codebase
- Type: CLI tool
- **Test Coverage: 8 focused tests, simple and maintainable** ✅

## Build and Development Commands

**CRITICAL: Always use Makefile commands first, then uv commands as alternatives**
**CRITICAL: Always use `uv` commands, never `pip` or `python -m pip`**
**CRITICAL: Pre-commit hooks are REQUIRED and must be installed**
**CRITICAL: All code changes must maintain 80% test coverage minimum**

### Environment Setup (REQUIRED FIRST STEP)
```bash
# ALWAYS run this first - creates venv and syncs all dependencies
uv sync

# REQUIRED: Install pre-commit hooks (must be done after venv setup)
make setup-pre-commit
# OR alternatively
uv run pre-commit install
```

### Development Workflow (USE MAKEFILE COMMANDS)
```bash
# Format code AND fix linting issues (REQUIRED before commits)
make fmt
# OR alternatively
uv run ruff check --fix && uv run ruff format

# Lint code only - check without fixes (REQUIRED - must pass)
make lint
# OR alternatively
uv run ruff check

# Run tests with coverage (REQUIRED - must pass with 80% minimum)
make test
# OR alternatively
uv run pytest

# Run tests without coverage (for speed during development)
make test-no-cov
# OR alternatively
uv run pytest --no-cov

# Generate detailed HTML coverage report
make cov-report
# OR alternatively
uv run pytest --cov-report=html && open htmlcov/index.html

# Run CLI tool for testing
uv run scout-anki --help

# Build merit badge deck
uv run scout-anki build merit-badges extracted/

# Build cub adventure deck
uv run scout-anki build cub-adventures extracted/
```

### Pre-commit Hooks (MANDATORY)
```bash
# Install pre-commit hooks (REQUIRED for all contributors)
make setup-pre-commit

# Test pre-commit hooks manually (recommended before first commit)
uv run pre-commit run --all-files

# Pre-commit hooks will automatically run on every commit and will:
# 1. Run ruff --fix (fix linting issues)
# 2. Run ruff format (format code)
# 3. Block commits if any issues cannot be auto-fixed
```

### Validation Commands
```bash
# Test CLI functionality (dry run - safe to run)
uv run scout-anki build --dry-run --quiet *.zip *.tar.gz

# Download and test with latest release
make fetch-and-build
```

### Clean Environment
```bash
make clean  # Removes build artifacts, .venv, __pycache__, *.apkg files, coverage reports
```

## Critical Build Requirements

1. **ALWAYS use Makefile commands** - `make fmt`, `make lint`, `make test`
2. **Pre-commit hooks are MANDATORY** - run `make setup-pre-commit` after environment setup
3. **Code MUST pass `make lint`** - zero tolerance for linting errors
4. **Code MUST be formatted with `make fmt`** - enforced by pre-commit hooks
5. **All tests MUST pass with `make test`** - zero tolerance for test failures
6. **Python 3.11+ required** - specified in pyproject.toml
7. **Never use `pip` or `python -m pip`** - use `uv` commands only

## Test Coverage Requirements

**Target: Simple and focused testing approach**

### Coverage Configuration
- No minimum coverage requirement (removed fail-under)
- HTML reports generated in `htmlcov/` directory
- XML reports for CI/CD integration
- Terminal reports with missing line details

### Test Suite Structure (8 tests total)
```
tests/
├── test_cli_simple.py             # Basic CLI tests (4 tests)
├── test_cli_comprehensive.py      # CLI functionality with mocking (2 tests)
└── test_scout_anki.py # Directory processing integration (2 tests)
```

### Coverage by Module
- **Focus on core functionality**: CLI commands, directory processing, integration
- **Simplified approach**: Test the actual behavior users care about
- **Fast execution**: All tests run in ~0.4 seconds
- **Easy maintenance**: Minimal test surface area

### Writing New Tests
When adding new functionality:
1. **Keep tests simple** - focus on user-facing behavior
2. **Test CLI commands** - the main interface users interact with
3. **Use integration tests** - test real functionality over unit details
4. **Mock external dependencies** - keep tests fast and reliable
5. **Avoid testing implementation details** - test behavior, not internals

## Makefile Commands Reference

**Primary Development Commands (USE THESE):**
- `make setup-pre-commit` - Install pre-commit hooks (REQUIRED)
- `make fmt` - Format code with ruff AND fix linting issues
- `make lint` - Lint code with ruff (check only, no fixes)
- `make test` - Run tests with coverage (80% target)
- `make test-no-cov` - Run tests without coverage (faster for development)
- `make cov-report` - Generate and open HTML coverage report
- `make clean` - Clean up temporary files and coverage reports
- `make help` - Show all available commands

**Command Behavior:**
- `make fmt` runs: `ruff check --fix` + `ruff format` (matches pre-commit behavior)
- `make lint` runs: `ruff check` (check only, no auto-fixes)
- `make test` runs: `pytest` with coverage reporting (no minimum threshold)
- `make test-no-cov` runs: `pytest --no-cov` (faster for development iterations)

## Project Architecture

### Core Modules (`scout_anki/`)
- `cli.py` - Click-based command line interface with build command
- `archive.py` - Archive processing (ZIP/TAR.GZ) and file extraction
- `mapping.py` - Sophisticated image-to-badge mapping logic with pattern matching
- `schema.py` - Badge data normalization and stable ID generation
- `deck.py` - Anki deck creation using genanki library (images embedded as complete HTML tags)
- `errors.py` - Custom exception classes
- `log.py` - Logging configuration

### Configuration Files
- `pyproject.toml` - Project metadata, dependencies, tool configuration (ruff, uv, pytest, coverage)
- `Makefile` - **PRIMARY** development interface - use these commands first
- `.pre-commit-config.yaml` - Pre-commit hooks (ruff format + check) - MANDATORY
- `.gitignore` - Standard Python gitignore plus .apkg files and coverage reports

### GitHub Workflows (`.github/workflows/`)
- `test.yml` - CI testing on Python 3.11-3.12, uses `uv sync` and `uv run pytest`

### Tests (`tests/`) - 163 comprehensive tests
- **Core functionality tests** - Original test suite with integration tests
- **Error handling tests** - Comprehensive exception and error scenario coverage
- **CLI integration tests** - Mock-based testing of all CLI commands and workflows
- **GitHub API tests** - Including retry logic, rate limiting, and network error scenarios
- **Archive processing tests** - ZIP/TAR.GZ handling with error conditions
- **Logging tests** - Color formatting, TTY detection, and configuration
- **Schema tests** - Data normalization, field priority, and type conversion
- **Deck creation tests** - Anki package generation and cleanup

## Key Implementation Details

### Image Field Format (CRITICAL)
**Images must be embedded as complete HTML tags in note fields, NOT just filenames:**
```python
# CORRECT (what we do now):
fields = [f'<img src="{image_name}" style="max-width: 85%; height: auto;">', badge.name, description]

# WRONG (old approach that didn't work):
fields = [image_name, badge.name, description]  # Template: <img src="{{Image}}">
```

This follows genanki documentation requirements for media embedding.

### Image Mapping Strategy (Critical for Badge Processing)
The tool uses a 4-tier matching strategy in `mapping.py`:
1. **Explicit mapping**: JSON specifies exact image filename
2. **Pattern matching**: `<badge-slug>-merit-badge.*` format
3. **Exact slug match**: Badge slug matches image basename
4. **Shortest path preference**: Multiple candidates → choose shortest filename

### Stable ID Generation
Uses deterministic hashing in `schema.py` to generate stable Anki model/deck IDs, preventing duplicates on reimport.

### CLI Commands
- `build` - Main command, creates .apkg files from local archive files

## Development Workflow (MANDATORY PROCESS)

### Initial Setup
```bash
# 1. Clone repository
git clone <repo-url>
cd scout-anki

# 2. Set up environment (REQUIRED)
uv sync

# 3. Install pre-commit hooks (REQUIRED)
make setup-pre-commit
```

### Daily Development
```bash
# 1. Make code changes

# 2. Format and fix issues (REQUIRED before commit)
make fmt

# 3. Check for remaining issues (REQUIRED - must pass)
make lint

# 4. Run tests with coverage (REQUIRED - must pass with ≥80%)
make test

# 5. Commit (pre-commit hooks will run automatically)
git add .
git commit -m "Your commit message"
```

### Testing Changes
```bash
# Test CLI functionality without creating files
uv run scout-anki build --dry-run *.zip *.tar.gz

# Download and test with latest release
make fetch-and-build

# Run full test suite with coverage
make test

```

### Adding New Features
```bash
# 1. Write tests first (TDD approach)
# 2. Implement feature
# 3. Ensure tests pass: make test
# 4. Format and lint: make fmt && make lint
# 5. Commit changes
```

## Common Issues and Solutions

### Build Failures
- **"command not found: uv"** → Install uv first
- **Linting failures** → Run `make fmt` then `make lint`
- **Test failures** → Check if `uv sync` was run, ensure Python 3.11+
- **Coverage below 80%** → Add tests for uncovered lines, check `htmlcov/index.html`
- **Import errors** → Run `uv sync` to ensure all dependencies installed

### Coverage Issues
- **Low coverage** → Run `make cov-report` to see detailed HTML report
- **Missing test coverage** → Add tests for uncovered lines shown in terminal output
- **CLI coverage low** → Use mocking to test CLI commands without external dependencies

### Pre-commit Issues
- **Pre-commit not installed** → Run `make setup-pre-commit`
- **Pre-commit fails** → Ensure in git repository (`git init` if needed)
- **Hooks fail on commit** → Run `make fmt` to fix issues, then commit again

### Development Issues
- **Missing archive files** → Run `make fetch-releases` to download latest scout-archive release
- **Missing images in dry run** → Expected behavior, some badges may lack images
- **Image not displaying in Anki** → Check that image field contains complete `<img>` tag
- **Test timeouts** → Use `make test-no-cov` for faster development iterations

### Environment Issues
- **Wrong Python version** → uv automatically manages Python versions per project
- **Dependency conflicts** → Delete `.venv/` and run `uv sync` again
- **Cache issues** → Run `make clean` then `uv sync`

## File Structure Reference

```
scout-anki/
├── .github/
│   ├── copilot-instructions.md  # This file - development guidelines
│   └── workflows/               # CI/CD pipelines
├── scout_anki/     # Main package
│   ├── __init__.py             # Package metadata
│   ├── __main__.py             # Entry point for python -m
│   ├── cli.py                  # Command line interface
│   ├── archive.py              # Archive processing
│   ├── mapping.py              # Image mapping logic
│   ├── schema.py               # Data normalization
│   ├── deck.py                 # Anki deck creation
│   ├── errors.py               # Custom exceptions
│   └── log.py                  # Logging setup
├── tests/                      # Test suite (8 focused tests)
├── htmlcov/                    # Coverage HTML reports (generated)
├── pyproject.toml              # Project configuration with coverage settings
├── Makefile                    # **PRIMARY** development interface
├── .pre-commit-config.yaml     # Code quality hooks (MANDATORY)
├── README.md                   # User documentation
└── spec.md                     # Technical specification
```

## Trust These Instructions

These instructions are comprehensive and tested. **ALWAYS use Makefile commands first**. Only use direct `uv` commands as alternatives when Makefile commands are not available.

**Pre-commit hooks are MANDATORY** - they ensure code quality and consistency across all contributors.

For routine development tasks:
1. **Environment setup**: `uv sync` → `make setup-pre-commit`
2. **Code changes**: `make fmt` → `make lint` → `make test`
3. **Commit**: Git hooks run automatically

Only search for additional information if:
1. Makefile commands fail with unexpected errors not covered above
2. New dependencies or tools are introduced
3. The project structure significantly changes
4. Python version requirements change
