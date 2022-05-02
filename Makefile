.phony: install lint

install:
	pip3 install --quiet -r requirements.txt
	streamlit run streamlit_app.py

lint:
	flake8
