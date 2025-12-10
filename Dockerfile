# ---- Stage 1: builder ------------------------------
# Use full Debian-based Python (not slim/alpine). PIN BY DIGEST.
FROM python:3.14-slim-bookworm@sha256:404ca55875fc24a64f0a09e9ec7d405d725109aec04c9bf0991798fd45c7b898 AS builder

WORKDIR /app

# Minimal system dependencies for psycopg2 / confluent-kafka wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git build-essential libpq-dev librdkafka-dev \
&& rm -rf /var/lib/apt/lists/*

# Pipenv
RUN pip install --no-cache-dir pipenv

# Copy dependency manifests
COPY Pipfile Pipfile.lock ./

# Install prod dependencies into the system site-packages
# Drop --dev here for a runtime image. Use a separate CI image for dev deps.
RUN PIPENV_VENV_IN_PROJECT=0 pipenv install --system --deploy

# Copy source (for type-checking / static analysis / building wheels if needed)
COPY src/ ./src

# ---- Stage 2: runtime ------------------------------
FROM python:3.14-slim-bookworm@sha256:404ca55875fc24a64f0a09e9ec7d405d725109aec04c9bf0991798fd45c7b898

# Security / behaviro envs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONNOUSERSITE=1 \
    PYTHONIOENCODING=UTF-8 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    librdkafka1 \
 && rm -rf /var/lib/apt/lists/*

# Create non-root user
ARG APP_UID=10001
RUN useradd -u ${APP_UID} -m appuser

WORKDIR /app



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
