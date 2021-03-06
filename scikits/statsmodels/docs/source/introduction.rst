.. currentmodule:: scikits.statsmodels

************
Introduction
************

Background
----------

Scipy.stats.models was originally written by Jonathan Taylor.
For some time it was part of scipy but then removed from it. During
the Google Summer of Code 2009, stats.models was corrected, tested and 
enhanced.

Now, we are releasing it as a standalone package in the scikits
namespace as :mod:`scikits.statsmodels` to gain some experience with 
actual usage of it. This scikits.statsmodels is intended to be eventually 
re-included in scipy.


Current Status
--------------

statsmodels is a pure python package.

statsmodels includes:

  * regression: mainly OLS and generalized least squares, GLS
    including weighted least squares and least squares with AR
    errors.
  * glm: generalized linear models
  * rlm: robust linear models
  * discretemod: regression with discrete dependent variables, Logit, Probit, 
    MNLogit, Poisson, based on maximum likelihood estimators 
  * datasets: for examples and tests

The other code which we didn't have enough time to verify and fix
was moved to a sandbox folder. The formula framework is not used any
more (in the verified code). The sandbox also contains models and functions
that we are currently developing, partially unfinished and not fully tested.

Compared to the original code, the class structure and some of the
method arguments have changed. Additional estimation
results, e.g. test statistics have been included.

Most importantly, most results have been verified with at least one 
other statistical package: R, Stata or SAS. The guiding principal for the 
rewrite was that all numbers have to be verified, even if we don't manage 
to cover everything. There are a few remaining issues, that we hope to 
clear up soon. Not all parts of the code have been tested for unexpected 
inputs and been made robust against them. Additionally, many of the tests 
call rpy to compare the results directly with R. We use an extended 
wrapper for R models in the test suite. This provides greater flexibility 
writing new test cases, but will eventually be replaced by hard coded 
expected results.

The code is written for plain NumPy arrays.

We have also included several datasets from the public domain and by
permission for the tests and examples.  The datasets follow
fairly closely David Cournapeau's datasets proposal in
scikits.learn, with some small modifications. The datasets
are set up so that it is easy to add more datasets.

Looking Forward
---------------

We are distributing statsmodels as a standalone package to gain 
experience with the API, and to allow us to make changes without 
being committed to backwards compatibility. It will also give us 
the opportunity to find and kill some remaining bugs, and fill 
some holes in our test suite. However, statsmodels is intended 
to become part of scipy after some maturing of the package.

Summer 2009, there was a discussion on the nipy
mailing list on the structure of the API and about possible
additional methods for the model classes. We would like
to invite everyone to give statsmodels a test drive and report
comments and possibilities for improvement and bugs to the 
scipy-user or statsmodels mailing lists or file tickets on our 
bug tracker at https://bugs.launchpad.net/statsmodels

The development repository is at http://code.launchpad.net/statsmodels .


We would also like to use statsmodels, or projects related to it, as 
a staging ground for new models. The current maintainers
are mostly interested in econometrics and time series analysis,
but we would like to invite any users or developers to contribute
their own extensions to existing models or new models.
statsmodels also contains some additional models in a sandbox folder. 
Those models were part of the original stats.models, but there was not
enough time during GSOC 2009 to test, correct and refactor them. Any
help to clean them up and bring them towards our testing standards
would be very appreciated. Whether additional models are included in 
scipy or remain separate can be discussed as they mature.

statsmodels is distributed under the same license as scipy (BSD) so 
it can be readily integrated into scipy.

Josef Perktold and Skipper Seabold

