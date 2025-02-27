FROM python:3.11-slim

ENV PYTHONUNBUFFERED True

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set environment variables for Poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="/opt/poetry/bin:$PATH"

ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock ./

# Install dependencies
ARG FLAVOR=minimal
RUN poetry install --no-dev --extras "${FLAVOR}"

# Copy the rest of the application
COPY . ./

# Set up environment variables and entrypoint
ENV PORT 8080
ENTRYPOINT ["docker/docker-entrypoint.sh"]
CMD ["poetry", "run", "embedbase"]