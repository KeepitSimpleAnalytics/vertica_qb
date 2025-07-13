#!/bin/bash

echo "Starting project foundation setup..."

# Create parent directories
echo "Creating main directories: backend, frontend, ollama..."
mkdir -p backend/app frontend/public frontend/src ollama

# Create empty Python files
echo "Creating initial Python files..."
touch backend/app/__init__.py

# --- Backend Files ---
echo "Writing backend configuration..."

# backend/requirements.txt
cat << 'EOT' > backend/requirements.txt
fastapi==0.111.0
uvicorn[standard]==0.30.1
vertica-python==1.3.11
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
EOT

# backend/app/main.py
cat << 'EOT' > backend/app/main.py
from fastapi import FastAPI

app = FastAPI(title="Vertica Query Tool API")

@app.get("/")
def read_root():
    return {"status": "API is running"}
EOT

# backend/Dockerfile
cat << 'EOT' > backend/Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./app /app
EOT

# --- Frontend Files ---
echo "Writing frontend configuration..."

# frontend/package.json
cat << 'EOT' > frontend/package.json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-scripts": "5.0.1",
    "axios": "^1.7.2"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOT

# frontend/public/index.html
cat << 'EOT' > frontend/public/index.html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Vertica Query Tool</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOT

# frontend/src/index.js
cat << 'EOT' > frontend/src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOT

# frontend/src/App.js
cat << 'EOT' > frontend/src/App.js
import React from 'react';
function App() {
  return (
    <div>
      <h1>Vertica Query Tool</h1>
      <p>Frontend is running.</p>
    </div>
  );
}
export default App;
EOT

# frontend/Dockerfile
cat << 'EOT' > frontend/Dockerfile
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
EOT

# frontend/.dockerignore
cat << 'EOT' > frontend/.dockerignore
node_modules
build
.dockerignore
EOT

# --- Docker Compose ---
echo "Writing docker-compose.yml..."
cat << 'EOT' > docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    container_name: vertica_api
    restart: unless-stopped
    volumes:
      - ./backend/app:/app
    ports:
      - "8000:8000"
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    environment:
      - DEFAULT_QUERY_LIMIT=1000
      - MAX_QUERY_LIMIT=10000

  frontend:
    build: ./frontend
    container_name: vertica_ui
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      - backend
EOT

echo "Foundation created successfully!"
