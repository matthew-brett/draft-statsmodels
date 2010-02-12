This is a simple scikits. The main intent is to serve as a template for new
scikits.

Installation from sources
=========================

In the directory example (the same as the file you are reading now), just do:

python setup.py install

See INSTALL.txt for requirements or 

http://statsmodels.sourceforge.net/

For more information.


=============
Release Notes
=============

Background
==========

The statsmodels code was started by Jonathan Taylor and was formerly included 
as part of scipy. It was taken up to be tested, corrected, and extended as part
of the Google Summer of Code 2009.

What it is
==========

We are now releasing the efforts of the last few months under the scikits 
namespace as scikits.statsmodels. Statsmodels is a pure python package that 
requires numpy and scipy. It offers a convenient interface for fitting 
parameterized statistical models with growing support for displaying univariate
and multivariate summary statistics, regression summaries, and (postestimation)
statistical tests.

Main Feautures
==============

* regression: Generalized least squares (including weighted least squares and
least squares with autoregressive errors), ordinary least squares.
* glm: Generalized linear models with support for all of the one-parameter 
exponential family distributions.
* discrete choice models: Poisson, probit, logit, multinomial logit
* rlm: Robust linear models with support for several M-estimators.
* datasets: Datasets to be distributed and used for examples and in testing.

There is also a sandbox which contains code for generalized additive models 
(untested), mixed effects models, cox proportional hazards model (both are 
untested and still dependent on the nipy formula framework), generating 
descriptive statistics, and printing table output to ascii, latex, and html.
There is also experimental code for systems of equations regression, 
time series models, and information theoretic measures.  None of this code 
is considered "production ready".

Where to get it
===============

Development branches will be on LaunchPad. This is where to go to get the most 
up to date code in the trunk branch. Experimental code will also be hosted here 
in different branches and merged to trunk often.  We try to make sure that the
trunk code is always stable.

https://code.launchpad.net/statsmodels

Source download of stable tags will be on SourceForge.

https://sourceforge.net/projects/statsmodels/

or

PyPi: http://pypi.python.org/pypi/scikits.statsmodels/

License
=======

Simplified BSD

Documentation
=============

The official documentation is hosted on SourceForge.

http://statsmodels.sourceforge.net/

The sphinx docs are currently undergoing a lot of work. They are not yet 
comprehensive, but should get you started.

Our blog will continue to be updated as we make progress on the code.

http://scipystats.blogspot.com


Discussion and Development
==========================

All chatter will take place on the or scipy-user mailing list. We are very 
interested in receiving feedback about usability, suggestions for improvements,
and bug reports via the mailing list or the bug tracker at 
https://bugs.launchpad.net/statsmodels. 

There is also a google group at 

http://groups.google.com/group/pystatsmodels

to discuss development and design issues that are deemed to be too specialized
for the scipy-dev/user list.
