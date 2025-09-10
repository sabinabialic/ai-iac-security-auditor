# Insecure Dockerfile with multiple security issues
FROM ubuntu:latest

# Running as root (security issue)
USER root

# Installing packages without pinning versions
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    sudo

# Exposing unnecessary ports
EXPOSE 22
EXPOSE 3389

# Adding secrets directly in the image (security issue)
ENV DATABASE_PASSWORD=supersecretpassword123
ENV API_KEY=sk-1234567890abcdef

# Running with unnecessary privileges
RUN chmod 777 /tmp

# Using COPY instead of ADD for security, but copying everything
COPY . /app

# Running application as root
WORKDIR /app
CMD ["./app"]
