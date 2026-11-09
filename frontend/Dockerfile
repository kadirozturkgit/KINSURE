# Build the Angular frontend and serve it with a same-origin API proxy.
FROM node:22-alpine AS build

WORKDIR /workspace/frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
COPY images/ ../images/
RUN npm run build

FROM nginx:1.27-alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /workspace/frontend/dist/kinsure/browser /usr/share/nginx/html

EXPOSE 8080
