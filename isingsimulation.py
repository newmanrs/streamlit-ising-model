import numpy as np
import pandas as pd
import time


class IsingSimulation():

    Nx = None
    Ny = None
    spins = None     # Ising board state
    energies = None  # Ising board energy
    df = None        # dataframe used to plot in altair
    beta = None      # 1/T (temperature)
    exp_beta_e = dict()  # discrete lookup table
    sweeps = 0
    neighborlist = None  # precompute neighbors
    accepted_count = None
    rejected_count = None
    rng = np.random.default_rng()

    def __init__(self, Nx, Ny):
        self.reinitialize(Nx, Ny)

    def reinitialize(self, Nx, Ny):
        if self.beta is None:
            self.set_beta(1 / 2.2692)
        self.Nx = Nx
        self.Ny = Ny
        # Initialize spins to random +1, -1
        self.spins = 2*self.rng.integers(0, 2, size=(Nx, Ny))-1
        self.energies = np.zeros(
            shape=(Nx, Ny),
            dtype=np.float32
            )
        self.sweeps = 0
        self.sweeps_per_second = 0
        self.accepted_count = 0
        self.rejected_count = 0

        # altair plot input needs pd dataframe
        i, j = np.meshgrid(range(0, Nx), range(0, Ny))
        self.df = pd.DataFrame(
            {
                'i': i.ravel(),
                'j': j.ravel(),
                'spin': self.spins.ravel(),
                'energy': self.energies.ravel()
            }
            )

        self.precompute_neighborlist()
        self.compute_energy()

    def precompute_neighborlist(self):
        # row, col index for each site into 4 i,j pairs of neighbors
        nl = np.empty(
            shape=(self.Nx, self.Ny, 4, 2),
            dtype=np.int32
            )
        for i in range(self.Nx):
            for j in range(self.Ny):
                nij = np.empty(shape=(4, 2), dtype=np.int32)
                nij[0] = (i-1, j)
                nij[1] = (i+1, j)
                nij[2] = (i, j-1)
                nij[3] = (i, j+1)
                # fix periodic boundary conditions
                for t in nij:
                    if t[0] < 0:
                        t[0] += self.Nx
                    elif t[0] == self.Nx:
                        t[0] -= self.Nx
                    if t[1] < 0:
                        t[1] += self.Ny
                    elif t[1] == self.Ny:
                        t[1] -= self.Ny
                nl[i][j] = nij
        self.neighborlist = nl

    def get_plot_data(self):
        """
        Updates df with ising data to put into Altair plot
        """
        self.df['spin'] = self.spins.ravel()
        self.df['energy'] = self.energies.ravel()
        return self.df

    def set_beta(self, beta):
        self.beta = beta
        # precompute exp(-beta*e) - dict lookup is faster in python
        d = dict()
        for i in [4, 8]:  # only possible delta E from flips
            d[i] = np.exp(-beta*i)
        self.exp_beta_e = d

    def monte_carlo_move(self):

        # select site
        row = self.rng.integers(0, self.Nx)
        col = self.rng.integers(0, self.Ny)
        neighbors = self.neighborlist[row][col]
        neigh_spins = 0  # Sum spins of neighbors

        # iterate over neighbors
        for t in neighbors:
            neigh_spins += self.spins[t[0], t[1]]
        spin = self.spins[row, col]

        trial_delta_e = 2*spin*neigh_spins

        # Favorable delta e, accept spin flip
        if trial_delta_e <= 0:
            self.accepted_count += 1
            self.spins[row, col] = -spin
        # Roll Monte Carlo move rand[0,1) vs exp(-beta*E)
        #  energy is a lookup table over discrete values
        #  of e.
        elif self.rng.random() < self.exp_beta_e[trial_delta_e]:
            self.accepted_count += 1
            self.spins[row, col] = -spin
        # Reject mc move (do nothing to state)
        else:
            self.rejected_count += 1

    def compute_energy(self):

        for row in range(self.Nx):
            for col in range(self.Ny):
                neighbors = self.neighborlist[row][col]
                neigh_spins = 0  # Sum spins of neighbors
                for t in neighbors:
                    neigh_spins += self.spins[t[0], t[1]]
                spin = self.spins[row, col]
                self.energies[row][col] = -spin*neigh_spins

    def monte_carlo_sweep(self, sweeps=1):

        self.accepted_count = 0
        self.rejected_count = 0
        tstart = time.time()
        for _ in range(0, self.Nx * self.Ny * sweeps):
            self.monte_carlo_move()
        self.sweeps += sweeps
        self.compute_energy()
        self.sweeps_per_second = sweeps / (time.time() - tstart)


if __name__ == '__main__':
    """
    Crude benchmark test
    """
    Nx = 40
    Ny = 40
    isim = IsingSimulation(Nx, Ny)
    isim.monte_carlo_sweep(5)
    tstart = time.time_ns()
    sweeps = 100
    isim.monte_carlo_sweep(sweeps)
    tend = time.time_ns()
    print(f"{Nx=}, {Ny=}, {sweeps=}, time={(tend-tstart)/1000000}ms")
