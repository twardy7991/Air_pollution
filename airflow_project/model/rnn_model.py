import torch.optim as optim
import numpy as np
import pandas as pd
from datetime import datetime

import torch
import torch.nn as nn
from torch.optim.lr_scheduler import StepLR
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from scipy.stats import norm
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error

class WrongModelDataException(BaseException):
    def __init__(self, message,*args):
        super().__init__(message, *args)

class RNNModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=1):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.rnn = nn.RNN(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True
        )
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        
        rnn_out, h_n = self.rnn(x)
        last_output = rnn_out[:, -1, :]
        output = self.fc(last_output)
        
        return output

def train_model(X : np.ndarray, Y : np.ndarray, model : nn.Module, lr, epochs, step_size, scheduler_gamma, l1, columns, batch_size : int = 32):

    date = datetime.now()
    
    if not isinstance(X, np.ndarray): 
        raise WrongModelDataException("X is not a numpy array")
    elif not isinstance(Y, np.ndarray):
        raise WrongModelDataException("Y is not a numpy array")
    elif not X.shape[0] == Y.shape[0]:
        raise WrongModelDataException("X and Y have different lengths")
        
    scaler_X = StandardScaler()
    scaler_Y = StandardScaler()
    
    x_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_Y.fit_transform(Y)
    
    X_train, X_test, y_train, y_test = train_test_split(x_scaled, y_scaled, test_size=0.3, random_state=10)
    
    batches = []
    losses = []

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    scheduler = StepLR(
        optimizer,
        step_size=step_size,
        gamma = scheduler_gamma
    )

    num_epochs = epochs
    batch_size = batch_size
    l1_lambda = l1

    for epoch in range(num_epochs):
        total_loss = 0
        num_batches = 0
        
        for i in range(0, len(X_train), batch_size):
            batch_X = X_train[i:i+batch_size]
            batch_y = y_train[i:i+batch_size]
            
            predictions = model(batch_X)
            #print("predictions", predictions)
            loss = criterion(predictions, batch_y)
            l1_norm = sum(p.abs().sum() for p in model.parameters())
            loss = loss + l1_lambda * l1_norm
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        scheduler.step()
        
        if (epoch + 1) % 5 == 0:
            # batches.append(num_batches)
            # losses.append(total_loss / num_batches)
            
            avg_loss = total_loss / num_batches
            print(f"Epoch {epoch+1}/{num_epochs}, Loss {avg_loss:.6}")

    predictions = model(X_test).detach().numpy()
    y_actual = y_test.detach().numpy()
    y_actual_unscaled = scaler_Y.inverse_transform(y_actual)
    y_pred_unscaled = scaler_Y.inverse_transform(predictions)
    print("Mean actual:", y_actual_unscaled.mean())
    print("Mean pred:", y_pred_unscaled.mean())
    print("Std actual:", y_actual_unscaled.std())
    print("Std pred:", y_pred_unscaled.std())
    
    mean_squared_error(y_actual_unscaled, y_pred_unscaled)

    plot_difference_distributions(y_pred_unscaled, y_actual_unscaled)

    grads = gradient_importance(X_test[0], model, abs=True)

    features = columns #df.drop(columns=['time', "pm10"]).columns
    
    plot_gradient_importance(features, grads, abs=True, date=date)
    
    grads = gradient_importance(X_test[0], model, abs=False)
    
    plot_gradient_importance(features, grads, abs=False, date=date)

def plot_gradient_importance(features, grads, abs, date):
    plt.figure(figsize=(8,10))

    plt.barh(features, grads)

    plt.xlabel("Gradient importance")
    plt.tight_layout()
    
    if abs:
        plt.savefig(f"model/training/graident_importance_abs_{date}.png")
    else:
        plt.savefig(f"model/training/graident_importance_{date}.png")
        
    return 0

def gradient_importance(seq, model, abs : bool = False):
    model.eval()

    seq = torch.tensor(seq[np.newaxis, :, :], dtype=torch.float32, requires_grad=True)

    predictions = model(seq)

    predictions.backward(torch.ones_like(predictions))

    grads = seq.grad
    
    if abs:
        grads = torch.abs(seq.grad).mean(dim=1).detach().numpy()[0]
    else:
        grads = grads.mean(dim=1).detach().numpy()[0]

    return grads

def plot_difference_distributions(y_pred_unscaled, y_actual_unscaled, date):
    df_pred = pd.DataFrame(np.concatenate((y_pred_unscaled, y_actual_unscaled), axis=1), columns=["pred", "actual"])
    df_pred["diff"] = df_pred["actual"] - df_pred["pred"]

    data = df_pred["diff"]

    mu = np.mean(data)
    sigma = np.std(data)
    x = np.linspace(min(data), max(data), 200)
    y = norm.pdf(x, mu, sigma)

    plt.axvline(mu)
    plt.axvline(mu-sigma, c="r")
    plt.axvline(mu+sigma, c="r")
    plt.hist(data, bins=25, density=True, alpha=0.6)
    plt.xlabel("Value")
    plt.ylabel("Probability")
    plt.title("Distribution")
    plt.plot(x, y)
    
    plt.savefig(f"model/training/difference_distributions_{date}.png")