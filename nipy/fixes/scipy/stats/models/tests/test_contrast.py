import numpy as np
import numpy.random as R
from numpy.testing import *
from models.contrast import Contrast

class TestContrast(object):
    def __init__(self):
        R.seed(54321)
        self.X = R.standard_normal((40,10))

    def TestContrast1(self):
        term = np.column_stack((self.X[:,0], self.X[:,2]))
        c = Contrast(term, self.X)
        test_contrast = [[1] + [0]*9, [0]*2 + [1] + [0]*7]
        assert_almost_equal(test_contrast, c.contrast_matrix)

    def TestContrast2(self):
        zero = np.zeros((40,))
        term = np.column_stack((zero, self.X[:,2]))
        c = Contrast(term, self.X)
        test_contrast = [0]*2 + [1] + [0]*7
        assert_almost_equal(test_contrast, c.contrast_matrix)

    def TestContrast3(self):
        P = np.dot(self.X, np.linalg.pinv(self.X))
        resid = np.identity(40) - P
        noise = np.dot(resid,R.standard_normal((40,5)))
        term = np.column_stack((noise, self.X[:,2]))
        c = Contrast(term, self.X)
        assert_equal(c.contrast_matrix.shape, (10,))
#TODO: this should actually test the value of the contrast, not only its dimension

    def TestEstimable(self):
        X2 = np.column_stack((self.X, self.X[:,5]))
        c = Contrast(self.X[:,5],X2)
        #TODO: I don't think this should be estimable?  isestimable correct?


if __name__=="__main__":
    run_module_suite()

