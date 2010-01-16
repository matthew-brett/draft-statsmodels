.. currentmodule:: scikits.statsmodels.sandbox


.. _sandbox:


Sandbox
=======

Introduction
------------

This sandbox contains code that is for various resons not ready to be 
included in statsmodels proper. It contains modules from the old stats.models
code that have not been tested, verified and updated to the new statsmodels
structure: cox survival model, mixed effects model with repeated measures,
generalized additive model and the formula framework. The sandbox also 
contains code that is currently being worked on until it fits the pattern 
of statsmodels or is sufficiently tested.

All sandbox modules have to be explicitly imported to indicate that they are
not yet part of the core of statsmodels. The quality and testing of the
sandbox code varies widely.


.. automodule:: scikits.statsmodels.sandbox


Examples
--------
    >>> import scikits.statsmodels as sm
    >>> data = sm.datasets.scotland.Load()
    >>> data.exog = sm.add_constant(data.exog)

    Instantiate a gamma family model with the default link function.

    >>> gamma_model = sm.GLM(data.endog, data.exog,
            family=sm.family.Gamma())
    >>> gamma_results = gamma_model.fit()

see also the `examples` and the `tests` folders


Module Reference
----------------


Time Series analysis :mod:`tsa`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this part we develop models and functions that will be useful for time
series analysis, initially focused on the ARMA model and functions to simulate
arma processes, and basic statistical properties such as autocorrelation, 
periodogram both estimated from data and the theoretical statistic given the
lag polynomials of the ARMA process, and tools to work with AR and MA 
lag polynomials.  

Some of the functions are currently written mainly to discover a way to use
existing functions in scipy for time series analysis. Related functions are
available in matplotlib, nitime, and scikits.talkbox. Those functions are
designed more for the use in signal processing where longer time series are
available and work largely in the frequency domain. 
 

.. currentmodule:: scikits.statsmodels.sandbox


      
Time Series Properties
""""""""""""""""""""""

.. autosummary::
   :toctree: generated/
      
   tsa.acf
   tsa.acovf
   tsa.pacf_ols
   tsa.pacf_yw
   tsa.ccf
   tsa.ccovf

ARMA Modeling
"""""""""""""
   
.. autosummary::
   :toctree: generated/
   
   tsa.ARIMA
   tsa.arma_acf
   tsa.arma_acovf
   tsa.arma_generate_sample
   tsa.arma_impulse_response

Moving Window Statistics
""""""""""""""""""""""""

.. autosummary::
   :toctree: generated/

   tsa.movmean
   tsa.movmoment
   tsa.movorder
   tsa.movstat
   tsa.movvar

   


Regression and ANOVA
^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: scikits.statsmodels.sandbox.regression

The following two ANOVA functions are fully tested against the NIST test data
for balanced one-way ANOVA. ``anova_oneway`` follows the same pattern as the
oneway anova function in scipy.stats but with higher precision for badly 
scaled problems. ``anova_ols`` produces the same results as the one way anova
however using the OLS model class. It also verifies against the NIST tests, 
with some problems in the worst scaled cases. It shows how to do simple ANOVA
using statsmodels in three lines and is also best taken as a recipe.  


.. autosummary::
   :toctree: generated/
   
   anova_oneway
   anova_ols
   wls_prediction_std


The following are helper functions for working with dummy variables and
generating ANOVA results with OLS. They are best considered as recipes since
they were written with a specific use in mind. These function will eventually
be rewritten or reorganized.

.. autosummary::
   :toctree: generated/
   
   try_ols_anova.data2dummy
   try_ols_anova.data2groupcont
   try_ols_anova.data2proddummy
   try_ols_anova.dropname
   try_ols_anova.form2design

The following are helper functions for group statistics where groups are 
defined by a label array. The qualifying comments for the previous group
 apply similar apply also to this group of functions.


.. autosummary::
   :toctree: generated/

   try_catdata.cat2dummy
   try_catdata.convertlabels
   try_catdata.groupsstats_1d
   try_catdata.groupsstats_dummy
   try_catdata.groupstatsbin
   try_catdata.labelmeanfilter
   try_catdata.labelmeanfilter_nd
   try_catdata.labelmeanfilter_str

Additional to these functions, sandbox regression still contains several 
examples, that are illustrative of the use of the regression models of
statsmodels.

Regression with Discrete Dependent Variable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

 .. currentmodule:: scikits.statsmodels.sandbox.discretemod

.. autosummary::
   :toctree: generated/
      
   DiscreteModel
   DiscreteResults
   Logit
   MNLogit
   NbReg
   NegBinTwo
   Poisson
   Probit
   Weibull


Seemingly Unrelated Regression
""""""""""""""""""""""""""""""

.. currentmodule:: scikits.statsmodels.sandbox.sysreg

.. autosummary::
   :toctree: generated/
      
   SUR

Miscellaneous
^^^^^^^^^^^^^
 .. currentmodule:: scikits.statsmodels.sandbox.tools.tools_tsa


Tools for Time Series Analysis
""""""""""""""""""""""""""""""

.. autosummary::
   :toctree: generated/

   lagmat
   lagmat2ds
   grangercausalitytests


Tools: Principal Component Analysis
"""""""""""""""""""""""""""""""""""

.. currentmodule:: scikits.statsmodels.sandbox.tools.tools_pca

.. autosummary::
   :toctree: generated/
   
   pca
   pcasvd



Graphics
""""""""

.. currentmodule:: scikits.statsmodels.sandbox

.. autosummary::
   :toctree: generated/
      
   graphics.qqplot
   
Descriptive Statistics Printing
"""""""""""""""""""""""""""""""

.. currentmodule:: scikits.statsmodels.sandbox

.. autosummary::
   :toctree: generated/
      
   descstats.sign_test
   descstats.descstats
   
   


Original stats.models
^^^^^^^^^^^^^^^^^^^^^

None of these are fully working. The formula framework is used by cox and
mixed.

**Mixed Effects Model with Repeated Measures using an EM Algorithm**

:mod:`scikits.statsmodels.sandbox.mixed`


**Cox Proportional Hazards Model**

:mod:`scikits.statsmodels.sandbox.cox`

**Generalized Additive Models**

:mod:`scikits.statsmodels.sandbox.gam`

**Formula**

:mod:`scikits.statsmodels.sandbox.formula`


