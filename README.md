# streamlit-ising-model

Testing using streamlit to run a program that has a continuous state loop.  Might be usable as a teaching model, but the ising model update step ought to be moved into C++ with pybind11 for performance reasons (or at least a more clever numpy solution than naive loops/indexing of arrays).  It does work, however running multiple browser tabs may cause the state to conflict and crash.

TODO: Maybe add external field term to the model, and compute magnetism to better illustrate the phase transition.

TODO: Run script maybe ought to configure a venv in the local directory instead of failing.  Maybe make a docker script so this is more portable - streamlit's installer seems a bit quirky.
