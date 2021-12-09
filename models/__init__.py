def str2model(model):

    if model == "LinearModel":
        from models.baseline_models import LinearModel
        return LinearModel

    elif model == "KNN":
        from models.baseline_models import KNN
        return KNN

    elif model == "SVM":
        from models.baseline_models import SVM
        return SVM

    elif model == "DecisionTree":
        from models.baseline_models import DecisionTree
        return DecisionTree

    elif model == "RandomForest":
        from models.baseline_models import RandomForest
        return RandomForest

    elif model == "XGBoost":
        from models.tree_models import XGBoost
        return XGBoost

    elif model == "CatBoost":
        from models.tree_models import CatBoost
        return CatBoost

    elif model == "LightGBM":
        from models.tree_models import LightGBM
        return LightGBM

    elif model == "MLP":
        from models.mlp import MLP
        return MLP

    elif model == "ModelTree":
        from models.modeltree import ModelTree
        return ModelTree

    elif model == "TabNet":
        from models.tabnet import TabNet
        return TabNet

    elif model == "VIME":
        from models.vime import VIME
        return VIME

    elif model == "TabTransformer":
        from models.tabtransformer import TabTransformer
        return TabTransformer

    elif model == "NODE":
        from models.node import NODE
        return NODE

    elif model == "DeepGBM":
        from models.deepgbm import DeepGBM
        return DeepGBM

    elif model == "RLN":
        from models.rln import RLN
        return RLN

    elif model == "DNFNet":
        from models.dnf import DNFNet
        return DNFNet

    elif model == "STG":
        from models.stochastic_gates import STG
        return STG

    else:
        raise NotImplementedError("Model \"" + model + "\" not yet implemented")
