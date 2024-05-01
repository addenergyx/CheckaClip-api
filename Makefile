.PHONY: tests run

run:
	python3 app.py

tests:
	pytest tests/*