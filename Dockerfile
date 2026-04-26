FROM node:20-slim

WORKDIR /app

# 1. Install Backend Dependencies
COPY backend/package*.json /app/backend/
RUN cd /app/backend && npm ci

# 2. Install & Build Frontend
COPY frontend/package*.json /app/frontend/
RUN cd /app/frontend && npm ci
COPY frontend/ /app/frontend/
RUN cd /app/frontend && npm run build

# 3. Copy Remaining Backend Source Code
COPY backend/ /app/backend/

ENV NODE_ENV=production

# Expose backend port
EXPOSE 5000

# Start backend server directly
WORKDIR /app/backend
CMD ["npm", "start"]
