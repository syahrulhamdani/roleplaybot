# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Set environment variables for build
# ENV VITE_SERVER_URL=https://voice-agent-server-413847466250.asia-southeast2.run.app/api
ENV VITE_SERVER_URL=http://34.128.68.230:7860/api

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine

# Install serve globally
RUN npm install -g serve

# Copy built files from builder stage
COPY --from=builder /app/dist /app/dist

# Expose port 5173
EXPOSE 5173

# Serve static files
CMD ["serve", "/app/dist", "-l", "5173", "-s"]
