import altair as alt
import numpy as np
import streamlit as st
import time
from isingsimulation import IsingSimulation


def make_chart(rect_size=5):
    """
    Build altair heatmap to show simulation
    """

    Ising = st.session_state.Ising

    source = Ising.get_plot_data()

    chart_title = f"Ising State for Nx = {Ising.Nx}, " \
        f"Ny = {Ising.Ny}, sweep = {Ising.sweeps}"

    # mark_rect <--> heatmap
    chart = alt.Chart(source).mark_rect().encode(
        x='i:O',
        y='j:O',
        color=alt.Color('spin:Q'),
        tooltip=['i', 'j', 'spin', 'energy']
    ).properties(
        height={'step': rect_size},
        width={'step': rect_size},
        title=chart_title
    ).configure_scale(
        # Gap between rectangles
        bandPaddingInner=0.1
    ).configure_title(
        fontSize=16,
        anchor='start'
    )

    return chart


def render_streamlit():
    st.title("Square Lattice Ising Model")

    st.write(
        r'''
        Basic 2D Ising model Monte Carlo simulator on the square lattice with four adjacent neighbors and periodic boundary conditions.  The Hamiltonian $H$ is then given then by


        $\displaystyle \quad\quad H=-\sum_{i=0}^{N_x N_y} \sum_{j=0}^{4} \sigma_{i}\sigma_{j}$

        where $\sigma_{i}$ is the spin of site $i$, and this summation is carried out over four adjacent neighbors $j$.
        ''' # noqa : E501
        )

    chartholder = st.empty()

    # Streamlit sidebar vars can be updated at any time by user
    #  I probably ought to prefix these variables with something like input_Nx.
    Nx = st.sidebar.number_input(
        "Nx (Sites on X axis)",
        min_value=3,
        value=20,
        max_value=400)

    Ny = st.sidebar.number_input(
        "Ny (Sites on Y axis)",
        min_value=3,
        value=20,
        max_value=400)

    T = st.sidebar.number_input(
        "T (Temperature)",
        min_value=0.0001,
        value=2.2692,  # Phase transition temp
        max_value=1000.0,
        format="%.4f")

    sweeps_per_frame = st.sidebar.number_input(
        "MC sweeps between redrawing chart",
        min_value=1,
        value=25,
        max_value=1000)

    sleep_timer = st.sidebar.number_input(
        "Additional sleep time between MC sweeps",
        min_value=0.0,
        value=0.0,
        max_value=60.0)

    st.write(r'''
        Each Monte Carlo (MC) sweep is $N_x N_y$ random Monte Carlo moves applied to the simulation board.  Moves are accepted with probability $\exp(-E/kT)$ where units are set such that Boltzmann's constant $k=1$.  Adjust sweeps per frame or add sleep time between loop iterations if the simulation is outpacing streamlit's ability to redraw the Ising model.  Critical point for the ordered-disordered phase transition is near the default temperature of 2.27.
    ''') # noqa : E501

    # Heuristic for making plot look reasonable
    chart_rect_width = 500 // np.max([Nx, Ny])
    if chart_rect_width == 0:
        chart_rect_width = 1  # min width 1 px

    # Initialize Simulation
    if 'Ising' not in st.session_state:
        st.session_state['Ising'] = IsingSimulation(Nx, Ny)

    Ising = st.session_state.Ising

    # Run simulation loop while periodically updating the chart and
    # some description statistics.
    while True:

        # Reinitialize upon changing simulation size sliders
        if Nx != Ising.Nx or Ny != Ising.Ny:
            Ising.reinitialize(Nx, Ny)

        # If T changes, recompute beta
        if Ising.beta != 1/T:
            Ising.set_beta(1.0/T)

        Ising.monte_carlo_sweep(sweeps_per_frame)

        with chartholder.container():

            chart = make_chart(chart_rect_width)
            st.altair_chart(chart, use_container_width=True)

            # Text here is bound to the chart object
            st.write(
                f"Currently on MC sweep {Ising.sweeps}, "
                f"proceeding at {Ising.sweeps_per_second:0.1f} "
                f"sweeps per second."
                )
            mean_energy = Ising.df['energy'].sum() \
                / (Ising.Nx * Ising.Ny)
            st.write(f"Mean energy is {mean_energy:.3f}.")

            mean_spin = Ising.df['spin'].sum() \
                / (Ising.Nx * Ising.Ny)
            st.write(f"Mean spin is {mean_spin:.3f}.")

            acc_rate = Ising.accepted_count \
                / (Ising.accepted_count + Ising.rejected_count)
            st.write(f"Monte Carlo acceptance rate {acc_rate:.3f}.")

        if sleep_timer > 0:
            time.sleep(sleep_timer)


if __name__ == '__main__':

    render_streamlit()
