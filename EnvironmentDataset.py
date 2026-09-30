import numpy as np
import pandas as pd


np.random.seed(42)
NUM_SAMPLES = 12000
TARGET_TEMP = 26.0
MAX_RPM = 2500.0
STATUS_LABELS = {
    0: 'Healthy',
    1: 'Warning',
    2: 'Critical',
}


def generate_dataset():
    data = []

    for _ in range(NUM_SAMPLES):
        fan_rpm = np.clip(np.random.normal(1250.0, 500.0), 0.0, MAX_RPM)
        airflow = fan_rpm / 625.0

        temperature = np.random.normal(TARGET_TEMP, 3.0)
        humidity = np.random.normal(55.0, 12.0)
        light = np.random.uniform(5.0, 35.0)
        gas_index = np.random.exponential(8.0) * np.clip(2.0 / max(airflow, 0.5), 0.5, 2.5)

        deviation = abs(temperature - TARGET_TEMP)

        if gas_index >= 22.0 or deviation > 5.0 or humidity < 35.0 or (temperature > 30.0 and humidity > 75.0):
            status = 2
        elif gas_index >= 14.0 or deviation > 2.0 or humidity > 68.0 or fan_rpm < 500.0:
            status = 1
        else:
            status = 0

        data.append([
            np.round(np.clip(humidity, 10.0, 95.0), 1),
            np.round(np.clip(gas_index, 0.0, 50.0), 1),
            np.round(np.clip(temperature, 10.0, 45.0), 1),
            np.round(np.clip(light, 0.0, 50.0), 1),
            np.round(fan_rpm, 0),
            status,
        ])

    columns = ['humidity', 'gas_index', 'temperature', 'light', 'fan_rpm', 'status']
    df = pd.DataFrame(data, columns=columns)
    return df


def summarize_statuses(df):
    counts = df['status'].value_counts().sort_index()
    for status_code, label in STATUS_LABELS.items():
        count = int(counts.get(status_code, 0))
        print(f'{label}: {count}')


def main():
    df = generate_dataset()
    df.to_csv('coop_environmental_data.csv', index=False)
    summarize_statuses(df)
    print(f"Dataset created: {len(df)} records saved to 'coop_environmental_data.csv'.")


if __name__ == '__main__':
    main()