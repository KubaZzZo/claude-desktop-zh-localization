# Repository Guidelines

## Project Structure & Module Organization

This repository contains tooling for applying, validating, and rolling back Chinese localization resources.

- `scripts/` contains Python utilities such as `apply_localization.py`, `verify_localization.py`, `validate_resources.py`, and shared helpers in `common.py`.
- `scripts/reference/` stores reference patching/restoration scripts used for comparison or recovery workflows.
- `locales/` contains active localization JSON files, including `root-zh-CN.json`, `ion-zh-CN.json`, and Statsig locale resources.
- `patches/` stores UI patch data, currently `main-ui-patches.json`.
- `docs/` contains user-facing and compatibility documentation.
- Root batch files such as `apply.bat`, `rollback.bat`, `restore-english.bat`, and `verify.bat` provide Windows entry points.
- `backups/`, `__pycache__/`, and `.pytest_cache/` are generated artifacts and should not be committed.

## Build, Test, and Development Commands

- `.\apply.bat` applies the localization workflow using the configured resources.
- `.\verify.bat` runs repository verification checks.
- `.\rollback.bat` rolls back the most recent localization changes where supported.
- `.\restore-english.bat` restores English resources.
- `python scripts\validate_resources.py` validates locale and patch resource structure.
- `python scripts\verify_localization.py` checks applied localization output.
- `pytest scripts` runs Python tests, including helper tests such as `scripts/test_common.py`.

Run commands from the repository root so relative paths in scripts and batch files resolve correctly.

## Coding Style & Naming Conventions

Use Python 3 for scripts. Follow standard PEP 8 conventions: 4-space indentation, `snake_case` for functions and modules, and clear constant names for shared paths or configuration keys. Keep scripts small and procedural unless shared behavior belongs in `scripts/common.py`.

JSON files should remain UTF-8 encoded, consistently indented, and valid after edits. Preserve existing locale key names exactly; only change values unless a script explicitly requires new keys.

## Testing Guidelines

Add or update tests under `scripts/` using `test_*.py` naming. Prefer focused tests around path handling, JSON validation, backup discovery, and rollback behavior. Before submitting changes, run `pytest scripts` plus the relevant validation or verification command for the touched workflow.

## Commit & Pull Request Guidelines

Use concise, imperative commit messages that describe the change, for example `Add locale validation checks` or `Update rollback backup handling`. Keep generated files out of commits unless they are intentional fixtures.

Pull requests should include a short summary, the commands run, and any manual verification performed. For localization changes, mention affected files under `locales/`, `patches/`, or `scripts/`, and include before/after notes when behavior changes.

## Security & Configuration Tips

Do not commit local backups, cache files, logs, upload artifacts, or credentials. Review `.gitignore` before publishing to ensure generated directories such as `backups/`, `__pycache__/`, and `.pytest_cache/` stay untracked.
