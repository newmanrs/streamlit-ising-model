import numpy as np
from numpy.random import default_rng
import pandas as pd
import time


class IsingState():
    Nx = 10
    Ny = 10
    ist = None  # Ising board state
    iste = None # Ising board energy
    df = None   # dataframe used to plot in altair
    beta = 1
    exp_beta_e = dict()  # lookup table
    sweeps = 0
    neighborlist = None  # precompute neighbors
    accepted_count = None
    rejected_count = None

    rng = np.random.default_rng()


    def __init__(self, Nx, Ny):
        self.reinitialize(Nx,Ny)

    def reinitialize(self, Nx, Ny):
        self.Nx = Nx
        self.Ny = Ny
        self.ist = 2*self.rng.integers(0,2,size=(Nx,Ny))-1
        self.iste = np.zeros(shape=(Nx,Ny),dtype=np.float64)
        self.sweeps = 0
        self.sweeps_per_second = 0
        self.accepted_count = 0
        self.rejected_count = 0

        # altair plot input needs pd dataframe
        i,j = np.meshgrid(range(0,Nx),range(0,Ny))
        self.df = pd.DataFrame(
            {'i' : i.ravel(),
             'j' : j.ravel(),
             'spin' : self.ist.ravel(),
             'energy' : self.iste.ravel()
            })

        self.precompute_neighborlist()
        self.compute_energy()

    def precompute_neighborlist(self):
        nl = np.empty(shape=(self.Nx,self.Ny,4,2),dtype = np.int32)
        for i in range(self.Nx):
            for j in range(self.Ny):
                nij = np.empty(shape=(4,2),dtype=np.int32)
                nij[0] = (i-1,j)
                nij[1] = (i+1,j)
                nij[2] = (i,j-1)
                nij[3] = (i,j+1)
                #fix periodic boundary conditions
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
        self.df['spin'] = self.ist.ravel()
        self.df['energy'] = self.iste.ravel()
        return self.df

    def set_beta(self,beta):
        self.beta = beta
        #precompute exp(-beta*e) - dict lookup is faster in python
        d = dict()
        for i in [4,8]:  #Only possible energies for unbiased ising on square lattice
            d[i] = np.exp(-beta*i)
        self.exp_beta_e = d

    def monte_carlo_move(self):
        #select site
        row = self.rng.integers(0,self.Nx)
        col = self.rng.integers(0,self.Ny)
        neighbors = self.neighborlist[row][col]
        neigh_spins = 0 #Sum spins of neighbors

        #consider manual unrolling
        for t in neighbors:
            neigh_spins += self.ist[t[0],t[1]]
        spin = self.ist[row,col]

        trial_delta_e = 2*spin*neigh_spins

        if trial_delta_e <= 0:
            self.accepted_count+=1
            self.ist[row,col]=-spin
        elif self.rng.random() < self.exp_beta_e[trial_delta_e]:
            self.accepted_count+=1
            self.ist[row,col]=-spin
        else:
            self.rejected_count+=1

    def compute_energy(self):
        for row in range(self.Nx):
            for col in range(self.Ny):
                neighbors = self.neighborlist[row][col]
                neigh_spins = 0 #Sum spins of neighbors
                for t in neighbors:
                    neigh_spins += self.ist[t[0],t[1]]
                spin = self.ist[row,col]
                self.iste[row][col] = -spin*neigh_spins

    def monte_carlo_sweep(self,sweeps=1):
        self.accepted_count = 0
        self.rejected_count = 0
        tstart = time.time()
        for _ in range(0, self.Nx * self.Ny * sweeps):
            self.monte_carlo_move()
        self.sweeps+=sweeps
        self.compute_energy()
        self.sweeps_per_second = sweeps / (time.time() - tstart)


Ising = IsingState(3,3)
