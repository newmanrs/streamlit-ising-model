import numpy as np
from numpy.random import default_rng
import pandas as pd

class IsingState():
    Nx = 10
    Ny = 10
    ist = None  #Ising board state
    xr = None #precomputing part of meshgrid for plot output
    yr = None
    beta = 1

    rng = np.random.default_rng()

    def __init__(self, Nx, Ny):
        self.reinitialize(Nx,Ny);

    @classmethod
    def reinitialize(cls,Nx,Ny):
        cls.Nx = Nx
        cls.Ny = Ny
        cls.ist = 2*cls.rng.integers(0,2,size=(Nx,Ny))-1;
        x,y = np.meshgrid(range(0,Nx),range(0,Ny))
        cls.xr = x.ravel()  #x column for plot df
        cls.yr = y.ravel()  #y ''

    @classmethod
    def get_plot_data(cls):
        """
        Convert the ising data to a dataframe compatible with Altair.
        """
        #TODO: If the size hasn't changed, it would be better
        # to mutate the df in place than create a new one.
        ir = cls.ist.ravel()
        df = pd.DataFrame({'x' : cls.xr, 'y' : cls.yr, 'z' : ir})
        return df

    @classmethod
    def set_beta(cls,beta):
        cls.beta = beta

    @classmethod
    def monte_carlo_move(cls):
        #select site
        row = cls.rng.integers(0,cls.Nx)
        col = cls.rng.integers(0,cls.Ny)
        neighbors = [[row-1, col], [row+1,col],[row,col-1],[row,col+1]]
        #periodic bcs
        neigh_spins = 0; #Sum spins of neighbors
        for t in neighbors:
            if t[0] < 0:
                t[0] += cls.Nx
            elif t[0] == cls.Nx:
                t[0] -= cls.Nx
            if t[1] < 0:
                t[1] += cls.Ny
            elif t[1] == cls.Ny:
                t[1] -= cls.Ny;
            neigh_spins += cls.ist[t[0],t[1]];
        spin = cls.ist[row,col]
        curr_e = -spin*neigh_spins
        trial_e = spin*neigh_spins
        #print("curr_e {}, trial e {}".format(curr_e, trial_e))
        #print("acc thres = {}".format(np.exp(-cls.beta*(trial_e - curr_e))))
        #print("beta {}".format(cls.beta))

        #Optimize this?
        if cls.rng.random() < np.exp(-cls.beta*(trial_e - curr_e)):
            cls.ist[row,col]*=-1

    @classmethod
    def monte_carlo_sweep(cls):
        for _ in range(0, cls.Nx * cls.Ny):
            cls.monte_carlo_move()

Ising = IsingState(10,10);
