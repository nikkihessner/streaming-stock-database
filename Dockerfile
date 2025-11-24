# Use full Debian-based Python (not slim/alpine). PIN BY DIGEST.
FROM python:3.14-bookworm@sha256:e392e288e977be19c14f075d3ec056b9a24113741ead2fcf5e4f3b3009285581

# Create non-root user
ARG APP_UID=10001
RUN useradd -u ${APP_UID} -m appuser

WORKDIR /app

# Minimal system dependencies for psycopg2 / confluent-kafka wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git build-essential libpq-dev librdkafka-dev \
&& rm -rf /var/lib/apt/lists/*

# Pipenv
RUN pip install --no-cache-dir pipenv

# Copy dependency manifests first
COPY Pipfile Pipfile.lock ./
RUN PIPENV_VENV_IN_PROJECT=0 pipenv install --system --deploy --dev

# Copy the code
COPY src/ ./src

# Drop privileges
USER appuser

# Keep container idle to explicitly run producers/consumers
CMD ["sleep", "infinity"]
