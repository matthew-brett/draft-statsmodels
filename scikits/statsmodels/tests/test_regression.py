"""
Test functions for models.regression
"""
import numpy as np
from numpy.testing import *
from scipy.linalg import toeplitz
from scikits.statsmodels.tools import add_constant
from scikits.statsmodels.regression import OLS, GLSAR, WLS, GLS, yule_walker
from check_for_rpy import skip_rpy
from nose import SkipTest
from scipy.stats import t as student_t

DECIMAL_4 = 4
DECIMAL_3 = 3
DECIMAL_2 = 2
DECIMAL_1 = 1
DECIMAL_7 = 7
DECIMAL_0 = 0
skipR = skip_rpy()
if not skipR:
    from rpy import r, RPyRException
    from rmodelwrap import RModel


class CheckRegressionResults(object):
    '''
    res2 contains results from Rmodelwrap or were obtained from a statistical
    packages such as R, Stata, or SAS and were written to model_results
    '''

    decimal_params = DECIMAL_4
    def test_params(self):
        assert_almost_equal(self.res1.params, self.res2.params,
                self.decimal_params)

    decimal_standarderrors = DECIMAL_4
    def test_standarderrors(self):
        assert_almost_equal(self.res1.bse,self.res2.bse,
                self.decimal_standarderrors)

    decimal_confidenceintervals = DECIMAL_4
    def test_confidenceintervals(self):
#        if hasattr(self.res2, 'conf_int'):
#            self.check_confidenceintervals(self.res1.conf_int(),
#                self.res2.conf_int)
#        else:
#            raise SkipTest, "Results from Rpy"
#NOTE: stata rounds residuals (at least) to sig digits so approx_equal
        conf1 = self.res1.conf_int()
        conf2 = self.res2.conf_int()
        for i in range(len(conf1)):
            assert_approx_equal(conf1[i][0], conf2[i][0],
                    self.decimal_confidenceintervals)
            assert_approx_equal(conf1[i][1], conf2[i][1],
                    self.decimal_confidenceintervals)

#        assert_almost_equal(self.res1.conf_int(), self.res2.conf_int,
#                self.decimal_confidenceintervals)

    decimal_conf_int_subset = DECIMAL_4
    def test_conf_int_subset(self):
        if len(self.res1.params) > 1:
            ci1 = self.res1.conf_int(cols=(1,2))
            ci2 = self.res1.conf_int()[1:3]
            assert_almost_equal(ci1, ci2, self.decimal_conf_int_subset)
        else:
            pass
#            SkipTest, "No subset of intervals for one parameter fit"

    decimal_scale = DECIMAL_4
    def test_scale(self):
        assert_almost_equal(self.res1.scale, self.res2.scale,
                self.decimal_scale)

    decimal_rsquared = DECIMAL_4
    def test_rsquared(self):
#        if hasattr(self.res2, 'rsquared'):
        assert_almost_equal(self.res1.rsquared, self.res2.rsquared,
                self.decimal_rsquared)
#        else:
#            raise SkipTest, "Results from R"

    decimal_rsquared_adj = DECIMAL_4
    def test_rsquared_adj(self):
#        if hasattr(self.res2, 'rsquared_adj'):
        assert_almost_equal(self.res1.rsquared_adj, self.res2.rsquared_adj,
                    self.decimal_rsquared_adj)
#        else:
#            raise SkipTest, "Results from R"

    def test_degrees(self):
#        if hasattr(self.res2, 'df_resid') and hasattr(self.res2, 'df_model'):
        assert_equal(self.res1.model.df_model, self.res2.df_model)
        assert_equal(self.res1.model.df_resid, self.res2.df_resid)
#        else:
#            raise SkipTest, "Results from R"

    decimal_ess = DECIMAL_4
    def test_ess(self):
        """
        Explained Sum of Squares
        """
#        if hasattr(self.res2, 'ess'):
        assert_almost_equal(self.res1.ess, self.res2.ess,
                    self.decimal_ess)
#        else:
#            raise SkipTest, "Results from Rpy"

    decimal_ssr = DECIMAL_4
    def test_sumof_squaredresids(self):
#        if hasattr(self.res2, 'ssr'):
        assert_almost_equal(self.res1.ssr, self.res2.ssr, self.decimal_ssr)
#        else:
#            raise SkipTest, "Results from Rpy"

    decimal_mse_resid = DECIMAL_4
    def test_mse_resid(self):
        """
        Mean squared error of residuals
        """
#        if hasattr(self.res2, "mse_model") and hasattr(self.res2, "mse_resid"):
        assert_almost_equal(self.res1.mse_model, self.res2.mse_model,
                    self.decimal_mse_resid)

    decimal_mse_model = DECIMAL_4
    def test_mse_model(self):
        assert_almost_equal(self.res1.mse_resid, self.res2.mse_resid,
                    self.decimal_mse_model)
#        else:
#            raise SkipTest, "Results from Rpy"

    decimal_fvalue = DECIMAL_4
    def test_fvalue(self):
#        if hasattr(self.res2, 'fvalue'):
            #didn't change this, not sure it should complain -inf not equal -inf
            #if not (np.isinf(self.res1.fvalue) and np.isinf(self.res2.fvalue)):
        assert_almost_equal(self.res1.fvalue, self.res2.fvalue,
                self.decimal_fvalue)
#        else:
#            raise SkipTest, "Results from R"

    decimal_loglike = DECIMAL_4
    def test_loglike(self):
        assert_almost_equal(self.res1.llf, self.res2.llf, self.decimal_loglike)

    decimal_aic = DECIMAL_4
    def test_aic(self):
#        if hasattr(self.res2, 'aic'):
        assert_almost_equal(self.res1.aic, self.res2.aic, self.decimal_aic)
#        else:
#            raise SkipTest, "Results from Rpy"

    decimal_bic = DECIMAL_4
    def test_bic(self):
#        if hasattr(self.res2, 'bic'):
        assert_almost_equal(self.res1.bic, self.res2.bic, self.decimal_bic)
#        else:
#            raise SkipTest, "Results from Rpy"

    decimal_pvalues = DECIMAL_4
    def test_pvalues(self):
        assert_almost_equal(self.res1.pvalues, self.res2.pvalues,
            self.decimal_pvalues)

    decimal_wresid = DECIMAL_4
    def test_wresid(self):
#        if not hasattr(self.res2, 'wresid'):
#            raise SkipTest('Comparison results (res2) has no wresid')
#        else:
        assert_almost_equal(self.res1.wresid, self.res2.wresid,
            self.decimal_wresid)

    decimal_resids = DECIMAL_4
    def test_resids(self):
        assert_almost_equal(self.res1.resid, self.res2.resid,
            self.decimal_resids)

#TODO: test fittedvalues

class TestOLS(CheckRegressionResults):
    def __init__(self):
        from scikits.statsmodels.datasets.longley import Load
        from results.results_regression import Longley
        data = Load()
        data.exog = add_constant(data.exog)
        res1 = OLS(data.endog, data.exog).fit()
        res2 = Longley()
        res2.wresid = res1.wresid # workaround hack
        self.res1 = res1
        self.res2 = res2


#    def check_confidenceintervals(self, conf1, conf2):
#        for i in range(len(conf1)):
#            assert_approx_equal(conf1[i][0], conf2[i][0], 6)
#            assert_approx_equal(conf1[i][1], conf2[i][1], 6)
            # stata rounds big residuals to significant digits

#    def check_params(self, params1, params2):
#        assert_almost_equal(params1, params2, DECIMAL_4)

#  Robust error tests.  Compare values computed with SAS
    def test_HC0_errors(self):
        '''
        They are split up because the copied results do not have any DECIMAL_4
        places for the last place.
        '''
        assert_almost_equal(self.res1.HC0_se[:-1],
                self.res2.HC0_se[:-1], DECIMAL_4)
        assert_approx_equal(np.round(self.res1.HC0_se[-1]), self.res2.HC0_se[-1])

    def test_HC1_errors(self):
        assert_almost_equal(self.res1.HC1_se[:-1],
                self.res2.HC1_se[:-1], DECIMAL_4)
        assert_approx_equal(self.res1.HC1_se[-1], self.res2.HC1_se[-1])

    def test_HC2_errors(self):
        assert_almost_equal(self.res1.HC2_se[:-1],
                self.res2.HC2_se[:-1], DECIMAL_4)
        assert_approx_equal(self.res1.HC2_se[-1], self.res2.HC2_se[-1])

    def test_HC3_errors(self):
        assert_almost_equal(self.res1.HC3_se[:-1],
                self.res2.HC3_se[:-1], DECIMAL_4)
        assert_approx_equal(self.res1.HC3_se[-1], self.res2.HC3_se[-1])

class TestFtest(object):
    """
    Tests f_test vs. RegressionResults
    """
    def __init__(self):
        from scikits.statsmodels.datasets.longley import Load
        data = Load()
        data.exog = add_constant(data.exog)
        self.res1 = OLS(data.endog, data.exog).fit()
        R = np.identity(7)[:-1,:]
        self.Ftest = self.res1.f_test(R)

    def test_F(self):
        assert_almost_equal(self.Ftest.fvalue, self.res1.fvalue, DECIMAL_4)

    def test_p(self):
        assert_almost_equal(self.Ftest.pvalue, self.res1.f_pvalue, DECIMAL_4)

    def test_Df_denom(self):
        assert_equal(self.Ftest.df_denom, self.res1.model.df_resid)

    def test_Df_num(self):
        assert_equal(self.Ftest.df_num, 6)

class TestFTest2(TestFtest):
    '''
    A joint test that the coefficient on
    GNP = the coefficient on UNEMP  and that the coefficient on
    POP = the coefficient on YEAR for the Longley dataset.

    Ftest1 is from statsmodels.  Results are from Rpy using R's car library.
    '''
    def setup(self):
        R2 = [[0,1,-1,0,0,0,0],[0, 0, 0, 0, 1, -1, 0]]
        self.Ftest1 = self.res1.f_test(R2)
#        from results.results_regression import FTest2
#        self.Ftest2 = FTest2


#    def setup(self):
#        if skipR:
#            raise SkipTest, "Rpy not installed"
#        try:
#            r.library('car')
#        except RPyRException:
#            raise SkipTest, "car library not installed for R"
#        self.R2 = [[0,1,-1,0,0,0,0],[0, 0, 0, 0, 1, -1, 0]]
#        self.Ftest2 = self.res1.f_test(self.R2)
#        self.R_Results = RModel(self.data.endog, self.data.exog, r.lm).robj
#        self.F = r.linear_hypothesis(self.R_Results,
#                r.c('x.2 = x.3', 'x.5 = x.6'))


    def test_fvalue(self):
        assert_almost_equal(self.Ftest1.fvalue, 9.7404618732968196, DECIMAL_4)

    def test_pvalue(self):
        assert_almost_equal(self.Ftest1.pvalue, 0.0056052885317493459,
                DECIMAL_4)

    def test_df_denom(self):
        assert_equal(self.Ftest1.df_denom, 9)

    def test_df_num(self):
        assert_equal(self.Ftest1.df_num, 2)

class TestTtest(object):
    '''
    Test individual t-tests.  Ie., are the coefficients significantly
    different than zero.

        '''
    def __init__(self):
        from scikits.statsmodels.datasets.longley import Load
        data = Load()
        self.data = data
        data.exog = add_constant(data.exog)
        self.res1 = OLS(data.endog, data.exog).fit()

#    def setup(self):
#        if skipR:
#            raise SkipTest, "Rpy not installed"
#        else:
        R = np.identity(7)
        self.Ttest = self.res1.t_test(R)
#        self.R_Results = RModel(data.endog, data.exog, r.lm).robj

    def test_tvalue(self):
        assert_almost_equal(self.Ttest.tvalue, self.res1.t(), DECIMAL_4)

    def test_sd(self):
        assert_almost_equal(self.Ttest.sd, self.res1.bse, DECIMAL_4)

    def test_pvalue(self):
        assert_almost_equal(self.Ttest.pvalue,
                student_t.sf(np.abs(self.res1.t()),self.res1.model.df_resid),
                    DECIMAL_4)

    def test_df_denom(self):
        assert_equal(self.Ttest.df_denom, self.res1.model.df_resid)

    def test_effect(self):
        assert_almost_equal(self.Ttest.effect, self.res1.params)

class TestTtest2(TestTtest):
    '''
    Tests the hypothesis that the coefficients on POP and YEAR
    are equal.
    '''
    def setup(self):
        if skipR:
            raise SkipTest, "Rpy not installed"
        try:
            r.library('car')
        except RPyRException:
            raise SkipTest, "car library not installed for R"
        R = np.zeros(len(self.res1.params))
        R[4:6] = [1,-1]
        self.R = R
        self.Ttest1 = self.res1.t_test(self.R)
        self.R_Results = RModel(self.data.endog, self.data.exog, r.lm).robj
        self.Ttest2 = r.linear_hypothesis(self.R_Results, 'x.5 = x.6')
        t = np.sign(np.inner(self.R, self.res1.params))*\
            np.sqrt(self.Ttest2['F'][1])
        self.t = t
        effect = np.inner(self.R, self.res1.params)
        self.effect = effect

    def test_tvalue(self):
        assert_almost_equal(self.Ttest1.tvalue, self.t, DECIMAL_4)

    def test_sd(self):
        assert_almost_equal(self.Ttest1.sd, self.effect/self.t, DECIMAL_4)

    def test_pvalue(self):
        assert_almost_equal(self.Ttest1.pvalue, student_t.sf(np.abs(self.t),
            self.Ttest2['Res.Df'][0]),
            DECIMAL_4)

    def test_df_denom(self):
        assert_equal(self.Ttest1.df_denom, self.Ttest2['Res.Df'][0])

    def test_effect(self):
        assert_almost_equal(self.Ttest1.effect, self.effect, DECIMAL_4)

class TestGLS(object):
    '''
    These test results were obtained by replication with R.
    '''
    def __init__(self):
        from scikits.statsmodels.datasets.longley import Load
        from model_results import LongleyGls

        data = Load()
        exog = add_constant(np.column_stack(\
                (data.exog[:,1],data.exog[:,4])))
        tmp_results = OLS(data.endog, exog).fit()
        rho = np.corrcoef(tmp_results.resid[1:],
                tmp_results.resid[:-1])[0][1] # by assumption
        order = toeplitz(np.arange(16))
        sigma = rho**order
        GLS_results = GLS(data.endog, exog, sigma=sigma).fit()
        self.res1 = GLS_results
        self.res2 = LongleyGls()

    def test_aic(self):
        assert_approx_equal(self.res1.aic+2, self.res2.aic, 3)

    def test_bic(self):
        assert_approx_equal(self.res1.bic, self.res2.bic, 2)

    def test_loglike(self):
        assert_almost_equal(self.res1.llf, self.res2.llf, DECIMAL_0)

    def test_params(self):
        assert_almost_equal(self.res1.params, self.res2.params, DECIMAL_1)

    def test_resid(self):
        assert_almost_equal(self.res1.resid, self.res2.resid, DECIMAL_4)

    def test_scale(self):
        assert_almost_equal(self.res1.scale, self.res2.scale, DECIMAL_4)

    def test_tvalues(self):
        assert_almost_equal(self.res1.t(), self.res2.t, DECIMAL_4)

    def test_standarderrors(self):
        assert_almost_equal(self.res1.bse, self.res2.bse, DECIMAL_4)

    def test_fittedvalues(self):
        assert_almost_equal(self.res1.fittedvalues, self.res2.fittedvalues,
                DECIMAL_4)

    def test_pvalues(self):
        assert_almost_equal(self.res1.pvalues, self.res2.pvalues, DECIMAL_4)

class TestGLS_nosigma(CheckRegressionResults):
    '''
    Test that GLS with no argument is equivalent to OLS.
    '''
    def __init__(self):
        from scikits.statsmodels.datasets.longley import Load
        data = Load()
        data.exog = add_constant(data.exog)
        ols_res = OLS(data.endog, data.exog).fit()
        gls_res = GLS(data.endog, data.exog).fit()
        self.res1 = gls_res
        self.res2 = ols_res
#        self.res2.conf_int = self.res2.conf_int()

#    def check_confidenceintervals(self, conf1, conf2):
#        assert_almost_equal(conf1, conf2, DECIMAL_4)

#class TestWLS(CheckRegressionResults):
#    '''
#    Test WLS with Greene's credit card data
#    '''
#    def __init__(self):
#        from scikits.statsmodels.datasets.ccard import Load
#        self.data = Load()
#        self.res1 = WLS(self.data.endog, self.data.exog,
#                weights=1/self.data.exog[:,2]).fit()
#FIXME: triaged results for noconstant
#        self.res1.ess = self.res1.uncentered_tss - self.res1.ssr
#        self.res1.rsquared = self.res1.ess/self.res1.uncentered_tss
#        self.res1.mse_model = self.res1.ess/(self.res1.df_model + 1)
#        self.res1.fvalue = self.res1.mse_model/self.res1.mse_resid
#        self.res1.rsquared_adj = 1 -(self.res1.nobs)/(self.res1.df_resid)*\
#                (1-self.res1.rsquared)

#    def setup(self):
#        if skipR:
#            raise SkipTest, "Rpy not installed"
#        self.res2 = RModel(self.data.endog, self.data.exog, r.lm,
#                        weights=1/self.data.exog[:,2])
#        self.res2.wresid = self.res2.rsum['residuals']
#        self.res2.scale = self.res2.scale**2 # R has sigma not sigma**2

#    def check_confidenceintervals(self, conf1, conf2):
#        assert_almost_equal(conf1, conf2, DECIMAL_4)


class TestWLS_GLS(CheckRegressionResults):
    def __init__(self):
        from scikits.statsmodels.datasets.ccard import Load
        data = Load()
        self.res1 = WLS(data.endog, data.exog, weights = 1/data.exog[:,2]).fit()
        self.res2 = GLS(data.endog, data.exog, sigma = data.exog[:,2]).fit()

    def check_confidenceintervals(self, conf1, conf2):
        assert_almost_equal(conf1, conf2(), DECIMAL_4)

class TestWLS_OLS(CheckRegressionResults):
    def __init__(self):
        from scikits.statsmodels.datasets.longley import Load
        data = Load()
        data.exog = add_constant(data.exog)
        self.res1 = OLS(data.endog, data.exog).fit()
        self.res2 = WLS(data.endog, data.exog).fit()

    def check_confidenceintervals(self, conf1, conf2):
        assert_almost_equal(conf1, conf2(), DECIMAL_4)

class TestGLS_OLS(CheckRegressionResults):
    def __init__(self):
        from scikits.statsmodels.datasets.longley import Load
        data = Load()
        data.exog = add_constant(data.exog)
        self.res1 = GLS(data.endog, data.exog).fit()
        self.res2 = OLS(data.endog, data.exog).fit()

    def check_confidenceintervals(self, conf1, conf2):
        assert_almost_equal(conf1, conf2(), DECIMAL_4)

#TODO: test AR
# why the two-stage in AR?
#class test_ar(object):
#    from scikits.statsmodels.datasets.sunspots import Load
#    data = Load()
#    model = AR(data.endog, rho=4).fit()
#    R_res = RModel(data.endog, aic="FALSE", order_max=4)

#    def test_params(self):
#        assert_almost_equal(self.model.rho,
#        pass

#    def test_order(self):
# In R this can be defined or chosen by minimizing the AIC if aic=True
#        pass


class TestYuleWalker(object):
    def __init__(self):
        from scikits.statsmodels.datasets.sunspots import Load
        self.data = Load()
        self.rho, self.sigma = yule_walker(self.data.endog, order=4, method="mle")

    def setup(self):
        if skipR:
            raise SkipTest, "Rpy not installed."

        R_results = r.ar(self.data.endog, aic="FALSE", order_max=4)
        self.R_params = R_results['ar']

    def test_params(self):
        assert_almost_equal(self.rho, self.R_params, DECIMAL_4)

class TestDataDimensions(CheckRegressionResults):
    def __init__(self):
        np.random.seed(54321)
        self.endog_n_ = np.random.uniform(0,20,size=30)
        self.endog_n_one = self.endog_n_[:,None]
        self.exog_n_ = np.random.uniform(0,20,size=30)
        self.exog_n_one = self.exog_n_[:,None]
        self.degen_exog = self.exog_n_one[:-1]
        self.mod1 = OLS(self.endog_n_one, self.exog_n_one)
        self.mod1.df_model += 1
        #self.mod1.df_resid -= 1
        self.res1 = self.mod1.fit()
        # Note that these are created for every subclass..
        # A little extra overhead probably
        self.mod2 = OLS(self.endog_n_one, self.exog_n_one)
        self.mod2.df_model += 1
        self.res2 = self.mod2.fit()

    def check_confidenceintervals(self, conf1, conf2):
        assert_almost_equal(conf1, conf2(), DECIMAL_4)

class TestNxNx(TestDataDimensions):
    def __init__(self):
        super(TestNxNx, self).__init__()
        self.mod2 = OLS(self.endog_n_,self.exog_n_)
        self.mod2.df_model += 1
        self.res2 = self.mod2.fit()

class TestNxOneNx(TestDataDimensions):
    def __init__(self):
        super(TestNxOneNx, self).__init__()
        self.mod2 = OLS(self.endog_n_one, self.exog_n_)
        self.mod2.df_model += 1
        self.res2 = self.mod2.fit()

class TestNxNxOne(TestDataDimensions):
    def __init__(self):
        super(TestNxNxOne, self).__init__()
        self.mod2 = OLS(self.endog_n_, self.exog_n_one)
        self.mod2.df_model += 1
        self.res2 = self.mod2.fit()

def test_bad_size():
    np.random.seed(54321)
    data = np.random.uniform(0,20,31)
    assert_raises(ValueError, OLS, data, data[1:])

if __name__=="__main__":
    #run_module_suite()
    import nose
    #nose.runmodule(argv=[__file__,'-vvs','-x'], exit=False) #, '--pdb'




