.PHONY: all install run debug test lint lint-strict clean fclean

all: install

install:
	poetry install

run:
	poetry run python main.py $(MAP)

debug:
	poetry run python -m pdb main.py $(MAP)

test:
	poetry run pytest tests/

lint:
	poetry run flake8 . --exclude=.venv
	poetry run mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs --exclude .venv

lint-strict:
	poetry run flake8 . --exclude=.venv
	poetry run mypy . --strict --exclude .venv

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name ".mypy_cache" -exec rm -rf {} +

fclean: clean
	poetry env remove --all
