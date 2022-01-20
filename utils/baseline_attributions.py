from tkinter.tix import X_REGION
import captum
import numpy as np
from models.basemodel import BaseModel
import shap

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

def get_probabilistic_predictions(model: BaseModel, X: np.ndarray):
    """ Return output probabilities as a single vector. """
    ypred = model.predict(X)
    if len(ypred.shape)==2:
        ypred = ypred[:,-1]
    return ypred

def get_shap_attributions(model: BaseModel, X: np.ndarray, y: np.ndarray):
    """ Return local shap attributions for the data. """
    f = lambda x: get_probabilistic_predictions(model, x)
    kernelshap = shap.KernelExplainer(f, X)
    shap_values = kernelshap.shap_values(X, nsamples = 1000)  # nsamples = no. of feature coalitions
    print(shap_values.shape, shap_values.dtype)
    return shap_values

