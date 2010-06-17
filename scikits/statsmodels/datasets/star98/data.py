# -*- coding: utf-8 -*-
# Last Change: Wed Jun 24 06:00 PM 2009 J

# The code and descriptive text is copyrighted and offered under the terms of
# the BSD License from the authors; see below. However, the actual dataset may
# have a different origin and intellectual property status. See the SOURCE and
# COPYRIGHT variables for this information.

# Copyright (c) 2007 David Cournapeau <cournape@gmail.com>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     * Neither the author nor the names of any contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__all__ = ['COPYRIGHT','TITLE','SOURCE','DESCRSHORT','DESCRLONG','NOTE', 'load']

"""Star98 Educational Testing dataset."""

__docformat__ = 'restructuredtext'

COPYRIGHT   = """Used with expressed permission from the original author,
who retains all rights."""
TITLE       = "Star98 Educational Dataset"
SOURCE      = """
Jeff Gill's `Generalized Linear Models: A Unifited Approach`

http://jgill.wustl.edu/research/books.html
"""
DESCRSHORT  = """Math scores for 303 student with 10 explanatory factors"""

DESCRLONG   = """
This data is on the California education policy and outcomes (STAR program
results for 1998.  The data measured standardized testing by the California
Department of Education that required evaluation of 2nd - 11th grade students
by the the Stanford 9 test on a variety of subjects.  This dataset is at
the level of the unified school district and consists of 303 cases.  The
binary response variable represents the number of 9th graders scoring
over the national median value on the mathematics exam.

The original source files and information are included in /star98/src/

The data used in this example is only a subset of the original source.
"""

NOTE        = """
Number of Observations: 303 (counties in California).
Number of Variables: 13 and 8 interaction terms.
Definition of variables names:
    NABOVE - Total number of students above the national median for the math
        section.
    NBELOW - Total number of students below the national median for the math
        section.
    LOWINC - Percentage of low income students
    PERASIAN - Percentage of Asian student
    PERBLACK - Percentage of black students
    PERHISP - Percentage of Hispanic students
    PERMINTE - Percentage of minority teachers
    AVYRSEXP - Sum of teachers' years in educational service divided by the
        number of teachers.
    AVSALK - Total salary budget including benefits divided by the number of
        full-time teachers (in thousands)
    PERSPENK - Per-pupil spending (in thousands)
    PTRATIO - Pupil-teacher ratio.
    PCTAF - Percentage of students taking UC/CSU prep courses
    PCTCHRT - Percentage of charter schools
    PCTYRRND - Percentage of year-round schools

    The below variables are interaction terms of the variables defined above.

    PERMINTE_AVYRSEXP
    PEMINTE_AVSAL
    AVYRSEXP_AVSAL
    PERSPEN_PTRATIO
    PERSPEN_PCTAF
    PTRATIO_PCTAF
    PERMINTE_AVTRSEXP_AVSAL
    PERSPEN_PTRATIO_PCTAF
"""

from numpy import recfromtxt, column_stack, array
from scikits.statsmodels.datasets import Dataset
from os.path import dirname, abspath

def load():
    """
    Load the star98 data and returns a Dataset class instance.

    Returns
    -------
    Load instance:
        a class of the data with array attrbutes 'endog' and 'exog'
    """
    filepath = dirname(abspath(__file__))
##### EDIT THE FOLLOWING TO POINT TO DatasetName.csv #####
    names = ["NABOVE","NBELOW","LOWINC","PERASIAN","PERBLACK","PERHISP",
            "PERMINTE","AVYRSEXP","AVSALK","PERSPENK","PTRATIO","PCTAF",
            "PCTCHRT","PCTYRRND","PERMINTE_AVYRSEXP","PERMINTE_AVSAL",
            "AVYRSEXP_AVSAL","PERSPEN_PTRATIO","PERSPEN_PCTAF","PTRATIO_PCTAF",
            "PERMINTE_AVYRSEXP_AVSAL","PERSPEN_PTRATIO_PCTAF"]
    data = recfromtxt(filepath + '/star98.csv', delimiter=",",
            names=names, skip_header=1, dtype=float)
    names = list(data.dtype.names)
    # endog = (successes, failures)
    NABOVE = array(data[names[1]]).astype(float) # successes
    NBELOW = array(data[names[0]]).astype(float) \
                - array(data[names[1]]).astype(float) # now its failures
    endog = column_stack((NABOVE,NBELOW))
    endog_name = names[:2]
    exog = column_stack(data[i] for i in names[2:]).astype(float)
    exog_name = names[2:]
    dataset = Dataset(data=data, names=names, endog=endog, exog=exog,
            endog_name = endog_name, exog_name=exog_name)
    return dataset
