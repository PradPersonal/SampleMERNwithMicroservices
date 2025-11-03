FROM node:18-alpine

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
# (copy package*.json first to leverage Docker layer caching)
COPY package*.json ./
RUN npm install --production

# Bundle app source
COPY . .

# Default port (can be overridden by env)
ENV PORT=3000
EXPOSE 3000

# Run the service
CMD ["node", "index.js"]