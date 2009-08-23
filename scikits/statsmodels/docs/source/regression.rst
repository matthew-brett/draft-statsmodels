.. currentmodule:: scikits.statsmodels.regression


.. _regression:

Regression
==========

Regression contains linear models with independently and identically 
distributed errors and for errors with heteroscedasticit or autocorrelation

The statistical model is assumed to be

y = X b + u,  where u is distributed with mean 0 and covariance \Sigma

depending on the assumption on V, we have currently four classes available

* GLS : generalized least squares for arbitrary covariance V
* OLS : ordinary least squares for i.i.d. errors
* WLS : eighted least squares for heteroscedastic errors
* GLSAR : feasible generalized least squares with autocorrelated AR(p) errors

All regression models define the same methods and follow the same structure, 
and can be used in a similar fashion. Some of them contain additional model 
spedific methods and attributes.

GLS is the superclass of the other regression classes. class hierachy


.. autosummary::
   :toctree: generated/

   OLS
   GLS
   WLS
   GLSAR
