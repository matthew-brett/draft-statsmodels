"""
This should be merged into statsmodels/tests/model_results.py when things
move out of the sandbox.
"""
import numpy as np

class Anes():
    def __init__(self):
        """
        Results are from Stata 11 (checked vs R nnet package).
        """
        self.nobs = 944

    def mnlogit_basezero(self):
        params = [-.01153598, .29771435, -.024945, .08249144, .00519655,
                -.37340167, -.08875065, .39166864, -.02289784, .18104276,
                .04787398, -2.2509132, -.1059667, .57345051, -.01485121,
                -.00715242, .05757516, -3.6655835, -.0915567, 1.2787718,
                -.00868135, .19982796, .08449838, -7.6138431, -.0932846,
                1.3469616, -.01790407, .21693885, .08095841, -7.0604782,
                -.14088069, 2.0700801, -.00943265, .3219257, .10889408,
                -12.105751]
        self.params = np.reshape(params, (6,-1))
        bse = [.0342823657, .093626795, .0065248584, .0735865799,
                .0176336937, .6298376313, .0391615553, .1082386919,
                .0079144618, .0852893563, .0222809297, .7631899491,
                .0570382292, .1585481337, .0113313133, .1262913234,
                .0336142088, 1.156541492, .0437902764, .1288965854,
                .0084187486, .0941250559, .0261963632, .9575809602,
                .0393516553, .1171860107, .0076110152, .0850070091,
                .0229760791, .8443638283, .042138047, .1434089089,
                .0081338625, .0910979921, .025300888, 1.059954821]
        self.bse = np.reshape(bse, (6,-1))
        self.cov_params = None
        self.llf = -1461.922747312
        self.llnull = -1750.34670999
        self.llr = 576.8479253554
        self.llr_pvalue = 1.8223179e-102
        self.prsquared = .1647810465387
        self.df_model = 30
        self.df_resid = 944 - 36
        self.J = 7
        self.K = 6
        self.aic = 2995.84549462
        self.bic = 3170.45003661


class Spector():
    """
    Results are from Stata 11
    """
    def __init__(self):
        self.nobs = 32

    def logit(self):
        self.params = [2.82611297201, .0951576702557, 2.37868772835,
                -13.0213483201]
        self.cov_params = [[1.59502033639, -.036920566629, .427615725153,
                -4.57347950298], [-.036920566629, .0200375937069,
                .0149126464275, -.346255757562], [.427615725153 ,
                .0149126464275, 1.13329715236, -2.35916128427],
                [-4.57347950298, -.346255757562, -2.35916128427,
                24.3179625937]]
        self.bse = [1.26294114526, .141554207662, 1.06456430165, 4.93132462871]
        self.llf = -12.8896334653335
        self.llnull = -20.5917296966173
        self.df_model = 3
        self.df_resid = 32 - 4  #TODO: is this right? not reported in stata
        self.llr = 15.4041924625676
        self.prsquared = .374038332124624
        self.llr_pvalue = .00150187761112892
        self.aic = 33.779266930667
        self.bic = 39.642210541866

    def probit(self):
        self.params = [1.62581025407, .051728948442, 1.42633236818,
                -7.45232041607]
        self.cov_params =    [[.481472955383, -.01891350017, .105439226234,
            -1.1696681354], [-.01891350017, .00703757594, .002471864882,
            -.101172838897], [.105439226234, .002471864882, .354070126802,
            -.594791776765], [-1.1696681354, -.101172838897, -.594791776765,
            6.46416639958]]
        self.bse = [.693882522754, .083890261293, .595037920474, 2.54247249731]
        self.llf = -12.8188033249334
        self.llnull = -20.5917296966173
        self.df_model = 3
        self.df_resid = 32 - 4
        self.llr = 15.5458527433678
        self.prsquared = .377478069409622
        self.llr_pvalue = .00140489496775855
        self.aic = 33.637606649867
        self.bic = 39.500550261066
