import copy

import numpy as np
from numpy.linalg import pinv
from models import utils

class ContrastResults(object):
    """
    Results from looking at a particular contrast of coefficients in
    a parametric model. The class does nothing, it is a container
    for the results from T and F contrasts.
    """

    #JP: what is this class supposed to be, just a container for a few numbers?

    def __init__(self, t=None, F=None, sd=None, effect=None, df_denom=None,
                 df_num=None):
        if F is not None:
            self.F = F
            self.df_denom = df_denom
            self.df_num = df_num
        else:
            self.t = t
            self.sd = sd
            self.effect = effect
            self.df_denom = df_denom

    def __array__(self):
        if hasattr(self, "F"):
            return self.F
        else:
            return self.t

    def __str__(self):
        if hasattr(self, 'F'):
            return '<F contrast: F=%s, df_denom=%d, df_num=%d>' % \
                   (`self.F`, self.df_denom, self.df_num)
        else:
            return '<T contrast: effect=%s, sd=%s, t=%s, df_denom=%d>' % \
                   (`self.effect`, `self.sd`, `self.t`, self.df_denom)


class Contrast(object):
    """
    This class is used to construct contrast matrices in regression models.
    They are specified by a (term, formula) pair.

    The term, T,  is a linear combination of columns of the design
    matrix D=formula(). The matrix attribute is
    a contrast matrix C so that

    colspan(dot(D, C)) = colspan(dot(D, dot(pinv(D), T)))

    where pinv(D) is the generalized inverse of D. Further, the matrix

    Tnew = dot(C, D)

    is full rank. The rank attribute is the rank of

    dot(D, dot(pinv(D), T))

    In a regression model, the contrast tests that E(dot(Tnew, Y)) = 0
    for each column of Tnew.

    """

    def __init__(self, term, formula, name=''):
        self.term = term
        self.formula = formula
        if name is '':
            self.name = str(term)
        else:
            self.name = name

    def __str__(self):
        return '<contrast:%s>' % \
               `{'term':str(self.term), 'formula':str(self.formula)}`

    def compute_matrix(self, *args, **kw):
        """
        Construct a contrast matrix C so that

        colspan(dot(D, C)) = colspan(dot(D, dot(pinv(D), T)))

        where pinv(D) is the generalized inverse of D=self.D=self.formula().

        If the design, self.D is already set,
        then evaldesign can be set to False.
        """

        t = copy.copy(self.term)
        t.namespace = self.formula.namespace
        T = np.transpose(np.array(t(*args, **kw)))  # T is column ordered
                                                    # groups from a design

        if T.ndim == 1:
            T.shape = (T.shape[0], 1)

        self.T = utils.clean0(T)

        self.D = self.formula.design(*args, **kw)   # D is the whole design
                                                    # groups in columns

        self._matrix = contrastfromcols(self.T, self.D)
        try:
            self.rank = self.matrix.shape[1]
        except:
            self.rank = 1

    def _get_matrix(self):
        """
        This will fail if the formula needs arguments to construct
        the design.
        """
        if not hasattr(self, "_matrix"):
            self.compute_matrix()
        return self._matrix
    matrix = property(_get_matrix)

def contrastfromcols(L, D, pseudo=None):
    """
    From an n x p design matrix D and a matrix L, tries
    to determine a p x q contrast matrix C which
    determines a contrast of full rank, i.e. the
    n x q matrix

    dot(transpose(C), pinv(D))

    is full rank.

    L must satisfy either L.shape[0] == n or L.shape[1] == p.

    If L.shape[0] == n, then L is thought of as representing
    columns in the column space of D.

    If L.shape[1] == p, then L is thought of as what is known
    as a contrast matrix. In this case, this function returns an estimable
    contrast corresponding to the dot(D, L.T)

    Note that this always produces a meaningful contrast, not always
    with the intended properties because q is always non-zero unless
    L is identically 0. That is, it produces a contrast that spans
    the column space of L (after projection onto the column space of D).

    """

    L = np.asarray(L)
    D = np.asarray(D)

    n, p = D.shape

    if L.shape[0] != n and L.shape[1] != p:
        raise ValueError, 'shape of L and D mismatched'

    if pseudo is None:
        pseudo = pinv(D)    # D^+ \approx= ((dot(D.T,D))^(-1),D.T)

    if L.shape[0] == n:
        C = np.dot(pseudo, L).T
    else:
        C = L
        C = np.dot(pseudo, np.dot(D, C.T)).T

    Lp = np.dot(D, C.T) # why compute this here if only used in if below?

    if len(Lp.shape) == 1:
        Lp.shape = (n, 1)

    if utils.rank(Lp) != Lp.shape[1]:
        Lp = utils.fullrank(Lp)
        C = np.dot(pseudo, Lp).T

    return np.squeeze(C)

if __name__=="__main__":

### Some ANOVA examples
### A matrix of treatment groups of 5 in rows.
    data = np.array(([6.9, 5.4, 5.8, 4.6, 4.0],
                     [8.3, 6.8, 7.8, 9.2, 6.5],
                     [8.0, 10.5, 8.1, 6.9, 9.3],
                     [5.8, 3.8, 6.1, 5.6, 6.2]))

    error_ss = 0
    for i in range(len(data)):
        error_ss += np.sum((data[i]-data.mean(1)[i])**2)

    total_ss = 0
    for i in range(len(data)):
        total_ss += np.sum((data[i]-data.mean())**2)

    treatment_ss = np.sum(data.shape[1]*(data.mean(1)-data.mean())**2)
# if all samples have the same size you can use shape

#    c_hat =

########
# Contrast class
## Set Up ##
    import numpy.random as R
    import formula
    import string
    R.seed(54321)
    X = R.standard_normal((40,10))
    namespace = {}
    terms = []
    for i in range(10):
        name = "%s" % string.uppercase[i]
        namespace[name] = X[:,i]
        terms.append(formula.Term(name))

    form = terms[0]
    for i in range(1, 10):
        form += terms[i]
    form.namespace = namespace

## Get a contrast ##

    new_term = terms[0] + terms[2]
    c = Contrast(new_term, form)
    test = [[1] + [0]*9, [0]*2 + [1] + [0]*7]
# this is c, the contrast
#    1 0 0 0 0 0 0 0 0 0
#    0 0 1 0 0 0 0 0 0 0


    X2 = form.design()
    P = np.dot(X2, np.linalg.pinv(X2))
    dummy = formula.Term('noise')
    resid = np.identity(40) - P
    namespace['noise'] = np.transpose(np.dot(resid,R.standard_normal((40,5))))
    new_term2 = dummy + terms[2]
    new_term2.namespace = form.namespace
    c2 = Contrast(new_term2, form)
# Is this correct?  0 0 .156 0 0 0 0 0 0 0 ?







