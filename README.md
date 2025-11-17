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

3. Open http://127.0.0.1:8000 in your browser.

What is implemented

- Template routes: `/`, `/about`, `/events`, `/actualites`, `/communities`, `/join`, `/contact`
- JSON API under `/api/v1`: `events`, `news`, `communities`, `translations/{lang}`, `join` (POST), `contact` (POST)
- Static files served from `/static`
