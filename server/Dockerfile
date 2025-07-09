# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables for Python and Poetry
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.1.3
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install Poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Set the working directory in the container
WORKDIR /app

# Copy only files necessary for dependency installation first
# This leverages Docker's layer caching. If these files don't change,
# Docker won't re-run poetry install.
COPY pyproject.toml poetry.lock ./

# Install project dependencies using Poetry
# --no-dev skips development dependencies
# --no-interaction and --no-ansi are good for CI/automated environments
RUN poetry install --no-interaction --no-ansi --no-root --without dev

# Copy the rest of the application code into the container
# Ensure you have a .dockerignore file to exclude unnecessary files
COPY . .

# Initialize db
RUN python -c "from common.database import init_db; import asyncio; asyncio.run(init_db())"

# Expose the port the app runs on
# This should match the port Uvicorn will listen on (default 8000 in sesame.py or passed in CMD)
EXPOSE 7860

# Command to run the application
# This uses the 'run' command from sesame.py to start the Uvicorn server.
# '--host 0.0.0.0' makes the server accessible from outside the container.
# '--no-reload' is generally preferred for production/staging images.
CMD ["uvicorn", "webapp.main:app", "--host", "0.0.0.0", "--port", "7860"]
