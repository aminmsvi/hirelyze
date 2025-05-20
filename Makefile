run:
	streamlit run src/app.py

lint:
	ruff check .
	isort .

format:
	ruff check --fix .
	isort .

deps-dev:
	pip install -r requirements/dev.txt

deps:
	pip install -r requirements.txt
