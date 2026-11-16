# Project notes

- Python requirement is 3.14 (`.python-version`). Install dependencies from this directory with command `uv sync`.
- The Flask app starts with command `uv run python src/index.py` and opens on `localhost:5001` To do browser tests, you must keep it running on a seperate terminal. 
- Robot Framework in `src/tests`. Run everything with `uv run robot src/tests`, or one test `uv run robot src/tests/<test-name>`
- Browser tests use Robot Framework and default to Chromium window. If browser binaries are missing, install them with `uv run rfbrowser install`; run headlessly with `uv run robot -v HEADLESS:true src/tests`.
- Tests reset state through `/tests/reset`; users are stored in memory in `src/repositories/user_repository.py` and state does not survive an app restart