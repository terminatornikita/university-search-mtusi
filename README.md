# Поисковая система базы знаний МТУСИ

Интеллектуальная поисковая система по внутренней базе знаний университета с использованием микросервисной архитектуры.

## Технологический стек

- **Backend:** Python, FastAPI, PostgreSQL, Elasticsearch, Redis
- **Frontend:** React, TypeScript, Vite, Nginx
- **DevOps:** Docker Compose, Prometheus, Grafana, GitHub Actions

## Запуск

```bash
cp .env.example .env
docker-compose up --build
```

## API

- Swagger UI: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/openapi.json

## Мониторинг

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Тестирование

```bash
cd backend
pytest tests/ --cov=app --cov-report=term-missing
```
