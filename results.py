import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import torch
import torch.nn as nn
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

sns.set_theme(style='whitegrid')
plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 18,
    'axes.labelsize': 14,
    'legend.fontsize': 12,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'figure.facecolor': 'white',
    'axes.facecolor': '#f5f5f5',
    'axes.edgecolor': '#333333',
    'grid.color': '#d7d7d7',
    'grid.linewidth': 0.8,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})


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


def load_model_data():
    df = pd.read_csv('coop_environmental_data.csv')
    X = df[['humidity', 'gas_index', 'temperature', 'light', 'fan_rpm']].values
    y = df['status'].values

    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = joblib.load('sensor_scaler.pkl')
    X_test_scaled = scaler.transform(X_test)

    return X_test, y_test, X_test_scaled


def evaluate_model(X_test, y_test, X_test_scaled):
    X_test_tensor = torch.FloatTensor(X_test_scaled)
    y_test_tensor = torch.LongTensor(y_test)

    model = EnvConditionModel()
    model.load_state_dict(torch.load('offline_env_model.pth'))
    model.eval()

    with torch.no_grad():
        outputs = model(X_test_tensor)
        _, predicted = torch.max(outputs.data, 1)
        criterion_none = nn.CrossEntropyLoss(reduction='none')
        sample_losses = criterion_none(outputs, y_test_tensor).numpy()

    return predicted.numpy(), sample_losses


def plot_confusion_matrix(preds, y_test):
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='white')
    cm = confusion_matrix(y_test, preds)
    status_labels = ['Healthy', 'Warning', 'Critical']

    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        cbar=False,
        linewidths=1.2,
        linecolor='white',
        annot_kws={'size': 14},
        ax=ax,
    )
    ax.set_title('1. How often the model was right', pad=18)
    ax.set_xlabel('Predicted Condition', labelpad=10)
    ax.set_ylabel('Actual Condition', labelpad=10)
    ax.set_xticklabels(status_labels)
    ax.set_yticklabels(status_labels)
    plt.tight_layout()
    plt.savefig('1_predicted_vs_actual.png', dpi=300)
    plt.close(fig)


def plot_pca_cloud(X_test_scaled, preds):
    pca3 = PCA(n_components=3)
    X_pca3 = pca3.fit_transform(X_test_scaled)

    fig = plt.figure(figsize=(10, 7), facecolor='white')
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(
        X_pca3[:, 0],
        X_pca3[:, 1],
        X_pca3[:, 2],
        c=preds,
        cmap='viridis',
        s=45,
        alpha=0.8,
        edgecolors='k',
        linewidth=0.4,
    )
    ax.set_title('2. How the sensor readings group together', pad=20)
    ax.set_xlabel('Pattern 1', labelpad=15)
    ax.set_ylabel('Pattern 2', labelpad=15)
    ax.set_zlabel('Pattern 3', labelpad=15)
    ax.view_init(elev=24, azim=45)
    colorbar = plt.colorbar(sc, ax=ax, pad=0.08, shrink=0.9)
    colorbar.set_label('Predicted Condition', rotation=270, labelpad=18)
    plt.tight_layout()
    plt.savefig('2_sensor_3d_cloud.png', dpi=300)
    plt.close(fig)


def plot_sensor_scatter(X_test, y_test):
    fig, ax = plt.subplots(figsize=(9, 6), facecolor='white')
    status_labels = ['Healthy', 'Warning', 'Critical']
    scatter = ax.scatter(
        X_test[:, 2],
        X_test[:, 0],
        c=y_test,
        cmap='viridis',
        alpha=0.75,
        edgecolors='k',
        linewidth=0.3,
        s=45,
    )
    ax.set_title('3. Temperature and humidity by condition', pad=18)
    ax.set_xlabel('Temperature (°C)', labelpad=10)
    ax.set_ylabel('Humidity (%)', labelpad=10)
    ax.grid(True, alpha=0.35)
    colorbar = plt.colorbar(scatter, ax=ax, pad=0.05)
    colorbar.set_ticks([0, 1, 2])
    colorbar.set_ticklabels(status_labels)
    colorbar.set_label('Actual Condition', rotation=270, labelpad=18)
    plt.tight_layout()
    plt.savefig('3_sensor_scatterplot.png', dpi=300)
    plt.close(fig)


def plot_loss(sample_losses):
    fig, ax = plt.subplots(figsize=(10, 5), facecolor='white')
    ax.scatter(range(len(sample_losses)), sample_losses, color='#e84a5f', alpha=0.75, s=30, edgecolors='k', linewidth=0.15)
    ax.axhline(
        y=sample_losses.mean(),
        color='black',
        linestyle='--',
        linewidth=2,
        label=f'Average error: {sample_losses.mean():.4f}',
    )
    ax.set_title('4. How confident the model was on each test sample', pad=18)
    ax.set_xlabel('Test sample', labelpad=10)
    ax.set_ylabel('Prediction error', labelpad=10)
    ax.grid(True, alpha=0.35)
    ax.legend(frameon=True, fancybox=True, framealpha=0.9)
    plt.tight_layout()
    plt.savefig('4_loss_deviation.png', dpi=300)
    plt.close(fig)


def main():
    print('Loading data and model...')
    X_test, y_test, X_test_scaled = load_model_data()
    preds, sample_losses = evaluate_model(X_test, y_test, X_test_scaled)

    print('Generating chart 1...')
    plot_confusion_matrix(preds, y_test)

    print('Generating chart 2...')
    plot_pca_cloud(X_test_scaled, preds)

    print('Generating chart 3...')
    plot_sensor_scatter(X_test, y_test)

    print('Generating chart 4...')
    plot_loss(sample_losses)

    print('Done! All 4 presentation charts have been saved to the current directory.')


if __name__ == '__main__':
    main()
