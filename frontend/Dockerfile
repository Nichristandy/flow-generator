FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy application code
COPY . .

# Build the Next.js application
RUN npm run build

# Expose the application port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
