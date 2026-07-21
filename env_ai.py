import pandas as pd
import tensorflow as tf
import numpy as np

# 1. Load and Shuffle Data
df = pd.read_csv("environment_data.csv")
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# 2. Features & Targets
features = ['Env_Type', 'Ammonia_Level_ppm', 'Temperature_C', 'Brightness_Lux', 'Humidity_Pct', 'Ventilation_Rate_CFM']
x = df[features].values
y = pd.get_dummies(df['State']).values

# 3. Fit Scaling Parameters & Save
x_min, x_max = x.min(axis=0), x.max(axis=0)
x_scaled = (x - x_min) / (x_max - x_min)
np.savez('scaling_params_dual.npz', min=x_min, max=x_max)

# 4. Neural Network
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(6,)),
    tf.keras.layers.Dropout(0.1),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dropout(0.1),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(3, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 5. Train
model.fit(x_scaled, y, epochs=150, batch_size=32, validation_split=0.2, verbose=1)

# 6. Convert & Save directly as TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open("coop_model.tflite", "wb") as f:
    f.write(tflite_model)

print("TFLite model exported successfully!")