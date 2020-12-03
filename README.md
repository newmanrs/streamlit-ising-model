# streamlit-ising-model

Basic 2D Ising model simulation with no external field, with some basic controls for system size and temperature.  Frontend provided via streamlit, running the Ising model in a continuous loop.  Maybe someone will find this useful as a teaching model letting students play with system size and temperature to observe the Ising phase transition.

## Installation
Assuming a working python3 install, after cloning and entering the project directory:
```
pip3 install -r requirements.txt
./run.sh
```
For more details, consult the documentation for [streamlit](https://docs.streamlit.io/en/stable/).

## Limitations 
Local streamlit server should only be accessed in one tab (user) due to the simulation state being stored in the Ising module.  Resizing Nx/Ny in several tabs is likely to cause a crash. Fixing this to be a multi-user streamlit app will need the Ising model refactored into a streamlit SessionState to have per-user sessions.
