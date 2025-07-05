When running any python commands, run them with `uv run`.
For any functionality you add or remove, include tests and ensure they work.
After all changes are completed and working, use `uv run ruff format; uv run ruff check` to format all files correctly and check for issues.
When running commands like grep, remove unneeded results with `--exclude-dir .venv --exclude-dir .mypy_cache --exclude uv.lock`
