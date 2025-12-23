FROM node:20.11.0-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Enable Corepack for Yarn v3
RUN corepack enable && corepack prepare yarn@3.6.4 --activate

# Copy the broken workspace app
COPY app/ /app/

# Set Node environment
ENV NODE_ENV=development
