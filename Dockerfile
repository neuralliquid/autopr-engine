# Multi-stage build for AutoPR Engine
# Stage 1: Build environment
FROM python:3.13-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy source code
COPY . .

# Build the package
RUN pip install -e .

# Run tests (optional, can be disabled for faster builds)
ARG RUN_TESTS=true
RUN if [ "$RUN_TESTS" = "true" ]; then \
    pip install -r requirements-dev.txt && \
    pytest tests/ -v --tb=short; \
    fi

# Stage 2: Production environment
FROM python:3.13-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.local/bin:$PATH" \
    AUTOPR_ENV=production

# Create non-root user for security
RUN groupadd -r autopr && useradd -r -g autopr autopr

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create application directories
RUN mkdir -p /app /app/logs /app/data /app/config && \
    chown -R autopr:autopr /app

# Set working directory
WORKDIR /app

# Copy built application from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Copy additional configuration files
COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/healthcheck.py /healthcheck.py

# Make scripts executable
RUN chmod +x /entrypoint.sh /healthcheck.py

# Switch to non-root user
USER autopr

# Expose port for web server
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python /healthcheck.py

# Default environment variables
ENV AUTOPR_HOST=0.0.0.0 \
    AUTOPR_PORT=8080 \
    AUTOPR_WORKERS=1 \
    AUTOPR_LOG_LEVEL=INFO \
    AUTOPR_CONFIG_FILE=/app/config/autopr.yml

# Volume for persistent data
VOLUME ["/app/data", "/app/logs", "/app/config"]

# Entry point
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["autopr-server"]

# Labels for metadata
LABEL org.opencontainers.image.title="AutoPR Engine" \
    org.opencontainers.image.description="AI-Powered GitHub PR Automation and Issue Management" \
    org.opencontainers.image.version="1.0.0" \
    org.opencontainers.image.vendor="VeritasVault" \
    org.opencontainers.image.source="https://github.com/veritasvault/autopr-engine" \
    org.opencontainers.image.documentation="https://autopr-engine.readthedocs.io" \
    org.opencontainers.image.licenses="MIT"
