FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* tsconfig.json* ./

RUN npm ci

COPY . .

RUN npm run build

CMD ["node", "dist/index.js"]