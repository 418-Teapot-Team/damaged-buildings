# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
COPY . /app/
RUN uv venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install uvicorn fastapi

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
# RUN uv pip install uvicorn fastapi

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 80

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []
CMD ["uv", "run", "uvicorn", "--host", "0.0.0.0", "--port", "80", "main:app"]