# enlarge_dual.py
import numpy as np
import pandas as pd

# ==========================================
# 1. RANGE DEFINITIONS FOR BOTH ENVIRONMENTS
# ==========================================

# --- ENVIRONMENT 1: HATCHERY ---
hatch_temp_ranges = [34.0, 36.0, 37.5, 38.1, 39.0] # Freezing, Cold, Optimal, Hot, Critical
hatch_hum_ranges  = [35.0, 45.0, 55.0, 72.0, 80.0] # Danger low, Warning low, Optimal, Warning high, Danger high
hatch_vent_ranges = [0.3, 0.7, 2.0, 4.0, 6.0]      # Suffocating, Warning low, Optimal, Warning high, High draft
# Hatchery ammonia is highly dangerous; brightness should be dark
hatch_amm_ranges  = [0.0, 3.0, 8.0]                # Normal, Warning, Danger
hatch_lux_ranges  = [0.0, 5.0, 15.0]               # Normal, Warning, Danger

# --- ENVIRONMENT 2: BREEDING (From your existing dataPlan) ---
breed_amm_ranges  = [5.0, 15.0, 22.0, 28.0]
breed_temp_ranges = [8.0, 12.0, 18.0, 30.0, 34.0, 40.0]
breed_lux_ranges  = [9.0, 20.0, 35.0]
breed_hum_ranges  = [25.0, 40.0, 60.0, 72.0, 80.0]
breed_vent_ranges = [0.3, 0.7, 3.0, 5.0, 8.0, 12.0]

records = []

# ==========================================
# 2. GENERATING DUAL DATA COMBINATIONS
# ==========================================
# We will generate balanced combinations for both environments
# to construct a cohesive 'environment_data.csv' file.

# Step A: Generate Hatchery (Env 1) States
for amm in hatch_amm_ranges:
    for temp in hatch_temp_ranges:
        for lux in hatch_lux_ranges:
            for hum in hatch_hum_ranges:
                for vent in hatch_vent_ranges:
                    is_danger = False
                    concerning_states = 0
                    
                    # Absolute Danger Thresholds for Hatchery
                    if amm >= 5.0 or temp < 35.0 or temp >= 38.4 or lux >= 10.0 or hum < 40.0 or hum > 75.0 or vent < 0.5 or vent > 5.0:
                        is_danger = True
                    
                    # Warning States counting
                    if 35.0 <= temp <= 37.1 or 37.9 <= temp <= 38.3:
                        concerning_states += 1
                    if 1.0 <= amm < 5.0:
                        concerning_states += 1
                    if 1.0 <= lux < 10.0:
                        concerning_states += 1
                    if 40.0 <= hum < 50.0 or 71.0 <= hum <= 75.0:
                        concerning_states += 1
                    if 0.5 <= vent <= 0.9 or 3.1 <= vent <= 5.0:
                        concerning_states += 1
                        
                    # State assignment
                    if is_danger:
                        state = "Danger"
                    elif concerning_states == 0:
                        state = "Normal"
                    else:
                        state = "Warning"
                        
                    # We write Env_Type = 1 for Hatchery
                    records.append([1, amm, temp, lux, hum, vent, state])

# Step B: Generate Breeding (Env 2) States
for amm in breed_amm_ranges:
    for temp in breed_temp_ranges:
        for lux in breed_lux_ranges:
            for hum in breed_hum_ranges:
                for vent in breed_vent_ranges:
                    is_danger = False
                    concerning_states = 0
                    
                    # Absolute Danger Thresholds for Breeding
                    if amm >= 25.0 or temp >= 38.0 or lux >= 31.0 or hum < 30.0 or hum > 75.0 or vent < 0.5 or vent > 10.0:
                        is_danger = True
                    
                    # Warnings
                    if temp < 10.0 or (10.0 <= temp <= 14.0) or (29.0 <= temp < 32.0) or (32.0 <= temp < 38.0):
                        concerning_states += 1
                    if 20.0 <= amm < 25.0:
                        concerning_states += 1
                    if 11.0 <= lux < 31.0:
                        concerning_states += 1
                    if (30.0 <= hum < 50.0) or (70.0 <= hum <= 75.0):
                        concerning_states += 1
                    if (7.0 <= vent <= 10.0) or (0.5 <= vent <= 0.9):
                        concerning_states += 1
                        
                    # State assignment
                    if is_danger:
                        state = "Danger"
                    elif concerning_states == 0:
                        state = "Normal"
                    else:
                        state = "Warning"
                        
                    # We write Env_Type = 2 for Breeding
                    records.append([2, amm, temp, lux, hum, vent, state])

# ==========================================
# 3. SAVE DUAL DATA TO THE FILE
# ==========================================
df = pd.DataFrame(records, columns=[
    'Env_Type', 
    'Ammonia_Level_ppm', 
    'Temperature_C', 
    'Brightness_Lux', 
    'Humidity_Pct', 
    'Ventilation_Rate_CFM', 
    'State'
])

# Overwrite current csv file
df.to_csv("environment_data.csv", index=False)
print(f"Successfully generated {len(df)} entries.")
print("Saved both Hatchery (Env 1) & Breeding (Env 2) conditions to environment_data.csv!")