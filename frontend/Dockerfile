# Multi-stage build for a React (or other static SPA) frontend
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies (use package-lock.json if present)
COPY package*.json ./
RUN npm ci --silent

# Copy source and build
COPY . .
ARG NODE_ENV=production
ENV NODE_ENV=${NODE_ENV}
RUN npm run build

# Serve with nginx
FROM nginx:stable-alpine
COPY --from=builder /app/build /usr/share/nginx/html

# Optional: replace nginx.conf if you need SPA fallback for client-side routing
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]