## Getting Started

* This project (server) uses python version: >=3.11,<4.0
* Poetry is used as the virtual env and package manager

## How to Run

### Server

1. Install Poetry if you haven't already: `curl -sSL https://install.python-poetry.org | python3 -`
2. Navigate to the project directory: `cd server`
3. Install the dependencies (or sync with `poetry.lock`): `POETRY_VIRTUALENVS_IN_PROJECT=1 poetry sync --with dev --no-root`
4. Run the server: `poetry run uvicorn webapp.main:app --host <HOST> --port <PORT>`

> Notes: <HOST> usually is `0.0.0.0` and <PORT> is `8000`

### Client

1. Navigate to the client directory: `cd client`
2. Install the dependencies: `npm install`
3. Run the client: `npm run dev`

**Note**: Make sure to update the `VITE_SERVER_URL` environment variable to point to the server's URL.
