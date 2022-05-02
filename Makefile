.phony: install lint

install:
	pip3 install --quiet -r requirements.txt
	streamlit run main.py

lint:
	flake8
