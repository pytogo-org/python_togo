# Python Togo — Local FastAPI server

Quick start

1. Create a virtual environment and install dependencies:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. Run the server:

```sh
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
or

```sh
fastapi dev
```
3. Open http://127.0.0.1:8000 in your browser.

4. Development

```bash
# Install pre-commit hooks
pre-commit install

# Run linting and formatting
ruff check --fix .
ruff format .

# Run all pre-commit checks
pre-commit run --all-files
```

What is implemented

- Template routes: `/`, `/about`, `/events`, `/actualites`, `/communities`, `/join`, `/contact`
- JSON API under `/api/v1`: `events`, `news`, `communities`, `translations/{lang}`, `join` (POST), `contact` (POST)
- Static files served from `/static`
