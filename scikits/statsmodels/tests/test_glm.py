"""

Test functions for models.GLM
"""

#TODO: use decorators to dynamical call test methods?
#TODO: move decimal_precision attributes to the classes here

#from __future__ import absolute_import
import numpy as np
from numpy.testing import *
import scikits.statsmodels as sm
from scikits.statsmodels.glm import GLM
from scikits.statsmodels.tools import add_constant
from nose import SkipTest
from check_for_rpy import skip_rpy

# Test Precisions
DECIMAL_4 = 4
DECIMAL_3 = 3
DECIMAL_2 = 2
DECIMAL_1 = 1
DECIMAL_0 = 0
#skipR = skip_rpy()
#if not skipR:
#    from rpy import r
#    from rmodelwrap import RModel

class CheckModelResults(object):
    '''
    res2 should be either the results from RModelWrap
    or the results as defined in model_results_data
    '''
    decimal_params = DECIMAL_4
    def test_params(self):
#        self.check_params(self.res1.params, self.res2.params)
        assert_almost_equal(self.res1.params, self.res2.params,
                self.decimal_params)

    decimal_bse = DECIMAL_4
    def test_standard_errors(self):
        assert_almost_equal(self.res1.bse, self.res2.bse, self.decimal_bse)

    decimal_resids = DECIMAL_4
    def test_residuals(self):
#TODO: remove RPY stuff?
#        if 'rmodelwrap' in self.res2.__module__ and not hasattr(self.res2,
#               'resids'):
#            assert_almost_equal(self.res1.resid_deviance,
#                self.res2.resid_deviance, DECIMAL_4)
#        else:
        resids = np.column_stack((self.res1.resid_pearson,
                self.res1.resid_deviance, self.res1.resid_working,
                self.res1.resid_anscombe, self.res1.resid_response))
#            self.check_resids(resids, self.res2.resids)
        assert_almost_equal(resids, self.res2.resids, self.decimal_resids)

    decimal_aic_R = DECIMAL_4
    def test_aic_R(self):
        # R includes the estimation of the scale as a lost dof
        # Doesn't with Gamma though
    #TODO:fix this?
        if self.res1.scale != 1:
            dof = 2
        else: dof = 0
#        self.check_aic_R(self.res1.aic+dof, self.res2.aic_R,
#                self.decimal_aic_R)
        assert_almost_equal(self.res1.aic+dof, self.res2.aic_R)

    decimal_aic_Stata = DECIMAL_4
    def test_aic_Stata(self):
#TODO: remove RPY stuff
        if 'rmodelwrap' in self.res2.__module__:
            raise SkipTest("Results are from RModel wrapper")
        aic = self.res1.aic/self.res1.nobs
#        self.check_aic_Stata(aic, self.res2.aic_Stata)
        assert_almost_equal(aic, self.res2.aic_Stata, self.decimal_aic_Stata)

    decimal_deviance = DECIMAL_4
    def test_deviance(self):
        assert_almost_equal(self.res1.deviance, self.res2.deviance,
                self.decimal_deviance)

    decimal_scale = DECIMAL_4
    def test_scale(self):
        assert_almost_equal(self.res1.scale, self.res2.scale,
                self.decimal_scale)

    decimal_loglike = DECIMAL_4
    def test_loglike(self):
#        self.check_loglike(self.res1.llf, self.res2.llf,
#                self.decimal_loglike)
        assert_almost_equal(self.res1.llf, self.res2.llf, self.decimal_loglike)

    decimal_null_deviance = DECIMAL_4
    def test_null_deviance(self):
        assert_almost_equal(self.res1.null_deviance, self.res2.null_deviance,
                    self.decimal_null_deviance)

    decimal_bic = DECIMAL_4
    def test_bic(self):
        #TODO: remove RPY stuff
#        if 'rmodelwrap' in self.res2.__module__ and not hasattr(self.res2,
#                'bic'):
#            raise SkipTest("Results are from RModel wrapper")
#        self.check_bic(self.res1.bic,
#            self.res2.bic_Stata)
        assert_almost_equal(self.res1.bic, self.res2.bic_Stata,
                self.decimal_bic)

    def test_degrees(self):
#        if not 'rmodelwrap' in self.res2.__module__:
#            assert_almost_equal(self.res1.model.df_model,self.res2.df_model,
#                    DECIMAL_4)
        assert_equal(self.res1.model.df_resid,self.res2.df_resid)

#TODO: how is this different than deviance?
#    def test_pearson_chi2(self):
#        if 'rmodelwrap' in self.res2.__module__:
#            raise SkipTest("Results are from RModel wrapper")
#        self.check_pearson_chi2(self.res1.pearson_chi2, self.res2.pearson_chi2)

    decimal_fittedvalues = DECIMAL_4
    def test_fittedvalues(self):
#        if not 'rmodelwrap' in self.res2.__module__:
#            raise SkipTest("Results do not have fitted values")
        assert_almost_equal(self.res1.fittedvalues, self.res2.fittedvalues,
                self.decimal_fittedvalues)

class TestGlmGaussian(CheckModelResults):
    def __init__(self):
        '''
        Test Gaussian family with canonical identity link
        '''
        # Test Precisions
        self.decimal_resids = DECIMAL_3
        self.decimal_params = DECIMAL_3
        self.decimal_bic_Stata = DECIMAL_1

        from scikits.statsmodels.datasets.longley import Load
        self.data = Load()
        self.data.exog = add_constant(self.data.exog)
        self.res1 = GLM(self.data.endog, self.data.exog,
                        family=sm.families.Gaussian()).fit()
        from results.results_glm import Longley
        self.res2 = Longley()

#    def setup(self):
#        if skipR:
#            raise SkipTest, "Rpy not installed."
#        Gauss = r.gaussian
#        self.res2 = RModel(self.data.endog, self.data.exog, r.glm, family=Gauss)
#        self.res2.resids = np.array(self.res2.resid)[:,None]*np.ones((1,5))
#        self.res2.null_deviance = 185008826 # taken from R. Rpy bug?

#    def check_params(self, params1, params2):
#        assert_almost_equal(params1, params2, DECIMAL_4)

#    def check_resids(self, resids1, resids2):
#        assert_almost_equal(resids1, resids2, DECIMAL_4)

#    def check_aic_R(self, aic1, aic2):
#        assert_almost_equal(aic1, aic2, DECIMAL_4)

#    def check_aic_Stata(self, aic1, aic2):
#        assert_almost_equal(aic1, aic2, DECIMAL_4)

#    def check_loglike(self, llf1, llf2):
#        assert_almost_equal(llf1, llf2, DECIMAL_4)

#    def check_bic(self, bic1, bic2):
#        assert_almost_equal(bic1, bic2, DECIMAL_4)

#    def check_pearson_chi2(self, pearson_chi21, pearson_chi22):
#        assert_almost_equal(pearson_chi21, pearson_chi22, DECIMAL_4)

class TestGaussianLog(CheckModelResults):
    def __init__(self):
        # Test Precision
        self.decimal_aic_R = DECIMAL_0
        self.decimal_aic_Stata = DECIMAL_2
        self.decimal_llf = DECIMAL_0



        nobs = 100
        x = np.arange(nobs)
        np.random.seed(54321)
#        y = 1.0 - .02*x - .001*x**2 + 0.001 * np.random.randn(nobs)
        self.X = np.c_[np.ones((nobs,1)),x,x**2]
        self.lny = np.exp(-(-1.0 + 0.02*x + 0.0001*x**2)) +\
                        0.001 * np.random.randn(nobs)

        GaussLog_Model = GLM(self.lny, self.X, \
                family=sm.families.Gaussian(sm.families.links.log))
        self.res1 = GaussLog_Model.fit()
        from results.results_glm import GaussianLog
        self.res2 = GaussianLog()

#    def setup(self):
#        if skipR:
#            raise SkipTest, "Rpy not installed"
#        GaussLogLink = r.gaussian(link = "log")
#        GaussLog_Res_R = RModel(self.lny, self.X, r.glm, family=GaussLogLink)
#        self.res2 = GaussLog_Res_R


#    def test_null_deviance(self):
#        assert_almost_equal(self.res1.null_deviance, self.res2.null_deviance,
#                    DECIMAL_1)

#    def check_params(self, params1, params2):
#        assert_almost_equal(params1, params2, DECIMAL_4)

#    def check_loglike(self, llf1, llf2):
#        assert_almost_equal(llf1, llf2, DECIMAL_0)

#    def check_aic_R(self, aic1, aic2):
#        assert_almost_equal(aic1, aic2, DECIMAL_0)
#TODO: is this a full test?

class TestGaussianInverse(CheckModelResults):
    def __init__(self):
        # Test Precisions

        self.decimal_bic_Stata = DECIMAL_2
        self.decimal_aic_R = DECIMAL_1
        self.decimal_aic_Stata = DECIMAL_3
        self.decimal_llf = DECIMAL_1
        self.decimal_resids = DECIMAL_3


        nobs = 100
        x = np.arange(nobs)
        np.random.seed(54321)
        y = 1.0 + 2.0 * x + x**2 + 0.1 * np.random.randn(nobs)
        self.X = np.c_[np.ones((nobs,1)),x,x**2]
        self.y_inv = (1. + .02*x + .001*x**2)**-1 + .001 * np.random.randn(nobs)
        InverseLink_Model = GLM(self.y_inv, self.X,
                family=sm.families.Gaussian(sm.families.links.inverse))
        InverseLink_Res = InverseLink_Model.fit()
        self.res1 = InverseLink_Res
        from results.results_glm import GaussianInverse
        self.res2 = GaussianInverse()

#    def setup(self):
#        if skipR:
#            raise SkipTest, "Rpy not installed."
#        InverseLink = r.gaussian(link = "inverse")
#        InverseLink_Res_R = RModel(self.y_inv, self.X, r.glm, family=InverseLink)
#        self.res2 = InverseLink_Res_R

    def check_params(self, params1, params2):
        assert_almost_equal(params1, params2, DECIMAL_4)

    def check_loglike(self, llf1, llf2):
        assert_almost_equal(llf1, llf2, DECIMAL_1)

    def check_aic_R(self, aic1, aic2):
        assert_almost_equal(aic1, aic2, DECIMAL_1)
#TODO: is this a full test?

#    @dec.knownfailureif(True, "This is a bug in Rpy")
    def test_null_deviance(self):
        assert_almost_equal(self.res1.null_deviance, self.res2.null_deviance,
                    DECIMAL_1)

class TestGlmBinomial(CheckModelResults):
    def __init__(self):
        '''
        Test Binomial family with canonical logit link using star98 dataset.
        '''
        from scikits.statsmodels.datasets.star98 import Load
#        from model_results import Star98
        from results.results_glm import Star98
        self.data = Load()
        self.data.exog = add_constant(self.data.exog)
        trials = self.data.endog[:,:2].sum(axis=1)
        self.res1 = GLM(self.data.endog, self.data.exog, \
        family=sm.families.Binomial()).fit(data_weights = trials)
        #NOTE: if you want to replicate with RModel
        #res2 = RModel(data.endog[:,0]/trials, data.exog, r.glm,
        #        family=r.binomial, weights=trials)

        self.res2 = Star98()

#    def check_params(self, params1, params2):
#        assert_almost_equal(params1, params2, DECIMAL_4)

#    def check_resids(self, resids1, resids2):
#        assert_almost_equal(resids1, resids2, DECIMAL_1)
        # rounding difference vs. stata

#    def check_aic_R(self, aic1, aic2):
#        assert_almost_equal(aic1, aic2, DECIMAL_4)

#    def check_aic_Stata(self, aic1, aic2):
#        assert_almost_equal(aic1, aic2, DECIMAL_4)

#    def check_loglike(self, llf1, llf2):
#        assert_almost_equal(llf1, llf2, DECIMAL_3)
        # precise up to 3 decimals

#    def check_bic(self, bic1, bic2):
#        assert_almost_equal(bic1, bic2, DECIMAL_2)
        # accurate to 1e-02

    def check_pearson_chi2(self, pearson_chi21, pearson_chi22):
        assert_almost_equal(pearson_chi21, pearson_chi22, DECIMAL_2)
        # Pearson's X2 sums residuals that are rounded differently in Stata
#TODO:
#Non-Canonical Links for the Binomial family require the algorithm to be
#slightly changed
#class TestGlmBinomialLog(CheckModelResults):
#    pass

#class TestGlmBinomialLogit(CheckModelResults):
#    pass

#class TestGlmBinomialProbit(CheckModelResults):
#    pass

#class TestGlmBinomialCloglog(CheckModelResults):
#    pass

#class TestGlmBinomialPower(CheckModelResults):
#    pass

#class TestGlmBinomialLoglog(CheckModelResults):
#    pass

#class TestGlmBinomialLogc(CheckModelResults):
#TODO: need include logc link
#    pass

class TestGlmBernoulli(CheckModelResults):
    def __init__(self):
        from results.results_glm import Lbw
        self.res2 = Lbw()
        self.res1 = GLM(self.res2.endog, self.res2.exog,
                family=sm.families.Binomial()).fit()

    def check_params(self, params1, params2):
        assert_almost_equal(params1, params2, DECIMAL_4)

    def check_resids(self, resids1, resids2):
        assert_almost_equal(resids1, resids2, DECIMAL_4)

    def check_aic_R(self, aic1, aic2):
        assert_almost_equal(aic1, aic2, DECIMAL_4)

    def check_aic_Stata(self, aic1, aic2):
        assert_almost_equal(aic1, aic2, DECIMAL_4)

    def check_loglike(self, llf1, llf2):
        assert_almost_equal(llf1, llf2, DECIMAL_4)

    def check_bic(self, bic1, bic2):
        assert_almost_equal(bic1, bic2, DECIMAL_4)

    def check_pearson_chi2(self, pearson_chi21, pearson_chi22):
        assert_almost_equal(pearson_chi21, pearson_chi22, DECIMAL_4)

#class TestGlmBernoulliIdentity(CheckModelResults):
#    pass

#class TestGlmBernoulliLog(CheckModelResults):
#    pass

#class TestGlmBernoulliProbit(CheckModelResults):
#    pass

#class TestGlmBernoulliCloglog(CheckModelResults):
#    pass

#class TestGlmBernoulliPower(CheckModelResults):
#    pass

#class TestGlmBernoulliLoglog(CheckModelResults):
#    pass

#class test_glm_bernoulli_logc(CheckModelResults):
#    pass

class TestGlmGamma(CheckModelResults):

    def __init__(self):
        '''
        Tests Gamma family with canonical inverse link (power -1)
        '''
        # Test Precisions
        self.decimal_aic_R = DECIMAL_0
        #TODO: the below is going to fail.
        self.decimal_llf = DECIMAL_0
        self.decimal_resids = DECIMAL_2



        from scikits.statsmodels.datasets.scotland import Load
#        from model_results import Scotvote
        from results.results_glm import Scotvote
        self.data = Load()
        self.data.exog = add_constant(self.data.exog)
        res1 = GLM(self.data.endog, self.data.exog, \
                    family=sm.families.Gamma()).fit()
#        res1.llf = res1.model.family.loglike(res1.model.endog, res1.mu, scale=1)
        #NOTE that this is Stata's default for loglikelihood
        # Ours is close to R's
        self.res1 = res1
        self.res2 = Scotvote()

#    def check_params(self, params1, params2):
#        assert_almost_equal(params1, params2, DECIMAL_4)

#    def check_resids(self, resids1, resids2):
#        assert_almost_equal(resids1, resids2, DECIMAL_2)

#    def check_aic_R(self, aic1, aic2):
#        assert_approx_equal(aic1-2, aic2, DECIMAL_3)
        # R includes another degree of freedom in calculation of AIC,
        # but not with
        # gamma for some reason
        # There is also a precision issue due to a different implementation?

#    def check_aic_Stata(self, aic1, aic2):
#        llf1 = self.res1.model.family.loglike(self.res1.model.endog,
#                self.res1.mu, scale=1)
#        aic1 = 2 *(self.res1.model.df_model + 1 - llf1)/self.res1.nobs
#        assert_almost_equal(aic1, aic2, DECIMAL_4)

#    def check_loglike(self, llf1, llf2):
#        llf1 = self.res1.model.family.loglike(self.res1.model.endog,
#                self.res1.mu, scale=1)
#        assert_almost_equal(llf1, llf2, DECIMAL_4)

#    def check_bic(self, bic1, bic2):
#        assert_almost_equal(bic1, bic2, DECIMAL_4)

#    def check_pearson_chi2(self, pearson_chi21, pearson_chi22):
#        assert_almost_equal(pearson_chi21, pearson_chi22, DECIMAL_4)

class TestGlmGammaLog(CheckModelResults):
    def __init__(self):
        # Test Precisions
        self.decimal_resids = DECIMAL_3
        self.decimal_aic_R = DECIMAL_1
        self.decimal_aic_Stata = DECIMAL_0
        self.decimal_llf = DECIMAL_1
        self.decimal_fittedvalues = DECIMAL_3


#        from model_results import Cancer
        from results.results_glm import CancerLog
        res2 = CancerLog()
        self.res1 = GLM(res2.endog, res2.exog,
            family=sm.families.Gamma(link=sm.families.links.log)).fit()
        self.res2 = res2


#    def setup(self):
#        if skipR:
#            raise SkipTest, "Rpy not installed."
#        self.res2 = RModel(self.data.endog, self.data.exog, r.glm,
#            family=r.Gamma(link="log"))
#        self.res2.null_deviance = 27.92207137420696 # From R (bug in rpy)
#        self.res2.bic = -154.1582089453923 # from Stata


#    def check_params(self, params1, params2):
#        assert_almost_equal(params1, params2, DECIMAL_4)

#    def check_resids(self, resids1, resids2):
#        assert_almost_equal(resids1, resids2, DECIMAL_4)

#    def check_aic_R(self, aic1, aic2):
#        assert_almost_equal(aic1, aic2, DECIMAL_0)

#    def check_loglike(self, llf1, llf2):
#        assert_almost_equal(llf1, llf2, DECIMAL_1)

#    def check_bic(self, bic1, bic2):
#        assert_almost_equal(bic1, bic2, DECIMAL_4)

class TestGlmGammaIdentity(CheckModelResults):
    def __init__(self):
        # Test Precisions
        self.decimal_resids = DECIMAL_0
        self.decimal_params = DECIMAL_2
        self.decimal_aic_R = DECIMAL_1
        self.decimal_aic_Stata = DECIMAL_0


#        from model_results import Cancer
        from results.results_glm import CancerIdentity
        res2 = CancerIdentity()
        self.res1 = GLM(res2.endog, res2.exog,
            family=sm.families.Gamma(link=sm.families.links.identity)).fit()
        self.res2 = res2

#    def setup(self):
#        if skipR:
#            raise SkipTest, "Rpy not installed."
#        self.res2 = RModel(self.data.endog, self.data.exog, r.glm,
#            family=r.Gamma(link="identity"))
#        self.res2.null_deviance = 27.92207137420696 # from R, Rpy bug

    def check_params(self, params1, params2):
        assert_almost_equal(params1, params2, DECIMAL_2)

    def check_resids(self, resids1, resids2):
        assert_almost_equal(resids1, resids2, DECIMAL_4)

    def check_aic_R(self, aic1, aic2):
        assert_almost_equal(aic1, aic2, DECIMAL_0)

    def check_loglike(self, llf1, llf2):
        assert_almost_equal(llf1, llf2, DECIMAL_1)

    def check_bic(self, bic1, bic2):
        assert_almost_equal(bic1, bic2, DECIMAL_4)

class TestGlmPoisson(CheckModelResults):
    def __init__(self):
        '''
        Tests Poisson family with canonical log link.

        Test results were obtained by R.
        '''
#        from model_results import Cpunish
        from results.results_glm import Cpunish
        from scikits.statsmodels.datasets.cpunish import Load
        self.data = Load()
        self.data.exog[:,3] = np.log(self.data.exog[:,3])
        self.data.exog = add_constant(self.data.exog)
        self.res1 = GLM(self.data.endog, self.data.exog,
                    family=sm.families.Poisson()).fit()
        self.res2 = Cpunish()

    def check_params(self, params1, params2):
        assert_almost_equal(params1, params2, DECIMAL_4)

    def check_resids(self, resids1, resids2):
        assert_almost_equal(resids1, resids2, DECIMAL_4)

    def check_aic_R(self, aic1, aic2):
        assert_almost_equal(aic1, aic2, DECIMAL_4)

    def check_aic_Stata(self, aic1, aic2):
        assert_almost_equal(aic1, aic2, DECIMAL_4)

    def check_loglike(self, llf1, llf2):
        assert_almost_equal(llf1, llf2, DECIMAL_4)

    def check_bic(self, bic1, bic2):
        assert_almost_equal(bic1, bic2, DECIMAL_4)

    def check_pearson_chi2(self, pearson_chi21, pearson_chi22):
        assert_almost_equal(pearson_chi21, pearson_chi22, DECIMAL_4)

#class TestGlmPoissonIdentity(CheckModelResults):
#    pass

#class TestGlmPoissonPower(CheckModelResults):
#    pass

class TestGlmInvgauss(CheckModelResults):
    def __init__(self):
        '''
        Tests the Inverse Gaussian family in GLM.

        Notes
        -----
        Used the rndivgx.ado file provided by Hardin and Hilbe to
        generate the data.  Results are read from model_results, which
        were obtained by running R_ig.s
        '''
        # Test Precisions
        self.decimal_aic_R = DECIMAL_1
        self.decimal_aic_Stata = DECIMAL_0
        self.decimal_loglike = DECIMAL_1

#        from model_results import InvGauss
        from results.results_glm import InvGauss
        res2 = InvGauss()
        self.res1 = GLM(res2.endog, res2.exog, \
                family=sm.families.InverseGaussian()).fit()
        self.res2 = res2

#    def setup(self):
#        if skipR:
#            raise nose.SkipTest('requires rpy')

#    def check_params(self, params1, params2):
#        assert_almost_equal(params1, params2, DECIMAL_4)

#    def check_resids(self, resids1, resids2):
#        assert_almost_equal(resids1, resids2, DECIMAL_4)

#    def check_aic_R(self, aic1, aic2):
#        assert_approx_equal(aic1, aic2, DECIMAL_4)
        # Off by 2e-1 due to implementation difference

#    def check_aic_Stata(self, aic1, aic2):
#        llf1 = self.res1.model.family.loglike(self.res1.model.endog,
#                self.res1.mu, scale=1)
#        aic1 = 2 * (self.res1.model.df_model + 1 - llf1)/self.res1.nobs
#        assert_almost_equal(aic1, aic2, DECIMAL_4)

#    def check_loglike(self, llf1, llf2):
#        llf1 = self.res1.model.family.loglike(self.res1.model.endog,
#                self.res1.mu, scale=1)    # Stata assumes scale = 1 in calc,
                                          # which shouldn't be right...
#        assert_almost_equal(llf1, llf2, DECIMAL_3)

#    def check_bic(self, bic1, bic2):
#        assert_almost_equal(bic1, bic2, DECIMAL_2) # precision in STATA

#    def check_pearson_chi2(self, pearson_chi21, pearson_chi22):
#        assert_almost_equal(pearson_chi21, pearson_chi22, DECIMAL_3)# summed resids

class TestGlmInvgaussLog(CheckModelResults):
    def __init__(self):
        # Test Precisions
        self.decimal_aic_R = DECIMAL_0
#        self.decimal_loglike = DECIMAL_0
        self.decimal_resids = DECIMAL_3


#        from model_results import Medpar1
        from results.results_glm import InvGaussLog
        res2 = InvGaussLog()
        res1 = GLM(res2.endog, res2.exog,
            family=sm.families.InverseGaussian(link=\
            sm.families.links.log)).fit()


        res2.null_deviance = 335.1539777981053 # from R, Rpy bug
        res2.llf = -12162.72308 # From Stata, Ours with scale = 1, which should
                            # not be the default?
                            #NOTE We have a big rounding difference vs R
        res1.llf = res1.model.family.loglike(res1.model.endog, res1.mu, scale=1)
        self.res1 = res1
        self.res2 = res2
                                     # common across Gamma implementation


#    def setup(self):
#        if skipR:
#            raise SkipTest, "Rpy not installed."
#        self.res2 = RModel(self.data.endog, self.data.exog, r.glm,
#            family=r.inverse_gaussian(link="log"))
#        self.res2.null_deviance = 335.1539777981053 # from R, Rpy bug
#        self.res2.llf = -12162.72308 # from Stata, R's has big rounding diff

#    def check_params(self, params1, params2):
#        assert_almost_equal(params1, params2, DECIMAL_4)

#    def check_resids(self, resids1, resids2):
#        assert_almost_equal(resids1, resids2, DECIMAL_4)

#    @dec.knownfailureif(True, "Big rounding difference vs. R")
#    def check_aic_R(self, aic1, aic2):
#        assert_almost_equal(aic1, aic2, DECIMAL_4)

#    def check_loglike(self, llf1, llf2):
#        llf1 = self.res1.model.family.loglike(self.res1.model.endog,
#                self.res1.mu, scale=1)
#        assert_almost_equal(llf1, llf2, DECIMAL_4)

class TestGlmInvgaussIdentity(CheckModelResults):
    def __init__(self):
        # Test Precisions
        self.decimal_aic_R = DECIMAL_0 #TODO: might fail
        self.decimal_aic_Stata = DECIMAL_0
        self.decimal_fittedvalues = DECIMAL_3
        self.decimal_loglike = DECIMAL_0
        self.decimal_params = DECIMAL_3

#        from model_results import Medpar1
        from results.results_glm import Medpar1
        self.data = Medpar1()
        self.res1 = GLM(self.data.endog, self.data.exog,
            family=sm.families.InverseGaussian(link=\
            sm.families.links.identity)).fit()
        from results.results_glm import InvGaussIdentity
        self.res2 = InvGaussIdentity()

#    def setup(self):
#        if skipR:
#            raise SkipTest, "Rpy not installed."
#        self.res2 = RModel(self.data.endog, self.data.exog, r.glm,
#            family=r.inverse_gaussian(link="identity"))
#        self.res2.null_deviance = 335.1539777981053 # from R, Rpy bug
#        self.res2.llf = -12163.25545    # from Stata, big diff with R

    def check_params(self, params1, params2):
        assert_almost_equal(params1, params2, DECIMAL_3)

    def check_resids(self, resids1, resids2):
        assert_almost_equal(resids1, resids2, DECIMAL_4)

#    @dec.knownfailureif(True, "Big rounding difference vs R")
    def check_aic_R(self, aic1, aic2):
        assert_almost_equal(aic1, aic2, DECIMAL_4)

    def check_loglike(self, llf1, llf2):
        llf1 = self.res1.model.family.loglike(self.res1.model.endog,
                self.res1.mu, scale=1)
        assert_almost_equal(llf1, llf2, DECIMAL_4)

class TestGlmNegbinomial(CheckModelResults):
    def __init__(self):
        '''
        Test Negative Binomial family with canonical log link
        '''
        # Test Precision
#        self.decimal_aic_R = DECIMAL_3
        self.decimal_resid = DECIMAL_1
        self.decimal_params = DECIMAL_3

        from scikits.statsmodels.datasets.committee import Load
        self.data = Load()
        self.data.exog[:,2] = np.log(self.data.exog[:,2])
        interaction = self.data.exog[:,2]*self.data.exog[:,1]
        self.data.exog = np.column_stack((self.data.exog,interaction))
        self.data.exog = add_constant(self.data.exog)
        self.res1 = GLM(self.data.endog, self.data.exog,
                family=sm.families.NegativeBinomial()).fit()
        from results.results_glm import Committee
        self.res2 = Committee()
        # Rpy does not return the same null deviance as R for some reason

#    def setup(self):
#        if skipR:
#            raise SkipTest, "Rpy not installed"
#        r.library('MASS')  # this doesn't work when done in rmodelwrap?
#        self.res2 = RModel(self.data.endog, self.data.exog, r.glm,
#                family=r.negative_binomial(1))
#        self.res2.null_deviance = 27.8110469364343

#    def check_params(self, params1, params2):
#        assert_almost_equal(params1, params2, DECIMAL_4-1)    # precision issue

#    def check_resids(self, resids1, resids2):
#        assert_almost_equal(resids1, resids2, DECIMAL_4)

#    def check_aic_R(self, aic1, aic2):
#        assert_almost_equal(aic1-2, aic2, DECIMAL_4)
        # note that R subtracts an extra degree of freedom for estimating
        # the scale

#    def check_aic_Stata(self, aic1, aic2):
#        aic1 = aci1/self.res1.nobs
#        assert_almost_equal(aic1, aic2, DECIMAL_4)

#    def check_loglike(self, llf1, llf2):
#        assert_almost_equal(llf1, llf2, DECIMAL_4)

#    def check_bic(self, bic1, bic2):
#        assert_almost_equal(bic1, bic2, DECIMAL_4)

#    def check_pearson_chi2(self, pearson_chi21, pearson_chi22):
#        assert_almost_equal(pearson_chi21, pearson_chi22, DECIMAL_4)

#class TestGlmNegbinomial_log(CheckModelResults):
#    pass

#class TestGlmNegbinomial_power(CheckModelResults):
#    pass

#class TestGlmNegbinomial_nbinom(CheckModelResults):
#    pass

if __name__=="__main__":
    #run_module_suite()
    #taken from Fernando Perez:
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb'],
                       exit=False)
