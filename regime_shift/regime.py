import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor

class RegimeIdentifier(object):
    """docstring for RegimeIdentifier"""
    def __init__(self, arg):
        super(RegimeIdentifier, self).__init__()
        self.arg = arg
        