# Multi-stage Dockerfile for Hospital Backend
# Stage 1: Builder - Compile C modules and collect Python dependencies

FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libssl-dev \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN pip install --no-cache-dir uv

WORKDIR /build

# Copy C module source
COPY native/ /build/native/

# Build C modules
RUN cd /build/native && \
    mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make

# Copy Python requirements
COPY backend/pyproject.toml /build/backend/
COPY backend/requirements/ /build/backend/requirements/

# Install Python dependencies
RUN cd /build/backend && \
    uv pip install --system -r requirements/prod.txt

# Stage 2: Runtime - Slim production image

FROM python:3.12-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r hospital && useradd -r -g hospital hospital

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy C libraries from builder
COPY --from=builder /build/native/build/*.so /usr/local/lib/
RUN ldconfig

# Copy application code
COPY backend/ /app/
COPY native/python/ /app/native_modules/

# Set permissions
RUN chown -R hospital:hospital /app

# Switch to non-root user
USER hospital

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

# Run gunicorn
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "gthread", \
     "--threads", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
