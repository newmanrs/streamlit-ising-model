.phony: install

install:
	pip3 install --quiet -r requirements.txt
	streamlit run ising_main.py
