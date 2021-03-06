import numpy
from scipy.integrate import odeint

class PerturbationGrowth(object):
    """ Perturbation Growth coefficients of Matter

        2-LPT is implemented Radiation in the background is ignored.

        All derivatives are against lna. (order)
    """
    def __init__(self, cosmo):
        self.cosmo = cosmo
        self.Om0 = cosmo.Om0
        self.Ok0 = cosmo.Ok0
        self.Ode0 = cosmo.Ode0

        self.lna = numpy.log(numpy.logspace(-7, 0, 1024*10, endpoint=True))

        self._D1, self._D2 = self._solve()

    def efunc(self, a):
        a = numpy.asarray(a)

        Om0, Ode0, Ok0 = self.Om0, self.Ode0, self.Ok0

        return numpy.sqrt(a ** -3 * Om0 + Ok0 * a ** -2 + Ode0)

    def efunc_prime(self, a):
        """ this is dE/da."""
        Om0, Ode0, Ok0 = self.Om0, self.Ode0, self.Ok0

        a = numpy.asarray(a)
        e = self.efunc(a)
        return 0.5 / e * (-3 * (a ** -4) * Om0 + -2 * Ok0 * a ** -3)

    def D1(self, a, order=0):
        lna = numpy.log(a)
        return numpy.interp(lna, self.lna, self._D1[:, order])

    def D2(self, a, order=0):
        lna = numpy.log(a)
        return numpy.interp(lna, self.lna, self._D2[:, order])

    def f1(self, a):
        return self.D1(a, order=1) / self.D1(a, order=0)

    def f2(self, a):
        return self.D2(a, order=1) / self.D2(a, order=0)
    
    def Gp(self, a):
        """ FastPM growth factor function, eq, 19;
        """
        return self.D1(a)

    def gp(self, a):
        """
            Notice the derivative of D1 is against ln a but gp is d D1 / da, so
            gp = D1(a, order=1) / a
        """
        return self.D1(a, order=1) / a

    def Gf(self, a):
        """ FastPM growth factor function, eq, 20
        """

        return self.D1(a, 1) * a ** 2 * self.E(a)

    def gf(self, a):
        """
            Similarly, the derivative is against ln a, so
            gf = Gf(a, order=1) / a
        """
        return 1 / a * (
            self.D1(a, 2) * a ** 2 * self.E(a) \
            +  self.D1(a, 1) * (
                    a ** 2 * self.E(a, order=1)
                +   2 * a ** 2 * self.E(a))
            )

    def E(self, a, order=0):
        if order == 0:
            return self.efunc(a)
        else:
            return self.efunc_prime(a) * a

    def Hfac(self, a):
        return -2. - self.E(a, order=1) / self.E(a)

    def Om(self, a):
        return self.Om0 * a ** -3 / self.E(a) **2

    def ode(self, y, lna):
        D1, F1, D2, F2 = y
        a = numpy.exp(lna)
        hfac = self.Hfac(a)
        omega = self.Om(a)
        F1p = hfac * F1 + 1.5 * omega * D1
        D1p = F1
        F2p = hfac * F2 + 1.5 * omega * D2 - 1.5 * omega * D1 ** 2
        D2p = D1
        return D1p, F1p, D2p, F2p

    def _solve(self):
        a0 = numpy.exp(self.lna[0])
        y0 = [a0, a0, -3./7 * a0**2, -6. / 7 *a0**2]

        y = odeint(self.ode, y0, self.lna)

        v1 = []
        v2 = []
        for yi, lnai in zip(y, self.lna):
            D1, F1, D2, F2 = yi
            D1p, F1p, D2p, F2p = self.ode(yi, lnai)
            v1.append((D1, F1, F1p))
            v2.append((D2, F2, F2p))

        v1 = numpy.array(v1)
        v2 = numpy.array(v2)

        # normalization to 1 at a=1.0
        v1 /= v1[-1][0]
        v2 /= v2[-1][0]
        return v1, v2
