from __future__ import print_function
from runtests.mpi import MPITest

from numpy.testing import assert_allclose
from numpy.testing.decorators import skipif
import fastpm

try:
    import nbodykit
    nbodykit.setup_logging('debug')
except ImportError:
    nbodykit = None


@MPITest([1, 4])
@skipif(nbodykit is None, "nbodykit is not installed")
def test_nbkit(comm):
    from fastpm.nbkit import FastPMParticleSource
    from nbodykit.lab import cosmology, FOF, Source
    cosmo = cosmology.Planck15
    power = cosmology.EHPower(cosmo, 0)

    linear = Source.LinearMesh(power, 256., 64, seed=400, comm=comm)
    sim = FastPMParticleSource(linear, boost=2, Nsteps=5, cosmo=cosmo)
    fof = FOF(sim, 0.2, 12)
    features = fof.find_features()
    assert_allclose(features.csize, 610, rtol=0.01)
