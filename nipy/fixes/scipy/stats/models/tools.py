'''
Utility functions models code
'''

import numpy as np
import numpy.lib.recfunctions as nprf
import numpy.linalg as L
import scipy.interpolate
import scipy.linalg

#FIXME: make this more robust
# needs to not return a dummy for *every* variable...
#TODO: update docstring to show handling of ndarrays
#TODO: needs to better preserve dtype and be more flexible
# ie., if you still have a string variable in your array you don't
# want to cast it to float
def xi(data, col=None, time=None, drop=False):
    '''
    Returns an array changing categorical variables to dummy variables.

    Returns an interaction expansion on the specified variable.

    Take a structured or record array and returns an array with categorical
    variables.


    Notes
    -----
    This returns a dummy variable for EVERY distinct string.  If noconsant
    then this is okay.  Otherwise, a "intercept" needs to be designated in
    regression.  Note that STATA returns which variable is omitted when this
    is called. And it is called at runtime of fit...

    Returns the same array as it's given right now (recarray and structured
    array only).

    Where should categoricals home be?
    It is used by every (?) model.

    In STATA, you use xi -- interaction expansion for turning categorical
    into indicator variables, perhaps this is a better name.

    Should also be able to handle numeric data in addition to strings.

    Default drops the "first" group (how to define? -- have an attribute
    "dropped"?)

    Also allows to define dropped as "prevalent" for most prevalent
    or to define which variable -- the latter may be our best option for now.
    '''

#needs error checking
    if data.__class__ is np.recarray:
        if isinstance(col, int):
            col = data.dtype.names[col]
        if data.dtype.names and isinstance(col,str):
            tmp_arr = np.unique(data[col])
            tmp_dummy = (tmp_arr[:,np.newaxis]==data[col]).astype(float)
            if drop is True:
                data=nprf.drop_fields(data, col, usemask=False,
                asrecarray=type(data) is np.recarray)
            data=nprf.append_fields(data, tmp_arr, data=tmp_dummy,
                usemask=False, asrecarray=type(data) is np.recarray)
# TODO: need better column names for numerical indicators
            return data
    elif data.__class__ is np.ndarray:
        if isinstance(col, int):
            tmp_arr = np.unique(data[:,col])
            tmp_dummy = (tmp_arr[:,np.newaxis]==data[:,col]).astype(float)
            tmp_dummy = np.rollaxis(tmp_dummy, 1, 0)
            if drop is True:
                data = np.delete(data, col, axis=1).astype(float)
            data = np.column_stack((data,tmp_dummy))
            return data
        else:
            raise IndexError, "The index %s is not understood" % col

def add_constant(data):
    '''
    This appends a constant to the design matrix.

    It checks to make sure a constant is not already included.  If there is
    at least one column of ones then an array of the original design is
    returned.

    Parameters
    ----------
    data : array-like
        `data` is the column-ordered design matrix

    Returns
    -------
    data : array
        The original design matrix with a constant (column of ones)
        as the last column.
    '''
    data = np.asarray(data)
    if np.any(data[0]==1):
        ind = np.squeeze(np.where(data[0]==1))
        if ind.size == 1 and np.all(data[:,ind] == 1):
            return data
        elif ind.size > 1:
            for col in ind:
                if np.all(data[:,col] == 1):
                    return data
    data = np.column_stack((data, np.ones((data.shape[0], 1))))
    return data

#class HCCM(OLSModel):
#    """
#    Heteroskedasticity-Corrected Covariance Matrix estimation

#    Parameters
#    ----------
#    design : array-like
#
#    Methods
#    -------
#    Same as OLSModel except that fit accepts an additional argument
#    to define the type of correction.

#    """

#    def __init__(self, design, hascons=True):
#        super(HCCM, self).__init__(design, hascons)

#    def fit(self, Y, robust='HC0'):
#        '''
#        Parameters
#        -----------
#        Y : array-like
#            Response variable

#        robust : string, optional
#            Estimation of the heteroskedasticity robust covariance matrix
#            Values can be "HC0", "HC1", "HC2", or "HC3"
#            Default is HC0

#        '''

#        Z = self.whiten(Y)
#        lfit = RegressionResults(np.dot(self.calc_beta, Z), Y,
#                       normalized_cov_beta=self.normalized_cov_beta)
#        lfit.predict = np.dot(self.design, lfit.beta)
#        lfit.resid = Z - np.dot(self.wdesign, lfit.beta)
#        if robust is "HC0": # HC0 (White 1980)
#            lfit.scale = np.diag(lfit.resid**2)
#        elif robust is "HC1": # HC1-3 MacKinnon and White (1985)
#            lfit.scale = lfit.n/(lfit.n-lfit.df_model-1)*(np.diag(lfit.resid**2))
#        elif robust is "HC2":
#            h=np.diag(np.dot(np.dot(self.wdesign,self.normalized_cov_beta),
#                    self.wdesign.T))
#            lfit.scale=np.diag(lfit.resid**2/(1-h))
#        elif robust is "HC3":
#             h=np.diag(np.dot(np.dot(self.wdesign,self.normalized_cov_beta),
#                    self.wdesign.T))
#             lfit.scale=np.diag((lfit.resid/(1-h))**2)
#        else:
#            raise ValueError, "Robust option %s not understood" % robust
#        lfit.df_resid = self.df_resid
#        lfit.df_model = self.df_model
#        lfit.Z = Z
#        lfit.calc_beta = self.calc_beta # needed for cov_beta()
#        return lfit

def isestimable(C, D):
    """
    From an q x p contrast matrix C and an n x p design matrix D, checks
    if the contrast C is estimable by looking at the rank of vstack([C,D]) and
    verifying it is the same as the rank of D.
    """
    if C.ndim == 1:
        C.shape = (C.shape[0], 1)
    new = np.vstack([C, D])
    if rank(new) != rank(D):
        return False
    return True

def recipr(X):
    """
    Return the reciprocal of an array, setting all entries less than or
    equal to 0 to 0. Therefore, it presumes that X should be positive in
    general.
    """
    x = np.maximum(np.asarray(X).astype(np.float64), 0)
    return np.greater(x, 0.) / (x + np.less_equal(x, 0.))

def mad(a, c=0.6745, axis=0):
    """
    Median Absolute Deviation:

    median(abs(a - median(a))) / c

    """

    _shape = a.shape
    a.shape = np.product(a.shape,axis=0)
    m = np.median(np.fabs(a - np.median(a))) / c
    a.shape = _shape
    return m

def recipr0(X):
    """
    Return the reciprocal of an array, setting all entries equal to 0
    as 0. It does not assume that X should be positive in
    general.
    """
    test = np.equal(np.asarray(X), 0)
    return np.where(test, 0, 1. / X)

def clean0(matrix):
    """
    Erase columns of zeros: can save some time in pseudoinverse.
    """
    colsum = np.add.reduce(matrix**2, 0)
    val = [matrix[:,i] for i in np.flatnonzero(colsum)]
    return np.array(np.transpose(val))

def rank(X, cond=1.0e-12):
    """
    Return the rank of a matrix X based on its generalized inverse,
    not the SVD.
    """
    X = np.asarray(X)
    if len(X.shape) == 2:
        D = scipy.linalg.svdvals(X)
        return int(np.add.reduce(np.greater(D / D.max(), cond).astype(np.int32)))
    else:
        return int(not np.alltrue(np.equal(X, 0.)))

def fullrank(X, r=None):
    """
    Return a matrix whose column span is the same as X.

    If the rank of X is known it can be specified as r -- no check
    is made to ensure that this really is the rank of X.

    """

    if r is None:
        r = rank(X)

    V, D, U = L.svd(X, full_matrices=0)
    order = np.argsort(D)
    order = order[::-1]
    value = []
    for i in range(r):
        value.append(V[:,order[i]])
    return np.asarray(np.transpose(value)).astype(np.float64)

class StepFunction:
    """
    A basic step function: values at the ends are handled in the simplest
    way possible: everything to the left of x[0] is set to ival; everything
    to the right of x[-1] is set to y[-1].

    Examples
    --------
    >>> from numpy import arange
    >>> from models.tools import StepFunction
    >>>
    >>> x = arange(20)
    >>> y = arange(20)
    >> f = StepFunction(x, y)
    >>>
    >>> print f(3.2)
    3.0
    >>> print f([[3.2,4.5],[24,-3.1]])
    [[  3.   4.]
     [ 19.   0.]]
    """

    def __init__(self, x, y, ival=0., sorted=False):

        _x = np.asarray(x)
        _y = np.asarray(y)

        if _x.shape != _y.shape:
            raise ValueError, 'in StepFunction: x and y do not have the same shape'
        if len(_x.shape) != 1:
            raise ValueError, 'in StepFunction: x and y must be 1-dimensional'

        self.x = np.hstack([[-np.inf], _x])
        self.y = np.hstack([[ival], _y])

        if not sorted:
            asort = np.argsort(self.x)
            self.x = np.take(self.x, asort, 0)
            self.y = np.take(self.y, asort, 0)
        self.n = self.x.shape[0]

    def __call__(self, time):

        tind = np.searchsorted(self.x, time) - 1
        _shape = tind.shape
        return self.y[tind]

def ECDF(values):
    """
    Return the ECDF of an array as a step function.
    """
    x = np.array(values, copy=True)
    x.sort()
    x.shape = np.product(x.shape,axis=0)
    n = x.shape[0]
    y = (np.arange(n) + 1.) / n
    return StepFunction(x, y)

def monotone_fn_inverter(fn, x, vectorized=True, **keywords):
    """
    Given a monotone function x (no checking is done to verify monotonicity)
    and a set of x values, return an linearly interpolated approximation
    to its inverse from its values on x.
    """

    if vectorized:
        y = fn(x, **keywords)
    else:
        y = []
        for _x in x:
            y.append(fn(_x, **keywords))
        y = np.array(y)

    a = np.argsort(y)

    return scipy.interpolate.interp1d(y[a], x[a])

