.PHONY : help build-backend up up-build down logs ps test-back coverage

help:
	@echo "Available commands:"
	@echo "  build-backend - Build the backend Docker image"
	@echo "  up - Start all services in detached mode"
	@echo "  up-build - Start all services in detached mode with build"
	@echo "  down - Stop and remove all services"
	@echo "  logs - Show the logs of all services"
	@echo "  ps - List the running containers"
	@echo "  test-back - Run the backend tests"
	@echo "  coverage - Run the backend tests with coverage"

build-backend:
	docker build -t backend:1.0 ./backend

run-local:
	poetry run uvicorn app-main:app -reload

up:
	docker-compose up -d

up-build:
	docker-compose up -d --build

down:
	docker-compose down

logs:
	docker-compose logs -f

ps:
	docker-compose ps

test-back:
	cd backend && poetry run pytest

coverage:
	cd backend && poetry run pytest --cov=app