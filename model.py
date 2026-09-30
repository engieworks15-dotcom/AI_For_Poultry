import joblib
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset


class EnvConditionModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(5, 16)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(16, 16)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(16, 3)

    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x


def train_and_evaluate_model():
    torch.manual_seed(42)  # same result every run, so accuracy numbers are comparable
    df = pd.read_csv('coop_environmental_data.csv')
    X = df[['humidity', 'gas_index', 'temperature', 'light', 'fan_rpm']].values
    y = df['status'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    scaler.transform(X_test)
    joblib.dump(scaler, 'sensor_scaler.pkl')

    X_train_tensor = torch.FloatTensor(X_train_scaled)
    y_train_tensor = torch.LongTensor(y_train)
    X_test_tensor = torch.FloatTensor(scaler.transform(X_test))
    y_test_tensor = torch.LongTensor(y_test)

    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    model = EnvConditionModel()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    epochs = 50
    for _ in range(epochs):
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        outputs = model(X_test_tensor)
        _, predicted = torch.max(outputs.data, 1)
        accuracy = (predicted == y_test_tensor).sum().item() / y_test_tensor.size(0)

        # Overfitting check: compare accuracy on data the model trained on vs unseen data
        train_outputs = model(X_train_tensor)
        _, train_predicted = torch.max(train_outputs.data, 1)
        train_accuracy = (train_predicted == y_train_tensor).sum().item() / y_train_tensor.size(0)

    torch.save(model.state_dict(), 'offline_env_model.pth')
    print(f'Train accuracy: {train_accuracy * 100:.2f}%')
    print(f'Test accuracy:  {accuracy * 100:.2f}%')
    print(f'Gap (train - test): {(train_accuracy - accuracy) * 100:+.2f} points')
    print("Saved model and scaler for offline use.")


if __name__ == '__main__':
    train_and_evaluate_model()