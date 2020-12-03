import numpy as np
from numpy.random import default_rng
import pandas as pd
import time

class IsingState():
    Nx = 10
    Ny = 10
    ist = None  #Ising board state
    iste = None #Ising board energy
    df = None  #dataframe used to plot in altair
    beta = 1
    exp_beta_e = dict()
    sweeps = 0
    neighborlist = None  #precompute neighbors
    accepted_count = None
    rejected_count = None

    rng = np.random.default_rng()


    def __init__(self, Nx, Ny):
        self.reinitialize(Nx,Ny)

    @classmethod
    def reinitialize(cls,Nx,Ny):
        cls.Nx = Nx
        cls.Ny = Ny
        cls.ist = 2*cls.rng.integers(0,2,size=(Nx,Ny))-1
        cls.iste = np.zeros(shape=(Nx,Ny),dtype=np.float64)
        cls.sweeps = 0
        cls.sweeps_per_second = 0
        cls.accepted_count = 0
        cls.rejected_count = 0

        #set up x,y for df needed to plot
        x,y = np.meshgrid(range(0,Nx),range(0,Ny))
        cls.df = pd.DataFrame(
            {'x' : x.ravel(),
             'y' : y.ravel(),
             'spin' : cls.ist.ravel(),
             'energy' : cls.iste.ravel()
            })

        cls.precompute_neighborlist()
        cls.compute_energy()

    @classmethod 
    def precompute_neighborlist(cls):
        nl = np.empty(shape=(cls.Nx,cls.Ny,4,2),dtype = np.int32)
        for i in range(cls.Nx):
            for j in range(cls.Ny):
                nij = np.empty(shape=(4,2),dtype=np.int32)
                nij[0] = (i-1,j)
                nij[1] = (i+1,j)
                nij[2] = (i,j-1)
                nij[3] = (i,j+1)
                #fix periodic boundary conditions
                for t in nij:
                    if t[0] < 0:
                        t[0] += cls.Nx
                    elif t[0] == cls.Nx:
                        t[0] -= cls.Nx
                    if t[1] < 0:
                        t[1] += cls.Ny
                    elif t[1] == cls.Ny:
                        t[1] -= cls.Ny
                nl[i][j] = nij
        cls.neighborlist = nl

    @classmethod
    def get_plot_data(cls):
        """
        Updates df with ising data to put into Altair plot
        """
        cls.df['spin'] = cls.ist.ravel()
        cls.df['energy'] = cls.iste.ravel()
        return cls.df

    @classmethod
    def set_beta(cls,beta):
        cls.beta = beta
        d = dict()
        for i in [4,8]:
            d[i] = np.exp(-beta*i)
        cls.exp_beta_e = d

    @classmethod
    def monte_carlo_move(cls):
        #select site
        row = cls.rng.integers(0,cls.Nx)
        col = cls.rng.integers(0,cls.Ny)
        neighbors = cls.neighborlist[row][col]
        neigh_spins = 0 #Sum spins of neighbors

        #This could probably be optimized
        for t in neighbors:
            neigh_spins += cls.ist[t[0],t[1]]
        spin = cls.ist[row,col]

        trial_delta_e = 2*spin*neigh_spins

        if trial_delta_e <= 0:
            cls.accepted_count+=1
            cls.ist[row,col]=-spin
        #elif cls.rng.random() < np.exp(-cls.beta*trial_delta_e):
        elif cls.rng.random() < cls.exp_beta_e[trial_delta_e]:
            cls.accepted_count+=1
            cls.ist[row,col]=-spin
        else:
            cls.rejected_count+=1

    @classmethod
    def compute_energy(cls):
        for row in range(cls.Nx):
            for col in range(cls.Ny):
                neighbors = cls.neighborlist[row][col]
                neigh_spins = 0 #Sum spins of neighbors
                for t in neighbors:
                    neigh_spins += cls.ist[t[0],t[1]]
                spin = cls.ist[row,col]
                cls.iste[row][col] = -spin*neigh_spins

    @classmethod
    def monte_carlo_sweep(cls,sweeps=1):
        cls.accepted_count = 0
        cls.rejected_count = 0
        tstart = time.time()
        for _ in range(0, cls.Nx * cls.Ny * sweeps):
            cls.monte_carlo_move()
        cls.sweeps+=sweeps
        cls.compute_energy()
        cls.sweeps_per_second = sweeps / (time.time() - tstart)

Ising = IsingState(3,3)
