.PHONY : help install show test run

POETRY := poetry run

help: 
	@echo "Makefile commands:"
	@echo "  install - Install dependencies using Poetry"
	@echo "  show    - Show installed dependencies"
	@echo "  test    - Run tests using pytest"
	@echo "  run     - Run the FastAPI application with uvicorn"

install:
	poetry install

show:
	poetry show

test:
	${POETRY} pytest

run:
	${POETRY} uvicorn backend.main:app --reload