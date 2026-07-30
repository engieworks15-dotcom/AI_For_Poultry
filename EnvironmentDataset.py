import numpy as np
import pandas as pd

np.random.seed(42)
num_samples = 3600  # 1200 samples per compartment

data = []

for _ in range(num_samples):
    comp = np.random.choice([0, 1, 2]) # 0: Incubator, 1: Hatchery, 2: Coop
    
    # -------------------------------------------------------------
    # COMPARTMENT 0: INCUBATOR (Setter stage)
    # -------------------------------------------------------------
    if comp == 0:
        week = 0 # Pre-hatch phase
        temperature = np.random.normal(37.5, 1.2)
        humidity = np.random.normal(53.0, 7.0)
        ammonia = np.random.exponential(2.5)
        light = np.random.uniform(0.0, 10.0)
        ventilation_rate = np.random.normal(0.35, 0.20)
        
        temp_err = abs(temperature - 37.5)
        if temp_err > 2.0 or humidity < 40.0 or humidity > 70.0 or ammonia >= 8.0 or ventilation_rate < 0.05:
            status = 2 # Danger
        elif temp_err > 0.8 or humidity < 48.0 or humidity > 58.0 or ammonia >= 4.0 or ventilation_rate < 0.15:
            status = 1 # Warning
        else:
            status = 0 # Normal

    # -------------------------------------------------------------
    # COMPARTMENT 1: HATCHERY (Hatcher stage)
    # -------------------------------------------------------------
    elif comp == 1:
        week = 0 # Pre-hatch phase
        temperature = np.random.normal(36.8, 1.2)
        humidity = np.random.normal(70.0, 7.0)
        ammonia = np.random.exponential(4.0)
        light = np.random.uniform(0.0, 15.0)
        ventilation_rate = np.random.normal(1.0, 0.35)
        
        temp_err = abs(temperature - 36.8)
        if temp_err > 2.0 or humidity < 50.0 or humidity > 85.0 or ammonia >= 12.0 or ventilation_rate < 0.2:
            status = 2 # Danger
        elif temp_err > 0.8 or humidity < 62.0 or humidity > 78.0 or ammonia >= 7.0 or ventilation_rate < 0.5:
            status = 1 # Warning
        else:
            status = 0 # Normal

    # -------------------------------------------------------------
    # COMPARTMENT 2: COOP (Brooding & Rearing stage)
    # -------------------------------------------------------------
    else:
        week = np.random.randint(1, 7) # Weeks 1 to 6
        ideal_temp = 33.0 - (week - 1) * 2.4
        
        temperature = np.random.normal(ideal_temp, 3.0)
        humidity = np.random.normal(55.0, 12.0)
        ammonia = np.random.exponential(8.0)
        light = np.random.uniform(5.0, 35.0)
        ventilation_rate = np.random.normal(2.0, 0.8)
        
        if ammonia >= 22.0 or abs(temperature - ideal_temp) > 5.0 or humidity < 35.0 or (temperature > 30.0 and humidity > 75.0):
            status = 2 # Danger
        elif ammonia >= 14.0 or abs(temperature - ideal_temp) > 2.0 or humidity > 68.0 or ventilation_rate < 0.8:
            status = 1 # Warning
        else:
            status = 0 # Normal

    # Append clipped physically realistic values
    data.append([
        comp,
        week,
        np.round(np.clip(humidity, 10.0, 95.0), 1),
        np.round(np.clip(ammonia, 0.0, 50.0), 1),
        np.round(np.clip(temperature, 10.0, 45.0), 1),
        np.round(np.clip(light, 0.0, 50.0), 1),
        np.round(np.clip(ventilation_rate, 0.05, 5.0), 2),
        status
    ])

# Export CSV
columns = ['compartment_id', 'week', 'humidity', 'ammonia', 'temperature', 'light', 'ventilation_rate', 'status']
df = pd.DataFrame(data, columns=columns)
df.to_csv('coop_environmental_data.csv', index=False)

print(f"[+] Multi-compartment dataset generated successfully with {len(df)} samples!")
print(df['status'].value_counts())