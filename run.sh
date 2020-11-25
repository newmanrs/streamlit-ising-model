#!/bin/zsh

echo "Trying to source virtual env at ./venv/bin/activate"
source venv/bin/activate

streamlit run ising_main.py
