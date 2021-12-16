import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

from models.basemodel import BaseModel

from utils.io_utils import get_output_path


class MLP(BaseModel, nn.Module):

    def __init__(self, params, args):
        BaseModel.__init__(self, params, args)
        nn.Module.__init__(self)

        input_dim = self.args.num_features
        hidden_dim = self.params["hidden_dim"]
        output_dim = self.args.num_classes  # 1 for regression and for binary

        self.layers = nn.ModuleList()

        # Input Layer (= first hidden layer)
        self.input_layer = nn.Linear(input_dim, hidden_dim)

        # Hidden Layers (number specified by n_layers)
        self.layers.extend([nn.Linear(hidden_dim, hidden_dim) for _ in range(self.params["n_layers"] - 1)])

        # Output Layer
        self.output_layer = nn.Linear(hidden_dim, output_dim)

        self.device = torch.device('cuda' if args.use_gpu and torch.cuda.is_available() else 'cpu')
        # print("On Device:", self.device)
        self.to(self.device)

    def forward(self, x):
        x = F.relu(self.input_layer(x))

        # Use ReLU as activation for all hidden layers
        for layer in self.layers:
            x = F.relu(layer(x))

        # No activation function on the output
        x = self.output_layer(x)

        if self.args.objective == "classification":
            x = F.softmax(x, dim=1)

        return x

    def fit(self, X, y, X_val=None, y_val=None):
        optimizer = optim.AdamW(self.parameters(), lr=self.params["learning_rate"])

        # For some reason this has to be set explicitly to work with categorical data
        X = np.array(X, dtype=np.float)
        X_val = np.array(X_val, dtype=np.float)

        X = torch.tensor(X).float()
        X_val = torch.tensor(X_val).float()

        y = torch.tensor(y)
        y_val = torch.tensor(y_val)

        if self.args.objective == "regression":
            loss_func = nn.MSELoss()
            y = y.float()
            y_val = y_val.float()
        elif self.args.objective == "classification":
            loss_func = nn.CrossEntropyLoss()
        else:
            loss_func = nn.BCEWithLogitsLoss()
            y = y.float()
            y_val = y_val.float()

        train_dataset = TensorDataset(X, y)
        train_loader = DataLoader(dataset=train_dataset, batch_size=self.params["batch_size"], shuffle=True,
                                  num_workers=2)

        val_dataset = TensorDataset(X_val, y_val)
        val_loader = DataLoader(dataset=val_dataset, batch_size=self.params["batch_size"], shuffle=True)

        min_val_loss = float("inf")
        min_val_loss_idx = 0

        for epoch in range(self.args.epochs):
            for i, (batch_X, batch_y) in enumerate(train_loader):

                out = self.forward(batch_X.to(self.device))

                if self.args.objective == "regression" or self.args.objective == "binary":
                    out = out.squeeze()

                loss = loss_func(out, batch_y.to(self.device))

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                # Early Stopping
                val_loss = 0.0
                val_dim = 0
                for val_i, (batch_val_X, batch_val_y) in enumerate(val_loader):
                    out = self.forward(batch_val_X.to(self.device))

                    if self.args.objective == "regression" or self.args.objective == "binary":
                        out = out.squeeze()

                    val_loss += loss_func(out, batch_val_y.to(self.device))
                    val_dim += 1
                val_loss /= val_dim

                current_idx = (i + 1) * (epoch + 1)

                print("Epoch %d, step % i, Loss: %.5f, Val Loss: %.5f" % (epoch, i, loss, val_loss))

                if val_loss < min_val_loss:
                    min_val_loss = val_loss
                    min_val_loss_idx = current_idx

                    # Save the currently best model
                    self.save_model(filename_extension="best", directory="tmp")

                if min_val_loss_idx + self.args.early_stopping_rounds < current_idx:
                    # print("Validation loss has not improved for %d steps!" % self.args.early_stopping_rounds)
                    # print("Early stopping applies.")
                    return

    def predict(self, X):

        self.load_model(filename_extension="best", directory="tmp")
        self.eval()

        # For some reason this has to be set explicitly to work with categorical data
        X = np.array(X, dtype=np.float)

        X = torch.tensor(X).float()
        test_dataset = TensorDataset(X)
        test_loader = DataLoader(dataset=test_dataset, batch_size=self.params["batch_size"], shuffle=True,
                                 num_workers=2)

        self.predictions = []
        with torch.no_grad():
            for batch_X in test_loader:
                preds = self.forward(batch_X[0].to(self.device))

                if self.args.objective == "binary":
                    preds = torch.sigmoid(preds)

                self.predictions.append(preds.detach().cpu().numpy())

        self.predictions = np.concatenate(self.predictions)
        return self.predictions

    def save_model(self, filename_extension="", directory="models"):
        filename = get_output_path(self.args, directory=directory, filename="m", extension=filename_extension,
                                   file_type="pt")
        torch.save(self.state_dict(), filename)

    def load_model(self, filename_extension="", directory="models"):
        filename = get_output_path(self.args, directory=directory, filename="m", extension=filename_extension,
                                   file_type="pt")
        state_dict = torch.load(filename)
        self.load_state_dict(state_dict)

    @classmethod
    def define_trial_parameters(cls, trial, args):
        params = {
            "hidden_dim": trial.suggest_int("hidden_dim", 10, 100),
            "n_layers": trial.suggest_int("n_layers", 2, 5),
            "learning_rate": trial.suggest_float("learning_rate", 0.0005, 0.001),
            "batch_size": trial.suggest_categorical("batch_size", [64, 128, 256, 512])
        }
        return params
