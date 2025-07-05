When running any python commands, run them with `uv run`.
For any functionality you add or remove, include tests and ensure they work.
When running commands like grep, remove unneeded results with `--exclude-dir .venv --exclude-dir .mypy_cache --exclude uv.lock`.
Source code belongs in ./convert_videos/ and tests in ./tests each source code file should have it's own test file using the same name and prefixed with `test_`
After all changes are completed and working, use `uv run ruff format; uv run ruff check` to format all files correctly and check for issues.
Then bump the minor version in `pyproject.toml` and run `uv sync`
