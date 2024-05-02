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

# validate input from client
def validate_input(features):
    if (features.age[0] <= 1 or features.age[0] >= 99):
        return -1
    if (features.bmi[0] <= 0 or features.bmi[0] >= 99):
        return -1
    if (features.children[0] <= 0):
        return -1

# predict result from client's input
## scaler: scaler to scale features
## model: model to predict
## lmbda: decode the encoded result
def predict_(features, scaler, model, lmbda):
    features = features_transform(features)  
    features = scaler.transform(features)   
    prediction = model.predict(features)
    prediction = inverse_transform(prediction, lmbda)
    prediction = np.round_(prediction, 2)[0]
    return prediction