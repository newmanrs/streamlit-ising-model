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
    chart_title = "Ising State for Nx = {}, Ny = {}, sweep = {}".format(
        Ising.Nx, Ising.Ny, Ising.sweeps)
    chart = alt.Chart(source).mark_rect().encode(
        x='x:O',
        y='y:O',
        color='spin:Q',
        tooltip=['x','y','spin','energy']
    ).properties(
        height = {'step':rect_size},
        width  = {'step':rect_size},
        title = chart_title
    ).configure_scale(bandPaddingInner=0.1)

    chart.configure_title(
        fontSize=20,
        anchor='start'
    )

    return chart

def render_streamlit():
    st.title("Ising Model")

    st.write(r'''
    Basic 2D Ising lattice Monte Carlo simulator using 4 neighbors and periodic boundary conditions.  The Hamiltonian $H$ is then given then by


    $H=-\sum_{i,j}\sigma_{i}\sigma_{j}$

    where $\sigma_{i}$ is the spin of site $i$, and this summation is carried out over four adjacent neighbors $j$.
    ''')

    #st.latex(r'''
    #H = - \sum_{i,j} \sigma_{i} \sigma_{j}
    #''')

    chartholder = st.empty()
    Nx = st.sidebar.number_input("Nx (Sites on X axis)", min_value = 3,value=50,max_value = 400)
    Ny = st.sidebar.number_input("Ny (Sites on Y axis)", min_value = 3,value=50,max_value = 400)
    T =  st.sidebar.number_input("T (Temperature)", min_value = 0.0001, value = 2.2692, max_value = 100.0,format="%.4f")
    sweeps_per_frame = st.sidebar.number_input("Sweeps per frame", min_value = 1, value = 25, max_value=10000)
    sleep_timer = st.sidebar.number_input("Sleep time between loops", min_value = 0.0, value = 0.0, max_value = 60.0)

    chart_rect_width = 500 // np.max([Nx,Ny])  #Heuristic for making plot look reasonable
    if chart_rect_width == 0:
        chart_rect_width = 1  #min width 1 px

    st.write(r'''
    Each Monte Carlo sweep is $N_x$$N_y$ random Monte Carlo moves applied to the simulation board.  Moves are accepted with probability $\exp(-E/kT)$ where units are set such that Boltzmann's constant $k=1$.  Adjust sweeps per frame or add sleep time between loop iterations if the simulation is outpacing streamlit's ability to redraw the Ising model.  Critical point is near the default temperature of 2.27.
    ''')

    while True:
        if Nx != Ising.Nx or Ny != Ising.Ny:
            Ising.reinitialize(Nx,Ny); #Reset data
        Ising.set_beta(1.0/T)

        Ising.monte_carlo_sweep(sweeps_per_frame)

        with chartholder.beta_container():
            chart = make_chart(chart_rect_width)
            st.altair_chart(chart,use_container_width=True)
            st.text("Currently on MC sweep {}, proceeding at {} sweeps per second.".format(Ising.sweeps, Ising.sweeps_per_second))
            st.text("Mean energy is {:.5f}.".format(Ising.df['energy'].sum() / (Ising.Nx * Ising.Ny)))
            st.text("Mean spin is {:.3f}.".format(Ising.df['spin'].sum() / (Ising.Nx * Ising.Ny)))
            st.text("MC acceptance rate {}.".format(Ising.accepted_count / (Ising.accepted_count + Ising.rejected_count)))
        if sleep_timer > 0:
            time.sleep(sleep_timer)

if __name__ == '__main__':
    render_streamlit()
