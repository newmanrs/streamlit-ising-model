import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import time
from ising_state import Ising

def make_chart(rect_size=5):
    """
    Create Altair plot from pd dataframe
    """
    source = Ising.get_plot_data()
    chart = alt.Chart(source).mark_rect().encode(
        x='x:O',
        y='y:O',
        color='spin:Q',
        tooltip=['x','y','spin']
    ).properties(
        height = {'step':rect_size},
        width  = {'step':rect_size}
    ).configure_scale(bandPaddingInner=0.1)
    return chart

def render_streamlit():
    st.title("Ising Model")

    st.write(r'''
    Basic 2D Ising lattice Monte Carlo simulator using 4 neighbors and periodic boundary conditions.  The Hamiltonian $H$ is then given then by


    $H=-\sum_{i,j}\sigma_{i}\sigma_{j}$

    where $\sigma_{i}$ is the spin of site $i$, and this summation is carried out over adjacent neighbors $j$.
    ''')

    #st.latex(r'''
    #H = - \sum_{i,j} \sigma_{i} \sigma_{j}
    #''')

    chartholder = st.empty()
    Nx = st.sidebar.number_input("Nx (Sites on X axis)", min_value = 3,value=25,max_value = 100)
    Ny = st.sidebar.number_input("Ny (Sites on Y axis)", min_value = 3,value=25,max_value = 100)
    T =  st.sidebar.number_input("T (Temperature)", min_value = 0.0001, value = 2.2692, max_value = 100.0)
    sweeps_per_frame = st.sidebar.number_input("Sweeps per frame", min_value = 1, value = 100, max_value=10000)
    sleep_timer = st.sidebar.number_input("Sleep time between loops", min_value = 0.0, value = 0.0, max_value = 30.0)

    chart_rect_width = 500 // np.max([Nx,Ny])

    st.write(r'''
    Each Monte Carlo sweep is Nx*Ny random moves applied to the simulation board.  Moves are accepted with probability $\exp(-E/kT)$ where units are set such that Boltzmann's constant $k=1$.  Adjust sweeps per frame or add sleep time between loop iterations if the simulation is outpacing streamlit's ability to redraw the Ising model.  Critical point is near the default temperature of 2.27.
    ''')

    while True:
        if Nx != Ising.Nx or Ny != Ising.Ny:
            Ising.reinitialize(Nx,Ny); #Reset data
        Ising.set_beta(1.0/T)

        Ising.monte_carlo_sweep(sweeps_per_frame)

        with chartholder.beta_container():
            chart = make_chart(chart_rect_width)
            st.altair_chart(chart,use_container_width=True)
            st.text("Currently on MC sweep {}".format(Ising.sweeps))
            st.text("Temperature is {}".format(1/Ising.beta))
        if sleep_timer > 0:
            time.sleep(sleep_timer)

if __name__ == '__main__':
    render_streamlit()
