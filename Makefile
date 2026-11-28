.PHONY : help build-backend up up-build down logs ps test-backend test-frontend test e2e coverage lint-backend lint-frontend lint format check-all

help:
	@echo "Available commands:"
	@echo "  build-backend - Build the backend Docker image"
	@echo "  up - Start all services in detached mode"
	@echo "  up-build - Start all services in detached mode with build"
	@echo "  down - Stop and remove all services"
	@echo "  logs - Show the logs of all services"
	@echo "  ps - List the running containers"
	@echo "  test-backend - Run the backend tests"
	@echo "  test-frontend - Run the frontend tests"
	@echo "  test - Run both back and frontend tests"
	@echo "  e2e - Run e2e test"
	@echo "  coverage - Run the backend tests with coverage"
	@echo "  lint-backend - Run lint for the backend"
	@echo "  lint-frontend - Run lint for the frontend"
	@echo "  lint - Run lint for both back and frontend"
	@echo "  format - Formats lint for backend"
	@echo "  check-all - Runs all unit and integration tests + lint and ruff checks"

build-backend:
	docker build -t backend:1.0 ./backend

run-local:
	cd backend && poetry run uvicorn app.main:app --reload

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

test-backend:
	cd backend && poetry run pytest -v

test-frontend:
	cd frontend && npm run test:ci

test: #todos os testes
	cd backend && poetry run pytest -v
	cd frontend && npm run test:ci

build-teste2e:
	cd backend && SINGLE_USER_EMAIL=usuario@exemplo.com SINGLE_USER_PASSWORD=senha_valida \
		poetry run uvicorn app.main:app --port 8000

e2e:  ##E2E com Playwright (rodar build-teste2e em paralelo)
	cd frontend && npm run e2e

coverage:
	cd backend && poetry run pytest --cov

lint-backend:
	cd backend && poetry run ruff check .
	cd backend && poetry run ruff format --check .

lint-frontend:
	cd frontend && npm run lint
	cd frontend && npx tsc -b --noEmit

lint: lint-backend lint-frontend  ##lint de tudo

format:  #corrige lint
	cd backend && poetry run ruff check --fix .
	cd backend && poetry run ruff format .

check-all: test lint