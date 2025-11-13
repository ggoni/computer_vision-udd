# syntax=docker/dockerfile:1.7
FROM node:18-alpine AS base

# Set working directory
WORKDIR /app

# Install dependencies for node-gyp
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    curl

# ============================================================================
# DEPENDENCIES STAGE
# ============================================================================
FROM base AS dependencies

# Copy package files
COPY package*.json ./

# Install dependencies with cache mount
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production && \
    npm cache clean --force

# ============================================================================
# BUILD STAGE
# ============================================================================
FROM dependencies AS build

# Install development dependencies
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copy source code
COPY src ./src
COPY public ./public
COPY index.html ./
COPY vite.config.ts ./
COPY tsconfig.json ./
COPY tsconfig.node.json ./

# Build the application
RUN npm run build

# ============================================================================
# PRODUCTION STAGE
# ============================================================================
FROM nginx:alpine AS production

# Create non-root user
RUN addgroup -g 1001 -S appuser && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G appuser appuser

# Copy built application
COPY --from=build --chown=appuser:appuser /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Set proper permissions and create pid directory
RUN chown -R appuser:appuser /usr/share/nginx/html && \
    chown -R appuser:appuser /var/cache/nginx && \
    chown -R appuser:appuser /var/log/nginx && \
    chown -R appuser:appuser /etc/nginx/conf.d && \
    mkdir -p /tmp && \
    chown -R appuser:appuser /tmp

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx (run as root to avoid permission issues)
CMD ["nginx", "-g", "daemon off;"]