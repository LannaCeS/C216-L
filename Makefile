.PHONY : help install show test run

BACKEND_ROOT = backend/
BACKEND_SRC = backend/src/backend/
POETRY := poetry run

help: 
	@echo "Makefile commands:"
	@echo "  install - Install dependencies using Poetry"
	@echo "  show    - Show installed dependencies"
	@echo "  test    - Run tests using pytest"
	@echo "  run     - Run the FastAPI application with uvicorn"

install:
	cd $(BACKEND_ROOT) && poetry install

show:
	cd $(BACKEND_ROOT) && poetry show

test:
	cd $(BACKEND_ROOT) && ${POETRY} pytest

run-backend:
	cd $(BACKEND_SRC) && ${POETRY} uvicorn backend.main:app --reload

build-docker-backend:
	cd $(BACKEND_ROOT) && docker build -t lab-backend:1.0 .

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

up-and-build:
	docker-compose up --build -d

ps:
	docker-compose ps
