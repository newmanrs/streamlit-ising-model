import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import time
from ising_state import Ising

def make_chart(rect_size=20):
    """
    Create Altair plot from pd dataframe
    """
    source = Ising.get_plot_data()
    #chart = alt.Chart(source).mark_rect().encode(
    chart = alt.Chart(source).mark_rect().encode(
        x='x:O',
        y='y:O',
        color='z:Q'
    ).interactive().properties(
        height = {'step':rect_size},
        width  = {'step':rect_size}
    )
    return chart

def render_streamlit():
    st.title("Ising Model")

    chartholder = st.empty()
    Nx = st.number_input("Nx", min_value = 3,value=15,max_value = 100)
    Ny = st.number_input("Ny", min_value = 3,value=15,max_value = 100)
    T =  st.number_input("T", min_value = 0.0001, value = 2.2692, max_value = 100.0)

    chart_rect_width = 500 // np.max([Nx,Ny])

    while True:
        if Nx != Ising.Nx or Ny != Ising.Ny:
            Ising.reinitialize(Nx,Ny); #Reset data
        Ising.set_beta(1.0/T)
        Ising.monte_carlo_sweep()

        chart = make_chart(chart_rect_width)
        chartholder.altair_chart(chart,use_container_width=True)
        time.sleep(1)

if __name__ == '__main__':
    render_streamlit()
    st.button("Next")
