# Agent Guidelines: convert_videos

- When running any python commands, run them with `uv run`.
- For any functionality you add or remove, include tests and ensure they work.
- When running commands like grep, remove unneeded results with `--exclude-dir .venv --exclude-dir .mypy_cache --exclude uv.lock`.
- Source code belongs in `./src/convert_videos/` and tests in `./tests`. Each source code file should have its own test file using the same name and prefixed with `test_`.
- After all changes are completed and working, use `uv run ruff format; uv run ruff check` to format all files correctly and check for issues. Run them as one command.
- When releasing, bump the version in `pyproject.toml`, run `uv sync`, commit, and create/push a semver tag.
