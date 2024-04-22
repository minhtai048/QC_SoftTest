import numpy as np
import json
from flask import Response

# power transformation
def inverse_transform(x, lmbda):
        x_inv = np.zeros_like(x)
        pos = x >= 0

        # when x >= 0
        if abs(lmbda) < np.spacing(1.0):
            x_inv[pos] = np.exp(x[pos]) - 1
        else:  # lmbda != 0
            x_inv[pos] = np.power(x[pos] * lmbda + 1, 1 / lmbda) - 1

        # when x < 0
        if abs(lmbda - 2) > np.spacing(1.0):
            x_inv[~pos] = 1 - np.power(-(2 - lmbda) * x[~pos] + 1, 1 / (2 - lmbda))
        else:  # lmbda == 2
            x_inv[~pos] = 1 - np.exp(-x[~pos])

        return x_inv

# transform categories to integer
def features_transform(features):
    features = features.replace('male', 1)
    features = features.replace('female', 0)
    features = features.replace('yes', 1)
    features = features.replace('no', 0)
    
    features = features.replace('northwest', 0)
    features = features.replace('northeast', 1)
    features = features.replace('southwest', 2)
    features = features.replace('southeast', 3)
    
    return features


def jsonResponse(data):
    '''Return a callable in top of Response'''
    def callable(response=None, *args, **kwargs):
        '''Return a response with JSON data from factory context'''
        return Response(json.dumps(data), *args, **kwargs)
    return callable