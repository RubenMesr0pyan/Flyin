.PHONY: install run debug clean lint lint-strict

install:
	pip install -r requirements.txt

run:
	python3 -m fly_in.main $(ARGS)

debug:
	python3 -m pdb -m fly_in.main $(ARGS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
