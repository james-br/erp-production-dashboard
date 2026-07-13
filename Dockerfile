# Stage 1 — build the React frontend
FROM node:20-alpine AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2 — Python runtime serving API + static frontend
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
COPY --from=frontend /build/dist ./frontend-dist
ENV FRONTEND_DIST=/app/frontend-dist
EXPOSE 8000
CMD ["sh", "-c", "gunicorn 'app:create_app()' --preload --bind 0.0.0.0:${PORT:-8000} --workers 2"]