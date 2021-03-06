import numpy as np
from scipy.stats import t, norm
from scipy import optimize, derivative
from tools import recipr
from contrast import ContrastResults

class Model(object):
    """
    A (predictive) statistical model. The class Model itself is not to be used.

    Model lays out the methods expected of any subclass.

    Parameters
    ----------
    endog : array-like
        Endogenous response variable.
    exog : array-like
        Exogenous design.

    Methods
    -------
    fit
        Call a models fit method
    predict
        Return fitted response values for a model.  If the model has

    Notes
    -----
    `endog` and `exog` are references to any data provided.  So if the data is
    already stored in numpy arrays and it is changed then `endog` and `exog`
    will change as well.
    """

    _results = None

    def __init__(self, endog, exog=None):
        endog = np.asarray(endog)
        endog = np.squeeze(endog) # for consistent outputs if endog is (n,1)

##        # not sure if we want type conversion, needs tests with integers
##        if np.issubdtype(endog.dtype, int):
##            endog = endog.astype(float)
##        if np.issubdtype(exog.dtype, int):
##            endog = exog.astype(float)
        if not exog is None:
            exog = np.asarray(exog)
            if exog.ndim == 1:
                exog = exog[:,None]
            if exog.ndim != 2:
                raise ValueError, "exog is not 1d or 2d"
            if endog.shape[0] != exog.shape[0]:
                raise ValueError, "endog and exog matrices are not aligned."
            if np.any(exog.var(0) == 0):
                # assumes one constant in first or last position
                const_idx = np.where(exog.var(0) == 0)[0].item()
                if const_idx == exog.shape[1] - 1:
                    exog_names = ['x%d' % i for i in range(1,exog.shape[1])]
                    exog_names += ['const']
                else:
                    exog_names = ['x%d' % i for i in range(exog.shape[1])]
                    exog_names[const_idx] = 'const'
                self.exog_names = exog_names
            else:
                self.exog_names = ['x%d' % i for i in range(exog.shape[1])]
        if endog.ndim == 1 or endog.shape[1] == 1:
            self.endog_names = ['y']
        else: # for VAR
            self.endog_names = ['y%d' % (i+1) for i in range(endog.shape[1])]
        self.endog = endog
        self.exog = exog
        self.nobs = float(self.endog.shape[0])

    def fit(self):
        """
        Fit a model to data.
        """
        raise NotImplementedError

    def predict(self, design):
        """
        After a model has been fit predict returns the fitted values.  If
        the model has not been fit, then fit is called.
        """
        raise NotImplementedError

class LikelihoodModel(Model):
    """
    Likelihood model is a subclass of Model.
    """

    def __init__(self, endog, exog=None):
        super(LikelihoodModel, self).__init__(endog, exog)
        self.initialize()

    def initialize(self):
        """
        Initialize (possibly re-initialize) a Model instance. For
        instance, the design matrix of a linear model may change
        and some things must be recomputed.
        """
        pass
#TODO: if the intent is to re-initialize the model with new data then
# this method needs to take inputs...

    def loglike(self, params):
        """
        Log-likelihood of model.
        """
        raise NotImplementedError

    def score(self, params):
        """
        Score vector of model.

        The gradient of logL with respect to each parameter.
        """
        raise NotImplementedError

    def information(self, params):
        """
        Fisher information matrix of model

        Returns -Hessian of loglike evaluated at params.
        """
        raise NotImplementedError

    def hessian(self, params):
        """
        The Hessian matrix of the model
        """
        raise NotImplementedError

    def fit(self, start_params=None, method='newton', maxiter=100, full_output=1,
            disp=1, fargs=(), callback=None, retall=0, **kwargs):
        """
        Fit method for likelihood based models

        Parameters
        ----------
        start_params : array-like, optional
            Initial guess of the solution for the loglikelihood maximization.
            The default is an array of zeros.
        method : str {'newton','nm','bfgs','powell','cg', or 'ncg'}
            Method can be 'newton' for Newton-Raphson, 'nm' for Nelder-Mead,
            'bfgs' for Broyden-Fletcher-Goldfarb-Shanno, 'powell' for modified
            Powell's method, 'cg' for conjugate gradient, or 'ncg' for Newton-
            conjugate gradient. `method` determines which solver from
            scipy.optimize is used.  The explicit arguments in `fit` are passed
            to the solver.  Each solver has several optional arguments that are
            not the same across solvers.  See the notes section below (or
            scipy.optimize) for the available arguments.
        maxiter : int
            The maximum number of iterations to perform.
        full_output : bool
            Set to True to have all available output in the Results object's
            mle_retvals attribute. The output is dependent on the solver.
            See LikelihoodModelResults notes section for more information.
        disp : bool
            Set to True to print convergence messages.
        fargs : tuple
            Extra arguments passed to the likelihood function, i.e.,
            loglike(x,*args)
        callback : callable callback(xk)
            Called after each iteration, as callback(xk), where xk is the
            current parameter vector.
        retall : bool
            Set to True to return list of solutions at each iteration.
            Available in Results object's mle_retvals attribute.

        Notes
        -----
        Optional arguments for the solvers (available in Results.mle_settings):

            'newton'
                tol : float
                    Relative error in params acceptable for convergence.
            'nm' -- Nelder Mead
                xtol : float
                    Relative error in params acceptable for convergence
                ftol : float
                    Relative error in loglike(params) acceptable for
                    convergence
                maxfun : int
                    Maximum number of function evaluations to make.
            'bfgs'
                gtol : float
                    Stop when norm of gradient is less than gtol.
                norm : float
                    Order of norm (np.Inf is max, -np.Inf is min)
                epsilon
                    If fprime is approximated, use this value for the step
                    size. Only relevant if LikelihoodModel.score is None.
            'cg'
                gtol : float
                    Stop when norm of gradient is less than gtol.
                norm : float
                    Order of norm (np.Inf is max, -np.Inf is min)
                epsilon : float
                    If fprime is approximated, use this value for the step
                    size. Can be scalar or vector.  Only relevant if
                    Likelihoodmodel.score is None.
            'ncg'
                fhess_p : callable f'(x,*args)
                    Function which computes the Hessian of f times an arbitrary
                    vector, p.  Should only be supplied if
                    LikelihoodModel.hessian is None.
                avextol : float
                    Stop when the average relative error in the minimizer
                    falls below this amount.
                epsilon : float or ndarray
                    If fhess is approximated, use this value for the step size.
                    Only relevant if Likelihoodmodel.hessian is None.
            'powell'
                xtol : float
                    Line-search error tolerance
                ftol : float
                    Relative error in loglike(params) for acceptable for
                    convergence.
                maxfun : int
                    Maximum number of function evaluations to make.
                start_direc : ndarray
                    Initial direction set.
                """
        methods = ['newton', 'nm', 'bfgs', 'powell', 'cg', 'ncg']
        if start_params is None:
            if self.exog is not None:
                start_params = [0]*self.exog.shape[1] # fails for shape (K,)?
            else:
                raise ValueError("If exog is None, then start_params should be \
specified")

        if method.lower() not in methods:
            raise ValueError, "Unknown fit method %s" % method
        method = method.lower()
#TODO: separate args from nonarg taking score and hessian, ie.,
# user-supplied and numerically evaluated
# estimate frprime doesn't take args in most (any?) of the optimize function
        f = lambda params, *args: -self.loglike(params, *args)
        score = lambda params: -self.score(params)
        try:
            hess = lambda params: -self.hessian(params)
        except:
            hess = None
        if method == 'newton':
            tol = kwargs.setdefault('tol', 1e-8)
            score = lambda params: self.score(params)
            hess = lambda params: self.hessian(params)
            iterations = 0
            oldparams = np.inf
            newparams = np.asarray(start_params)
            if retall:
                history = [oldparams, newparams]
            while (iterations < maxiter and np.all(np.abs(newparams -
                    oldparams) > tol)):
                H = hess(newparams)
                oldparams = newparams
                newparams = oldparams - np.dot(np.linalg.inv(H),
                        score(oldparams))
                if retall:
                    history.append(newparams)
                if callback is not None:
                    callback(newparams)
                iterations += 1
            fval = f(newparams, *fargs) # this is the negative likelihood
            if iterations == maxiter:
                warnflag = 1
                if disp:
                    print "Warning: Maximum number of iterations has been \
exceeded."
                    print "         Current function value: %f" % fval
                    print "         Iterations: %d" % iterations
            else:
                warnflag = 0
                if disp:
                    print "Optimization terminated successfully."
                    print "         Current function value: %f" % fval
                    print "         Iterations %d" % iterations
            if full_output:
                xopt, fopt, niter, gopt, hopt = (newparams, f(newparams, *fargs),
                    iterations, score(newparams), hess(newparams))
                converged = not warnflag
                retvals = {'fopt' : fopt, 'iterations' : niter, 'score' : gopt,
                        'Hessian' : hopt, 'warnflag' : warnflag,
                        'converged' : converged}
                if retall:
                    retvals.update({'allvecs' : history})
            else:
                retvals = newparams
        elif method == 'nm':    # Nelder-Mead
            xtol = kwargs.setdefault('xtol', 0.0001)
            ftol = kwargs.setdefault('ftol', 0.0001)
            maxfun = kwargs.setdefault('maxfun', None)
            retvals = optimize.fmin(f, start_params, args=fargs, xtol=xtol,
                        ftol=ftol, maxiter=maxiter, maxfun=maxfun,
                        full_output=full_output, disp=disp, retall=retall,
                        callback=callback)
            if full_output:
                if not retall:
                    xopt, fopt, niter, fcalls, warnflag = retvals
                else:
                    xopt, fopt, niter, fcalls, warnflag, allvecs = retvals
                converged = not warnflag
                retvals = {'fopt' : fopt, 'iterations' : niter,
                    'fcalls' : fcalls, 'warnflag' : warnflag,
                    'converged' : converged}
                if retall:
                    retvals.update({'allvecs' : allvecs})
        elif method == 'bfgs':
            gtol = kwargs.setdefault('gtol', 1.0000000000000001e-05)
            norm = kwargs.setdefault('norm', np.Inf)
            epsilon = kwargs.setdefault('epsilon', 1.4901161193847656e-08)
            retvals = optimize.fmin_bfgs(f, start_params, score, args=fargs,
                            gtol=gtol, norm=norm, epsilon=epsilon,
                            maxiter=maxiter, full_output=full_output,
                            disp=disp, retall=retall, callback=callback)
            if full_output:
                if not retall:
                    xopt, fopt, gopt, Hinv, fcalls, gcalls, warnflag = retvals
                else:
                    xopt, fopt, gopt, Hinv, fcalls, gcalls, warnflag, allvecs =\
                        retvals
                converged = not warnflag
                retvals = {'fopt' : fopt, 'gopt' : gopt, 'Hinv' : Hinv,
                        'fcalls' : fcalls, 'gcalls' : gcalls, 'warnflag' :
                        warnflag, 'converged' : converged}
                if retall:
                    retvals.update({'allvecs' : allvecs})
        elif method == 'ncg':
            fhess_p = kwargs.setdefault('fhess_p', None)
            avextol = kwargs.setdefault('avextol', 1.0000000000000001e-05)
            epsilon = kwargs.setdefault('epsilon', 1.4901161193847656e-08)
            retvals = optimize.fmin_ncg(f, start_params, score, fhess_p=fhess_p,
                            fhess=hess, args=fargs, avextol=avextol,
                            epsilon=epsilon, maxiter=maxiter,
                            full_output=full_output, disp=disp, retall=retall,
                            callback=callback)
            if full_output:
                if not retall:
                    xopt, fopt, fcalls, gcalls, hcalls, warnflag = retvals
                else:
                    xopt, fopt, fcalls, gcalls, hcalls, warnflag, allvecs =\
                        retvals
                converged = not warnflag
                retvals = {'fopt' : fopt, 'fcalls' : fcalls, 'gcalls' : gcalls,
                    'hcalls' : hcalls, 'warnflag' : warnflag,
                    'converged' : converged}
                if retall:
                    retvals.update({'allvecs' : allvecs})
        elif method == 'cg':
            gtol = kwargs.setdefault('gtol', 1.0000000000000001e-05)
            norm = kwargs.setdefault('norm', np.Inf)
            epsilon = kwargs.setdefault('epsilon', 1.4901161193847656e-08)
            retvals = optimize.fmin_cg(f, start_params, score,
                            gtol=gtol, norm=norm,
                            epsilon=epsilon, maxiter=maxiter,
                            full_output=full_output, disp=disp, retall=retall,
                            callback=callback)
            if full_output:
                if not retall:
                    xopt, fopt, fcalls, gcalls, warnflag = retvals
                else:
                    xopt, fopt, fcalls, gcalls, warnflag, allvecs = retvals
                converged = not warnflag
                retvals = {'fopt' : fopt, 'fcalls' : fcalls, 'gcalls' : gcalls,
                    'warnflag' : warnflag, 'converged' : converged}
                if retall:
                    retvals.update({'allvecs' : allvecs})
        elif method == 'powell':
            xtol = kwargs.setdefault('xtol', 0.0001)
            ftol = kwargs.setdefault('ftol', 0.0001)
            maxfun = kwargs.setdefault('maxfun', None)
            start_direc = kwargs.setdefault('start_direc', None)
            retvals = optimize.fmin_powell(f, start_params, args=fargs,
                            xtol=xtol, ftol=ftol, maxiter=maxiter,
                            maxfun=maxfun, full_output=full_output, disp=disp,
                            retall=retall, callback=callback, direc=start_direc)
            if full_output:
                if not retall:
                    xopt, fopt, direc, niter, fcalls, warnflag = retvals
                else:
                    xopt, fopt, direc, niter, fcalls, warnflag, allvecs =\
                        retvals
                converged = not warnflag
                retvals = {'fopt' : fopt, 'direc' : direc, 'iterations' : niter,
                    'fcalls' : fcalls, 'warnflag' : warnflag, 'converged' :
                    converged}
                if retall:
                    retvals.update({'allvecs' : allvecs})
        if not full_output:
            xopt = retvals

#NOTE: better just to use the Analytic Hessian here, as approximation isn't
# great
#        if method == 'bfgs' and full_output:
#            Hinv = retvals.setdefault('Hinv', 0)
        elif method == 'newton' and full_output:
            Hinv = np.linalg.inv(-hopt)
        else:
            try:
                Hinv = np.linalg.inv(-1*self.hessian(xopt))
            except:
                Hinv = None
#TODO: add Hessian approximation and change the above if needed
        mlefit = LikelihoodModelResults(self, xopt, Hinv, scale=1.)
#TODO: hardcode scale?

        if isinstance(retvals, dict):
            mlefit.mle_retvals = retvals
        optim_settings = {'optimizer' : method, 'start_params' : start_params,
            'maxiter' : maxiter, 'full_output' : full_output, 'disp' : disp,
            'fargs' : fargs, 'callback' : callback, 'retall' : retall}
        optim_settings.update(kwargs)
        mlefit.mle_settings = optim_settings
        self._results = mlefit
        return mlefit

#TODO: the below is unfinished
class GenericLikelihoodModel(LikelihoodModel):
    """
    Allows the fitting of any likelihood function via maximum likelihood.

    Notes
    -----
    Methods that require only a likelihood function.
        'nm'
        'powell'

    Methods that require a likelihood function and a score/gradient.
        'bfgs'
        'cg'
        'ncg' - A function to compute the Hessian is optional.

    Methods that require a likelihood function, a score/gradient, and a
    Hessian.
        'newton'


    Example

    import scikits.statsmodels as sm
    data = sm.datasets.spector.load()
    data.exog = sm.add_constant(data.exog)
# in this dir
    from model import GenericLikelihoodModel
    probit_mod = sm.Probit(data.endog, data.exog)
    probit_res = probit_mod.fit()
    loglike = probit_mod.loglike
    score = probit_mod.score
    mod = GenericLikelihoodModel(data.endog, data.exog, loglike, score)
    res = mod.fit(method="nm", maxiter = 500)
    import numpy as np
    np.allclose(res.params, probit_res.params)
    """
    def __init__(self, endog, exog=None, loglike=None, score=None, hessian=None):
    # let them be none in case user wants to use inheritance
        if loglike:
            self.loglike = loglike
        if score:
            self.score = score
        if hessian:
            self.hessian = hessian
        super(GenericLikelihoodModel, self).__init__(endog, exog)

    def initialize(self):
        if not self.score:  # right now score is not optional
            from sandbox.regression.numdiff import approx_fprime1
            self.score = approx_fprime1
            if not self.hessian:
                pass
        else:   # can use approx_hess_p if we have a gradient
            if not self.hessian:
                pass

class Results(object):
    """
    Class to contain model results
    """
    def __init__(self, model, params, **kwd):
        """
        Parameters
        ----------
        model : class instance
            the previously specified model instance
        params : array
            parameter estimates from the fit model
        """
        self.__dict__.update(kwd)
        self.initialize(model, params, **kwd)

    def initialize(self, model, params, **kwd):
        self.params = params
        self.model = model
#TODO: public method?

class LikelihoodModelResults(Results):
    def __init__(self, model, params, normalized_cov_params=None, scale=1.):
        """
        Class to contain results from likelihood models

        Parameters
        -----------
        model : LikelihoodModel instance or subclass instance
            LikelihoodModelResults holds a reference to the model that is fit.
        params : 1d array_like
            parameter estimates from estimated model
        normalized_cov_params : 2d array
           Normalized (before scaling) covariance of params. (dot(X.T,X))**-1
        scale : float
            For (some subset of models) scale will typically be the
            mean square error from the estimated model (sigma^2)

        Returns
        -------
        **Attributes**
        mle_retvals : dict
            Contains the values returned from the chosen optimization method if
            full_output is True during the fit.  Available only if the model
            is fit by maximum likelihood.  See notes below for the output from
            the different methods.
        mle_settings : dict
            Contains the arguments passed to the chosen optimization method.
            Available if the model is fit by maximum likelihood.  See
            LikelihoodModel.fit for more information.
        model : model instance
            LikelihoodResults contains a reference to the model that is fit.
        params : ndarray
            The parameters estimated for the model.
        scale : float
            The scaling factor of the model given during instantiation.


        Notes
        --------
        The covariance of params is given by scale times normalized_cov_params.

        Return values by solver if full_ouput is True during fit:

            'newton'
                fopt : float
                    The value of the (negative) loglikelihood at its
                    minimum.
                iterations : int
                    Number of iterations performed.
                score : ndarray
                    The score vector at the optimum.
                Hessian : ndarray
                    The Hessian at the optimum.
                warnflag : int
                    1 if maxiter is exceeded. 0 if successful convergence.
                converged : bool
                    True: converged. False: did not converge.
                allvecs : list
                    List of solutions at each iteration.
            'nm'
                fopt : float
                    The value of the (negative) loglikelihood at its
                    minimum.
                iterations : int
                    Number of iterations performed.
                warnflag : int
                    1: Maximum number of function evaluations made.
                    2: Maximum number of iterations reached.
                converged : bool
                    True: converged. False: did not converge.
                allvecs : list
                    List of solutions at each iteration.
            'bfgs'
                fopt : float
                    Value of the (negative) loglikelihood at its minimum.
                gopt : float
                    Value of gradient at minimum, which should be near 0.
                Hinv : ndarray
                    value of the inverse Hessian matrix at minimum.  Note
                    that this is just an approximation and will often be
                    different from the value of the analytic Hessian.
                fcalls : int
                    Number of calls to loglike.
                gcalls : int
                    Number of calls to gradient/score.
                warnflag : int
                    1: Maximum number of iterations exceeded. 2: Gradient
                    and/or function calls are not changing.
                converged : bool
                    True: converged.  False: did not converge.
                allvecs : list
                    Results at each iteration.
            'powell'
                fopt : float
                    Value of the (negative) loglikelihood at its minimum.
                direc : ndarray
                    Current direction set.
                iterations : int
                    Number of iterations performed.
                fcalls : int
                    Number of calls to loglike.
                warnflag : int
                    1: Maximum number of function evaluations. 2: Maximum number
                    of iterations.
                converged : bool
                    True : converged. False: did not converge.
                allvecs : list
                    Results at each iteration.
            'cg'
                fopt : float
                    Value of the (negative) loglikelihood at its minimum.
                fcalls : int
                    Number of calls to loglike.
                gcalls : int
                    Number of calls to gradient/score.
                warnflag : int
                    1: Maximum number of iterations exceeded. 2: Gradient and/
                    or function calls not changing.
                converged : bool
                    True: converged. False: did not converge.
                allvecs : list
                    Results at each iteration.
            'ncg'
                fopt : float
                    Value of the (negative) loglikelihood at its minimum.
                fcalls : int
                    Number of calls to loglike.
                gcalls : int
                    Number of calls to gradient/score.
                hcalls : int
                    Number of calls to hessian.
                warnflag : int
                    1: Maximum number of iterations exceeded.
                converged : bool
                    True: converged. False: did not converge.
                allvecs : list
                    Results at each iteration.
        """
        super(LikelihoodModelResults, self).__init__(model, params)
        self.normalized_cov_params = normalized_cov_params
        self.scale = scale

    def normalized_cov_params(self):
        raise NotImplementedError

    def t(self, column=None):
        """
        Return the t-statistic for a given parameter estimate.

        Parameters
        ----------
        column : array-like
            The columns for which you would like the t-value.
            Note that this uses Python's indexing conventions.

        See also
        ---------
        Use t_test for more complicated t-statistics.

        Examples
        --------
        >>> import scikits.statsmodels as sm
        >>> data = sm.datasets.longley.load()
        >>> data.exog = sm.add_constant(data.exog)
        >>> results = sm.OLS(data.endog, data.exog).fit()
        >>> results.t()
        array([ 0.17737603, -1.06951632, -4.13642736, -4.82198531, -0.22605114,
        4.01588981, -3.91080292])
        >>> results.t([1,2,4])
        array([-1.06951632, -4.13642736, -0.22605114])
        >>> import numpy as np
        >>> results.t(np.array([1,2,4]))
        array([-1.06951632, -4.13642736, -0.22605114])

        """

        if self.normalized_cov_params is None:
            raise ValueError, 'need covariance of parameters for computing T\
 statistics'

        if column is None:
            column = range(self.params.shape[0])

        column = np.asarray(column)
        _params = self.params[column]
        _cov = self.cov_params(column=column)
        if _cov.ndim == 2:
            _cov = np.diag(_cov)
#        _t = _params * recipr(np.sqrt(_cov))
# repicr drops precision for MNLogit?
        _t = _params / np.sqrt(_cov)
        return _t


    def cov_params(self, r_matrix=None, column=None, scale=None, other=None):
        """
        Returns the variance/covariance matrix.

        The variance/covariance matrix can be of a linear contrast
        of the estimates of params or all params multiplied by scale which
        will usually be an estimate of sigma^2.  Scale is assumed to be
        a scalar.

        Parameters
        -----------
        r_matrix : array-like
            Can be 1d, or 2d.  Can be used alone or with other.
        column :  array-like, optional
            Must be used on its own.  Can be 0d or 1d see below.
        scale : float, optional
            Can be specified or not.  Default is None, which means that
            the scale argument is taken from the model.
        other : array-like, optional
            Can be used when r_matrix is specified.

        Returns
        -------
        (The below are assumed to be in matrix notation.)

        cov : ndarray

        If no argument is specified returns the covariance matrix of a model
        (scale)*(X.T X)^(-1)

        If contrast is specified it pre and post-multiplies as follows
        (scale) * r_matrix (X.T X)^(-1) r_matrix.T

        If contrast and other are specified returns
        (scale) * r_matrix (X.T X)^(-1) other.T

        If column is specified returns
        (scale) * (X.T X)^(-1)[column,column] if column is 0d

        OR

        (scale) * (X.T X)^(-1)[column][:,column] if column is 1d

        """
        if self.normalized_cov_params is None:
            raise ValueError, 'need covariance of parameters for computing \
(unnormalized) covariances'
        if column is not None and (r_matrix is not None or other is not None):
            raise ValueError, 'Column should be specified without other \
arguments.'
        if other is not None and r_matrix is None:
            raise ValueError, 'other can only be specified with r_matrix'
        if scale is None:
            scale = self.scale
        if column is not None:
            column = np.asarray(column)
            if column.shape == ():
                return self.normalized_cov_params[column, column] * scale
            else:
                return self.normalized_cov_params[column][:,column] * scale
        elif r_matrix is not None:
            r_matrix = np.asarray(r_matrix)
            if r_matrix.shape == ():
                raise ValueError, "r_matrix should be 1d or 2d"
            if other is None:
                other = r_matrix
            else:
                other = np.asarray(other)
            tmp = np.dot(r_matrix, np.dot(self.normalized_cov_params,
                np.transpose(other)))
            return tmp * scale
        if r_matrix is None and column is None:
            return self.normalized_cov_params * scale

#TODO: make sure this works as needed for GLMs
    def t_test(self, r_matrix, scale=None):
        """
        Compute a tcontrast/t-test for a row vector array.

        Parameters
        ----------
        r_matrix : array-like
            A length p row vector specifying the linear restrictions.
        scale : float, optional
            An optional `scale` to use.  Default is the scale specified
            by the model fit.

        scale : scalar

        Examples
        --------
        >>> import numpy as np
        >>> import scikits.statsmodels as sm
        >>> data = sm.datasets.longley.load()
        >>> data.exog = sm.add_constant(data.exog)
        >>> results = sm.OLS(data.endog, data.exog).fit()
        >>> r = np.zeros_like(results.params)
        >>> r[4:6] = [1,-1]
        >>> print r
        [ 0.  0.  0.  0.  1. -1.  0.]

        r tests that the coefficients on the 5th and 6th independent
        variable are the same.

        >>>T_Test = results.t_test(r)
        >>>print T_test
        <T contrast: effect=-1829.2025687192481, sd=455.39079425193762, t=-4.0167754636411717, p=0.0015163772380899498, df_denom=9>
        >>> T_test.effect
        -1829.2025687192481
        >>> T_test.sd
        455.39079425193762
        >>> T_test.t
        -4.0167754636411717
        >>> T_test.p
        0.0015163772380899498

        See also
        ---------
        t : method to get simpler t values
        f_test : for f tests

        """
        r_matrix = np.squeeze(np.asarray(r_matrix))

        if self.normalized_cov_params is None:
            raise ValueError, 'Need covariance of parameters for computing \
T statistics'
        if r_matrix.ndim == 1:
            if r_matrix.shape[0] != self.params.shape[0]:
                raise ValueError, 'r_matrix and params are not aligned'
        elif r_matrix.ndim >1:
            if r_matrix.shape[1] != self.params.shape[0]:
                raise ValueError, 'r_matrix and params are not aligned'

        _t = _sd = None

        _effect = np.dot(r_matrix, self.params)
        _sd = np.sqrt(self.cov_params(r_matrix=r_matrix))
        if _sd.ndim > 1:
            _sd = np.diag(_sd)
        _t = _effect * recipr(_sd)
        return ContrastResults(effect=_effect, t=_t, sd=_sd,
                df_denom=self.model.df_resid)

#TODO: untested for GLMs?
    def f_test(self, r_matrix, q_matrix=None, scale=1.0, invcov=None):
        """
        Compute an Fcontrast/F-test for a contrast matrix.

        Here, matrix `r_matrix` is assumed to be non-singular. More precisely,

        r_matrix (pX pX.T) r_matrix.T

        is assumed invertible. Here, pX is the generalized inverse of the
        design matrix of the model. There can be problems in non-OLS models
        where the rank of the covariance of the noise is not full.

        Parameters
        -----------
        r_matrix : array-like
            q x p array where q is the number of restrictions to test and
            p is the number of regressors in the full model fit.
            If q is 1 then f_test(r_matrix).fvalue is equivalent to
            the square of t_test(r_matrix).t
        q_matrix : array-like
            q x 1 array, that represents the sum of each linear restriction.
            Default is all zeros for each restriction.
        scale : float, optional
            Default is 1.0 for no scaling.
        invcov : array-like, optional
            A qxq matrix to specify an inverse covariance
            matrix based on a restrictions matrix.

        Examples
        --------
        >>> import numpy as np
        >>> import scikits.statsmodels as sm
        >>> data = sm.datasets.longley.load()
        >>> data.exog = sm.add_constant(data.exog)
        >>> results = sm.OLS(data.endog, data.exog).fit()
        >>> A = np.identity(len(results.params))
        >>> A = A[:-1,:]

        This tests that each coefficient is jointly statistically
        significantly different from zero.

        >>> print results.f_test(A)
        <F contrast: F=330.28533923463488, p=4.98403052872e-10, df_denom=9, df_num=6>

        Compare this to

        >>> results.F
        330.2853392346658
        >>> results.F_p
        4.98403096572e-10

        >>> B = np.array(([0,1,-1,0,0,0,0],[0,0,0,0,1,-1,0]))

        This tests that the coefficient on the 2nd and 3rd regressors are
        equal and jointly that the coefficient on the 5th and 6th regressors
        are equal.

        >>> print results.f_test(B)
        <F contrast: F=9.740461873303655, p=0.00560528853174, df_denom=9, df_num=2>

        See also
        --------
        scikits.statsmodels.contrasts
        scikits.statsmodels.model.t_test

        """
        r_matrix = np.asarray(r_matrix)
        r_matrix = np.atleast_2d(r_matrix)

        if self.normalized_cov_params is None:
            raise ValueError, 'need covariance of parameters for computing F statistics'

        cparams = np.dot(r_matrix, self.params[:,None])
        J = float(r_matrix.shape[0]) # number of restrictions
        if q_matrix is None:
            q_matrix = np.zeros(J)
        else:
            q_matrix = np.asarray(q_matrix)
        if q_matrix.ndim == 1:
            q_matrix = q_matrix[:,None]
            if q_matrix.shape[0] != J:
                raise ValueError("r_matrix and q_matrix must have the same \
number of rows")
        Rbq = cparams - q_matrix
        if invcov is None:
            invcov = np.linalg.inv(self.cov_params(r_matrix=r_matrix))
        F = np.dot(np.dot(Rbq.T,invcov),Rbq)/J
        return ContrastResults(F=F, df_denom=self.model.df_resid,
                    df_num=invcov.shape[0])

    def conf_int(self, alpha=.05, cols=None):
        """
        Returns the confidence interval of the fitted parameters.

        Parameters
        ----------
        alpha : float, optional
            The `alpha` level for the confidence interval.
            ie., The default `alpha` = .05 returns a 95% confidence interval.
        cols : array-like, optional
            `cols` specifies which confidence intervals to return

        Returns
        --------
        conf_int : array
            Each row contains [lower, upper] confidence interval

        Examples
        --------
        >>> import scikits.statsmodels as sm
        >>> data = sm.datasets.longley.load()
        >>> data.exog = sm.add_constant(data.exog)
        >>> results = sm.OLS(data.endog, data.exog).fit()
        >>> results.conf_int()
        array([[ -1.77029035e+02,   2.07152780e+02],
        [ -1.11581102e-01,   3.99427438e-02],
        [ -3.12506664e+00,  -9.15392966e-01],
        [ -1.51794870e+00,  -5.48505034e-01],
        [ -5.62517214e-01,   4.60309003e-01],
        [  7.98787515e+02,   2.85951541e+03],
        [ -5.49652948e+06,  -1.46798779e+06]])

        >>> results.conf_int(cols=(1,2))
        array([[-0.1115811 ,  0.03994274],
        [-3.12506664, -0.91539297]])

        Notes
        -----
        The confidence interval is based on Student's t distribution for all
        models except RLM and GLM, which uses the standard normal distribution.

        """
        #TODO: simplify structure, DRY
        if self.__class__.__name__ in ['RLMResults','GLMResults','DiscreteResults']:
            dist = norm
        else:
            dist = t
        if cols is None and dist == t:
            lower = self.params - dist.ppf(1-alpha/2,self.model.df_resid) *\
                    self.bse
            upper = self.params + dist.ppf(1-alpha/2,self.model.df_resid) *\
                    self.bse
        elif cols is None and dist == norm:
            lower = self.params - dist.ppf(1-alpha/2)*self.bse
            upper = self.params + dist.ppf(1-alpha/2)*self.bse
        elif cols is not None and dist == t:
            cols = np.asarray(cols)
            lower = self.params[cols] - dist.ppf(1-\
                        alpha/2,self.model.df_resid) *self.bse[cols]
            upper = self.params[cols] + dist.ppf(1-\
                        alpha/2,self.model.df_resid) *self.bse[cols]
        elif cols is not None and dist == norm:
            cols = np.asarray(cols)
            lower = self.params[cols] - dist.ppf(1-alpha/2)*self.bse[cols]
            upper = self.params[cols] + dist.ppf(1-alpha/2)*self.bse[cols]
        return np.asarray(zip(lower,upper))




