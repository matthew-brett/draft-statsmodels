import numpy as np
import numpy.testing as npt
from scipy import signal
from models.tools import add_constant
from models.regression import AR, yule_walker

examples_all = range(10) + ['test_copy']

examples = examples_all #[5]

if 0 in examples:
    X = np.arange(1,8)
    X = add_constant(X)
    Y = np.array((1, 3, 4, 5, 8, 10, 9))
    rho = 2
    model = AR(Y, X, 2)
    for i in range(6):
        results = model.fit()
        print "AR coefficients:", model.rho
        rho, sigma = yule_walker(results.resid, order = model.order)
        model = AR(Y, X, rho)
    par0 = results.params
    print par0
    model0if = AR(Y, X, 2)
    res = model0if.iterative_fit(6)
    print 'iterativefit beta', res.params
    results.t() # is this correct? it does equal params/bse
    # but isn't the same as the AR example (which was wrong in the first place..)
    print results.Tcontrast([0,1])  # are sd and t correct? vs
    print results.Fcontrast(np.eye(2))


rhotrue = [0.5, 0.2]
rhotrue = np.asarray(rhotrue)
nlags = np.size(rhotrue)
beta = np.array([0.1, 2])
noiseratio = 0.01
nsample = 2000
x = np.arange(nsample)
X1 = add_constant(x)

wnoise = noiseratio * np.random.randn(nsample+nlags)
#noise = noise[1:] + rhotrue*noise[:-1] # wrong this is not AR





#find my drafts for univariate ARMA functions
# generate AR(p)
if np.size(rhotrue) == 1:
    # replace with scipy.signal.lfilter ?
    arnoise = np.zeros(nsample+1)
    for i in range(1,nsample+1):
        arnoise[i] = rhotrue*arnoise[i-1] + wnoise[i]
    noise = arnoise[1:]
    an = signal.lfilter([1], np.hstack((1,-rhotrue)), wnoise[1:])
    print 'simulate AR(1) difference', np.max(np.abs(noise-an))
else:
    noise = signal.lfilter([1], np.hstack((1,-rhotrue)), wnoise)[nlags:]

# generate GLS model with AR noise
y1 = np.dot(X1,beta) + noise

if 1 in examples:
    mod1 = AR(y1, X1, 1)
    print mod1.results.params
    print mod1.rho

    for i in range(10):
        mod1.iterative_fit(1)
        print mod1.rho
        print mod1.results.params

if 2 in examples:
    print '\n iterative fitting of first model'
    print 'with AR(0)', par0
    parold = par0
    mod0 = AR(Y, X, 1)
    for i in range(10):
        print mod0.wdesign.sum()
        print mod0.calc_params.sum()
        mod0.iterative_fit(1)
        print mod0.rho
        parnew = mod0.results.params
        print parnew
        print parnew - parold
        parold = parnew

# generate pure AR(p) process
Y = noise

#example with no regressor,
#results now have same estimated rho as yule-walker directly

if 3 in examples:
    model3 = AR(Y, rho=2)
    for i in range(10):
        results = model3.fit()
        print "AR coefficients:", model3.rho, results.params
        rho, sigma = yule_walker(results.resid, order = model3.order)
        model3 = AR(Y, rho=rho)

if 'test_copy' in examples:
    xx = X.copy()
    rhoyw, sigmayw = yule_walker(xx[:,0], order = 2)
    print rhoyw, sigmayw
    print (xx == X).all()  # test for unchanged array (fixed)

    yy = Y.copy()
    rhoyw, sigmayw = yule_walker(yy, order = 2)
    print rhoyw, sigmayw
    print (yy == Y).all()  # test for unchanged array (fixed)


if 4 in examples:
    Ydemeaned = Y - Y.mean()
    model4 = AR(Ydemeaned, rho=2)
    for i in range(10):
        results = model4.fit()
        print "AR coefficients:", model3.rho, results.params
        rho, sigma = yule_walker(results.resid, order = model4.order)
        model4 = AR(Ydemeaned, rho=rho)

if 5 in examples:
    model3a = AR(Y, rho=1)
    res3a = model3a.iterative_fit(5)
    print res3a.params
    print model3a.rho
    rhoyw, sigmayw = yule_walker(Y, order = 1)
    print rhoyw, sigmayw
    npt.assert_array_almost_equal(model3a.rho, rhoyw, 15)
