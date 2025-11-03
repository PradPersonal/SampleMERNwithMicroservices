FROM node:18-alpine

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies (copy package*.json first for layer caching)
COPY package*.json ./
RUN npm install --production

# Copy service source
COPY . .

# Default port (can be overridden with -e PORT=...)
ENV PORT=3000
EXPOSE 3000

# Start the service (adjust index.js if your entry file differs)
CMD ["node", "index.js"]