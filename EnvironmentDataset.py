import numpy as np
import pandas as pd

np.random.seed(42)
num_samples = 4000
data = []

for _ in range(num_samples):
    # Coop Chamber (Day 1 to 42)
    day = np.random.randint(1, 43)
    week = int(np.ceil(day / 7.0))
    
    ideal_temp = 33.0 - (week - 1) * 2.4
    
    temperature = np.random.normal(ideal_temp, 3.0)
    humidity = np.random.normal(55.0, 12.0)
    ammonia = np.random.exponential(8.0)
    light = np.random.uniform(5.0, 35.0)
    ventilation_rate = np.random.normal(2.0, 0.8)
    
    if ammonia >= 22.0 or abs(temperature - ideal_temp) > 5.0 or humidity < 35.0 or (temperature > 30.0 and humidity > 75.0):
        status = 2
    elif ammonia >= 14.0 or abs(temperature - ideal_temp) > 2.0 or humidity > 68.0 or ventilation_rate < 0.8:
        status = 1
    else:
        status = 0

    data.append([
        day, week, 
        np.round(np.clip(humidity, 10.0, 95.0), 1),
        np.round(np.clip(ammonia, 0.0, 50.0), 1),
        np.round(np.clip(temperature, 10.0, 45.0), 1),
        np.round(np.clip(light, 0.0, 50.0), 1),
        np.round(np.clip(ventilation_rate, 0.05, 5.0), 2),
        status
    ])

# Removed compartment_id from columns
columns = ['day', 'week', 'humidity', 'ammonia', 'temperature', 'light', 'ventilation_rate', 'status']
df = pd.DataFrame(data, columns=columns)
df.to_csv('coop_environmental_data.csv', index=False)
print("[+] Created dataset 'coop_environmental_data.csv' with 4,000 coop records.")