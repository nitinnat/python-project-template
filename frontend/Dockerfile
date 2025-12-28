# Frontend Dockerfile for React + Vite application
FROM node:20-alpine

# Set work directory
WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./

# Use npm install if package-lock.json doesn't exist, otherwise use npm ci
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy application code
COPY . .

# Build the application (for production)
ARG NODE_ENV=development
RUN if [ "$NODE_ENV" = "production" ]; then npm run build; fi

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5173 || exit 1

# Development: Run dev server
# Production: Run preview server (or use nginx)
CMD ["npm", "run", "dev", "--", "--host"]
