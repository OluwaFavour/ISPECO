# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.11.5
FROM python:${PYTHON_VERSION}-slim AS base

# Install system dependencies.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy the source code into the container.
COPY . .

# Copy the docker entrypoint script into the container.
COPY docker_entrypoint.sh .

# Ensure docker_entrypoint.sh is executable.
RUN chmod +x /app/docker_entrypoint.sh

# Copy the entrypoint script into the container.
COPY entrypoint.sh .

# Ensure entrypoint.sh is executable.
RUN chmod +x /app/entrypoint.sh

# Expose the port that the application listens on.
EXPOSE 8000

# Set docker_entrypoint.sh as the entry point script.
ENTRYPOINT ["/app/docker_entrypoint.sh"]

# Run the application.
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "ISPECO_Core.asgi:application"]
