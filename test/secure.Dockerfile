# Secure Dockerfile following best practices
FROM ubuntu:20.04

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install packages with pinned versions and clean up
RUN apt-get update && apt-get install -y \
    curl=7.68.0-1ubuntu2.22 \
    ca-certificates=20230311ubuntu0.20.04.1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Only expose necessary ports
EXPOSE 8080

# Use build args for secrets (passed at build time, not stored in image)
ARG DATABASE_URL
ARG API_ENDPOINT

# Copy only necessary files with specific ownership
COPY --chown=appuser:appuser ./app /app/
COPY --chown=appuser:appuser ./config /app/config/

# Set working directory
WORKDIR /app

# Switch to non-root user
USER appuser

# Use exec form of CMD
CMD ["./app", "--port=8080"]
