import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import time
from ising_state import Ising

def make_chart():
    """
    Create Altair plot from pd dataframe
    """
    source = Ising.get_plot_data()
    chart = alt.Chart(source).mark_rect().encode(
        x='x:O',
        y='y:O',
        color='z:Q'
    ).interactive()
    return chart

def render_streamlit():
    st.title("Ising Model")

    chartholder = st.empty()

    Nx = st.number_input("nx", min_value = 5,value=15,max_value = 50)
    Ny = st.number_input("ny", min_value = 5,value=15,max_value = 50)
    T =  st.number_input("T", min_value = 0.0, value = 1.0, max_value = 10000.0)

    while True:
        if Nx != Ising.Nx or Ny != Ising.Ny:
            Ising.reinitialize(Nx,Ny); #Reset data
        Ising.set_beta(1.0/T)
        Ising.monte_carlo_sweep()
        chart = make_chart()
        chartholder.altair_chart(chart,use_container_width=True)
        time.sleep(1)

if __name__ == '__main__':
    render_streamlit()
    st.button("Next")
