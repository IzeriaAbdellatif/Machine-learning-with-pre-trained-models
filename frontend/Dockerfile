FROM node:20-alpine AS builder

WORKDIR /usr/src/app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install --silent

# Copy source and build
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /usr/src/app

# Copy only necessary files from builder
COPY --from=builder /usr/src/app/package.json ./
COPY --from=builder /usr/src/app/.next ./.next
COPY --from=builder /usr/src/app/node_modules ./node_modules

ENV NODE_ENV=production
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
  CMD wget -qO- --timeout=2 http://localhost:3000/ || exit 1

CMD ["npm", "run", "start"]
