# Stage 1: Build the React app
FROM node:18 AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build
# Stage 2: Serve the built app with Nginx
FROM nginx:1.25-alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
