'''
Defines the link functions to be used with GLM families.
'''

import numpy as np
import scipy.stats

#TODO: are the instance actually "aliases"
# I used this terminology in varfuncs as well -ss

class Link(object):

    """
    A generic link function for one-parameter exponential family.

    `Link` does nothing, but lays out the methods expected of any subclass.

    Methods
    --------
    call
        Return the value of the link function g(p) = z
    inverse
        Return the value of the inverse of the link function g^(-1)(z) = p
        z is usually the linear predictor of the transformed variable
        in the IRLS algorithm for GLM.
    deriv
        Return the value of the derivative of the link function g'(p)
    """

    def __call__(self, p):
        return NotImplementedError

    def inverse(self, z):
        return NotImplementedError

    def deriv(self, p):
        return NotImplementedError

class Logit(Link):
    """
    The logit transform as a link function

    Methods
    -------
    call
        Returns the logit transform at `p`
        g(p) = log(p / (1 - p))
    inverse
        Returns the inverse of the logit transform of `z`
        g^(-1)(`z`) = exp(`z`)/(1 + exp(`z`))
    derivative
        Returns the derivative of the logit transform at `p`
        g'(p) = 1 / (x * (1 - x))

    Notes
    -----
    call and derivative use a private method _clean to make trim p by
    1e-10 so that p is in (0,1)

    Alias of Logit:
    logit = Logit()
    """

    tol = 1.0e-10

    def _clean(self, p):
        """
        Clip logistic values to range (tol, 1-tol)

        Parameters
        -----------
        p : array-like
            Probabilities

        Returns
        --------
        pclip : array
            Clipped probabilities
        """
        return np.clip(p, Logit.tol, 1. - Logit.tol)

    def __call__(self, p):
        """
        The logit transform

        Parameters
        ----------
        p : array-like
            Probabilities

        Returns
        -------
        z : array
            Logit transform of `p`

        Formulas
        --------
        g(p) = log(p / (1 - p))
        """
        p = self._clean(p)
        return np.log(p / (1. - p))

    def inverse(self, z):
        """
        Inverse of the logit transform

        Parameters
        ----------
        z : array-like
            The value of the logit transform at `p`

        Returns
        -------
        p : array
            Probabilities

        Formulas
        --------
        g^(-1)(z) = exp(z)/(1+exp(z))
        """
        t = np.exp(z)
        return t / (1. + t)

    def deriv(self, p):

        """
        Derivative of the logit transform


        INPUTS:
           p   -- probabilities

        Returns
        -------
        g'(p) : array
           Value of the derivative of logit transform at `p`

        Formulas
        --------
        g'(p) = 1 / (p * (1 - p))

        Notes
        -----
        Alias for `Logit`:
        logit = Logit()
        """
        p = self._clean(p)
        return 1. / (p * (1 - p))

logit = Logit()

class Power(Link):

    """
    The power transform as a link function

    Parameters
    ----------
    power : float
        The exponent of the power tranform

    Methods
    -------
    call
        The value of the power tranform link at `p`
        g(p) = `p`**`power`
    inverse
        The inverse of the power transorm link at `z`
        g^(-1) = `z`**(1/`power`)
    derivative
        The derivative of the power transform link at `p`
        g'(p) = `power`*`p`**(`power`-1)

    Notes
    -----
    Aliases of Power:
    inverse = Power(power=-1)
    sqrt = Power(power=.5)
    inverse_squared = Power(power=-2.)
    identity = Power(power=1.)
    """

    def __init__(self, power=1.):
        self.power = power

    def __call__(self, p):
        """
        Power transform link function

        Parameters
        ----------
        p : array-like
            Mean parameters

        Returns
        -------
        z : array-like
            Power transform of x

        Formulas
        --------
        g(p) = x**self.power
        """

        return np.power(p, self.power)

    def inverse(self, z):
        """
        Inverse of the power transform link function


        Parameters
        ----------
        `z` : array-like
            Value of the transformed mean parameters at `p`

        Returns
        -------
        `p` : array
            Mean parameters

        Formulas
        --------
        g^(-1)(`z`) = `z`**(1/`power`)
        """
        return np.power(z, 1. / self.power)

    def deriv(self, p):
        """
        Derivative of the power transform

        Parameters
        ----------
        p : array-like
            Mean parameters

        Returns
        --------
        g'(p) : array
            Derivative of power transform of `p`

        Formulas
        --------
        g'(`p`) = `power` * `p`**(`power` - 1)
        """
        return self.power * np.power(p, self.power - 1)

inverse = Power(power=-1.)
inverse.__doc__ = """

The inverse transform as a link function

Formulas
--------
g(`p`) = 1 / `p`

Notes
-----
Alias of statsmodels.family.links.Power(power=-1.)
"""

sqrt = Power(power=0.5)
sqrt.__doc__ = """

The square-root transform as a link function

Formulas
--------
g(`p`) = sqrt(`p`)

Notes
-----
Alias of statsmodels.family.links.Power(power=.5)"""

inverse_squared = Power(power=-2.)
inverse_squared.__doc__ = """

The inverse squared transform as a link function

Formulas
---------
g(`p`) = 1 / `p`**2

Notes
-----
Alias of statsmodels.family.links.Power(power=2.)
"""

identity = Power(power=1.)
identity.__doc__ = """
The identity transform as a link function

Formulas
---------
g(`p`) = `p`

Notes
-----
Alias of statsmodels.family.links.Power(power=1.)
"""

class Log(Link):

    """
    The log transform as a link function

    Methods
    -------
    call
        Returns the value of the log link function at `p`
        g(p) = log(p)
    inverse
        Returns the value of the inverse of the log link function at `z`
        g^(-1)(z) = exp(z)
    derivative
        Returns the derivative of the log link function at `p`
        g'(p) = 1/p

    Notes
    -----
    call and derivative call a private method _clean to trim the data by
    1e-10 so that p is in (0,1)

    Alias of Log:
    log = Log()
    """

    tol = 1.0e-10

    def _clean(self, x):
        return np.clip(x, Logit.tol, np.inf)

    def __call__(self, p, **extra):
        """
        Log transform link function

        Parameters
        ----------
        x : array-like
            Mean parameters

        Returns
        -------
        z : array
            log(x)

        Formulas
        ---------
        g(p) = log(p)
        """
        x = self._clean(p)
        return np.log(p)

    def inverse(self, z):
        """
        Inverse of log transform link function

        Parameters
        ----------
        z : array
            The inverse of the link function at `p`

        Returns
        -------
        p : array
            The mean probabilities given the value of the inverse `z`

        Formulas
        --------
        g^(-1)(z) = exp(z)
        """
        return np.exp(z)

    def deriv(self, p):
        """
        Derivative of log transform link function

        Parameters
        ----------
        p : array-like
            Mean parameters

        Returns
        -------
        g'(p) : array
            derivative of log transform of x

        Formulas
        --------
        g(x) = 1/x
        """
        p = self._clean(p)
        return 1. / p
log = Log()
log.__doc__ = """
The log transform as a link function

Notes
-----
log is a an alias of Log.  log = Log()
"""

#TODO: the CDFLink is untested
class CDFLink(Logit):
    """
    The use the CDF of a scipy.stats distribution as a link function

    CDFLink is a subclass of logit in order to use its _clean method
    for the link and its derivative.

    Parameters
    ----------
    dbn : scipy.stats distribution
        Default is dbn=scipy.stats.norm

    Methods
    -------
    call
        Return the value of CDF link at `p`
        g(p) = `dbn`.ppf(`p`)
    inverse
        Return the inverse of the CDF link at `z`
        g^(-1)(z) = `dbn`.cdf(`z`)
    derivative
        Return the derivative of the CDF link at `p`
        g'(`p`) = 1. / `dbn`.pdf(p)

    Notes
    -----
    The CDF link is untested.
    """

    def __init__(self, dbn=scipy.stats.norm):
        self.dbn = dbn

    def __call__(self, p):
        """
        CDF link function

        Parameters
        ----------
        p : array-like
            Mean parameters

        Returns
        -------
        z : array
           (ppf) inverse of CDF transform of p

        Formulas
        --------
        g(`p`) = `dbn`.ppf(`p`)
        """
        p = self._clean(p)
        return self.dbn.ppf(p)

    def inverse(self, z):
        """
        The inverse of the CDF link

        Parameters
        ----------
        z : array-like
            The value of the inverse of the link function at `p`

        Returns
        -------
        p : array
            Mean probabilities.  The value of the inverse of CDF link of `z`

        Formulas
        --------
        g^(-1)(`z`) = `dbn`.cdf(`z`)
        """
        return self.dbn.cdf(z)

    def deriv(self, p):
        """
        Derivative of CDF link

        Parameters
        ----------
        p : array-like
            mean parameters

        Returns
        -------
        g'(p) : array
         The derivative of CDF transform at `p`

        Formulas
        --------
        g'(`p`) = 1./ `dbn`.pdf(`p`)
        """
# Or is it
#        g'(`p`) = 1/`dbn`.pdf(`dbn`.ppf(`p`))
#TODO: make sure this is correct.
#can we just have a numerical approximation?
        p = self._clean(p)
        return 1. / self.dbn.pdf(p)

probit = CDFLink()
probit.__doc__ = """

The probit (standard normal CDF) transform as a link function

Formulas
--------
g(p) = scipy.stats.norm.ppf(p)

Notes
-----
probit is an alias of CDFLink.
probit = CDFLink()
"""

cauchy = CDFLink(dbn=scipy.stats.cauchy)
cauchy.__doc__ = """

The Cauchy (standard Cauchy CDF) transform as a link function

Formulas
--------
g(p) = scipy.stats.cauchy.ppf(p)

Notes
-----
cauchy is an alias of CDFLink.
cauch = CFGLink(dbn=scipy.stats.cauchy)
"""

#TODO: CLogLog is untested
class CLogLog(Logit):
    """
    The complementary log-log transform as a link function

    CLogLog inherits from Logit in order to have access to its _clean method
    for the link and its derivative.

    Methods
    -------
    call
        The comlementary log-log tranform at `p`
        g(`p`) = log(-log(1-`p`))
    inverse
        The inverse of the complementary log-log transform at `z`
        g^(-1) = 1 - exp(-exp('z'))
    derivative
        The derivate of the complementary log-log transform at `p
        g'(p) = -1 / (log(p) * p)

    Notes
    -----
    CLogLog is untested.
    """

    def __call__(self, p):
        """
        C-Log-Log transform link function

        Parameters
        ----------
        p : array
            Mean parameters

        Returns
        -------
        z : array
            The CLogLog transform of `p`

        Formulas
        --------
        g(p) = log(-log(1-p))
        """
        p = self._clean(p)
        return np.log(-np.log(1-p))

    def inverse(self, z):
        """
        Inverse of C-Log-Log transform link function


        Parameters
        ----------
        z : array-like
            The value of the inverse of the CLogLog link function at `p`

        Returns
        -------
        p : array
           Mean parameters

        Formulas
        --------
        g^(-1)(`z`) = 1-exp(-exp(`z`))
        """
        return 1-np.exp(-np.exp(z))

    def deriv(self, p):
        """
        Derivatve of C-Log-Log transform link function

        Parameters
        ----------
        p : array-like
            Mean parameters

        Returns
        -------
        g'(p) : array
           The derivative of the CLogLog transform link function

        Formulas
        --------
        g'(p) = - 1 / (log(p) * p)
        """
        p = self._clean(p)
        return 1. / ((p-1)*(np.log(1-p)))

cloglog = CLogLog()
cloglog.__doc__ = """
The CLogLog transform link function.

Formulas
--------
g(`p`) = log(-log(1-`p`))

Notes
-----
cloglog is an alias for CLogLog
cloglog = CLogLog()
"""

class NegativeBinomial(object):
    '''
    The negative binomial link function

    Parameters
    ----------
    alpha : float, optional
        Alpha is the ancillary parameter of the Negative Binomial link function.
        It is assumed to be nonstochastic.  The default value is 1. Permissible
        values are usually assumed to be in (.01,2).

    Methods
    -------
    call
        The value of the negative binomial link function at `p`
        g(p) = log(p/(p + 1/alpha))
    inverse
        The value of the inverse of the negative binomial link function at `z`
        g^(-1)(`z`) = 1 - exp(-exp(`z`))
    derivative
        The value of the derivative of the negative binomial link function at
        `p`
        g'(p) = - 1 / (log(p) * p)
    '''

    tol = 1.0e-10

    def __init__(self, alpha=1.):
        self.alpha = alpha

    def _clean(self, x):
        return np.clip(x, NegativeBinomial.tol, np.inf)

    def __call__(self, x):
        '''
        Negative Binomial transform link function

        Parameters
        ----------
        p : array-like
            Mean parameters

        Returns
        -------
        z : array
            The negative binomial transform of `p`

        Formulas
        --------
        g(p) = log(p/(p + 1/alpha))
        '''
        p = self._clean(p)
        return np.log(p/(p+1/self.alpha))

    def inverse(self, z):
        '''
        Inverse of the negative binomial transform

        Parameters
        -----------
        z : array-like
            The value of the inverse of the negative binomial link at `p`.
        Returns
        -------
        p : array
            Mean parameters

        Formulas
        --------
        g^(-1)(z) = exp(z)/(alpha*(1-exp(z)))
        '''
        return np.exp(z)/(self.alpha*(1-np.exp(z)))

    def deriv(self,p):
        '''
        Derivative of the negative binomial transform

        Parameters
        ----------
        p : array-like
            Mean parameters

        Returns
        -------
        g'(p) : array
            The derivative of the negative binomial transform link function

        Formulas
        --------
        g'(x) = 1/(x+alpha*x^2)
        '''
        return 1/(p+self.alpha*p**2)

nbinom = NegativeBinomial()
nbinom.__doc__ = """
The negative binomial link function.

Formulas
--------
g(p) = log(p/(p + 1/alpha))

Notes
-----
nbinom is an alias of NegativeBinomial.
nbinom = NegativeBinomial(alpha=1.)
"""
