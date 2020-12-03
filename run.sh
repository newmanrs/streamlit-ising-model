#!/bin/zsh

echo "Trying to source virtual env at ./venv/bin/activate"
source venv/bin/activate
python3 --version
streamlit run ising_main.py
