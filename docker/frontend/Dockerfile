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

# Copy package files for better layer caching
COPY package*.json ./

# Install production dependencies with cache mount and clean up
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production --no-audit --no-fund && \
    npm cache clean --force

# ============================================================================
# BUILD STAGE
# ============================================================================
FROM dependencies AS build

# Install ALL dependencies (including dev) for building
RUN --mount=type=cache,target=/root/.npm \
    npm ci --no-audit --no-fund

# Copy source code (done after npm install for better caching)
COPY src ./src
COPY public ./public
COPY index.html ./
COPY vite.config.ts ./
COPY tsconfig.json ./
COPY tsconfig.node.json ./

# Build the application with optimizations
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

# Health check with faster response
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx (run as root to bind to port 80)
CMD ["nginx", "-g", "daemon off;"]