.PHONY: help install show test test-integration lint lint-fix run-backend \
	build-docker-backend up down build up-and-build ps db-upgrade db-migration \
	db-current db-import-grades

BACKEND_ROOT = backend/
BACKEND_SRC = backend/app
DOCKER_SRC = backend/docker
POETRY := poetry run

help: 
	@echo "Makefile commands:"
	@echo "  install - Install dependencies using Poetry"
	@echo "  show    - Show installed dependencies"
	@echo "  test    - Run tests using pytest"
	@echo "  lint    - Run code linting using ruff"
	@echo "  lint-fix - Automatically fix linting issues using ruff"
	@echo "  build-docker-backend - Build the backend Docker image"
	@echo "  up      - Start the Docker containers in detached mode"
	@echo "  down    - Stop the Docker containers"
	@echo "  build   - Build the Docker containers"
	@echo "  up-and-build - Start the Docker containers and build them"
	@echo "  ps      - List the running Docker containers"
	@echo "  db-upgrade - Upgrade the database schema using Alembic"
	@echo "  db-migration - Create a new database migration using Alembic"
	@echo "  db-current - Show the current database schema"
	@echo "  db-import-grades - Import grades into the database"

install:
	cd $(BACKEND_ROOT) && poetry install

show:
	cd $(BACKEND_ROOT) && poetry show

test:
	cd $(BACKEND_ROOT)tests/unit && ${POETRY} pytest

test-integration:
	cd $(BACKEND_ROOT) && ${POETRY} pytest tests/integration -m integration

lint:
	cd $(BACKEND_ROOT) && ${POETRY} ruff check app tests

lint-fix:
	cd $(BACKEND_ROOT) && ${POETRY} ruff check --fix app

run-backend:
	cd $(BACKEND_ROOT) && ${POETRY} uvicorn app.main:app --reload

build-docker-backend:
	cd ${BACKEND_ROOT} && docker build -f docker/Dockerfile -t lab-backend:1.0 .

up: # platform running on localhost:8888
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

up-and-build:
	docker-compose up --build -d

ps:
	docker-compose ps

db-upgrade:
	docker-compose exec -T api alembic upgrade head

db-migration: #ex.: make db-migration msg="create table users"
	cd backend && poetry run alembic revision --autogenerate -m "$(msg)"

db-current:
	cd backend && poetry run alembic current

db-import-grades:
	docker-compose exec -T api python -m app.services.import_grades
