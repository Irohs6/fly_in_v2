.PHONY: all install run debug test test-maps test-maps-export lint lint-strict clean fclean

all: install

install:
	poetry install

run:
	poetry run python main.py $(MAP) $(ARGS)

debug:
	poetry run python -m pdb main.py $(MAP) $(ARGS)

test:
	poetry run pytest tests/

test-maps:
	poetry run python tests/test_all_maps_terminal.py

test-maps-export:
	poetry run python tests/test_all_maps_terminal.py --output-dir tests/results_by_map

lint:
	poetry run flake8 . --exclude=.venv
	poetry run mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs --exclude .venv

lint-strict:
	poetry run flake8 . --exclude=.venv ; poetry run mypy . --strict --exclude .venv

clean:
	find . \
		\( -name .git -o -name .venv -o -name '.venv-*' \
		-o -name venv \) -prune -o \
		-type d \( -name __pycache__ -o -name .mypy_cache \
		-o -name .pytest_cache -o -name .ruff_cache \) \
		-prune -exec rm -rf {} + -o \
		-type f \( -name '*.pyc' -o -name '*.pyo' \) -exec rm -f {} +
	rm -rf tests/results_by_map
	rm -f tests/results_maps_terminal.txt

fclean: clean
	poetry env remove --all
