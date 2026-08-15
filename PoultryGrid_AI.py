import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, BatchNormalization, Dropout
from keras.callbacks import EarlyStopping

# 1. Load Data
df = pd.read_csv('coop_environmental_data.csv')

# 2. Dynamic Target Calculation (Coop Only)
def get_target_temp(row):
    return 33.0 - (row['week'] - 1) * 2.4

df['temp_deviation'] = abs(df['temperature'] - df.apply(get_target_temp, axis=1))

# 3. Input Features (8 Features)
X = df[[
    'day', 'week', 
    'humidity', 'ammonia', 'temperature', 
    'light', 'ventilation_rate', 'temp_deviation'
]]
Y = df['status']

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# 4. Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

joblib.dump(scaler, 'scaler.pkl')

print("\n--- COPY THESE VALUES TO ESP32 INO ---")
# C++ Arrays updated to size 8
print("const float SCALER_MEAN[8]  = {" + ", ".join(f"{m:.6f}f" for m in scaler.mean_) + "};")
print("const float SCALER_SCALE[8] = {" + ", ".join(f"{s:.6f}f" for s in scaler.scale_) + "};\n")

# 5. Neural Network Architecture (Input shape changed from 9 to 8)
model = Sequential([
    Dense(64, activation='relu', input_shape=(8,)),
    BatchNormalization(),
    Dropout(0.2),
    Dense(32, activation='relu'),
    BatchNormalization(),
    Dense(16, activation='relu'),
    Dense(3, activation='softmax')
])

model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

# 6. Train
early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
model.fit(X_train_scaled, y_train, epochs=300, batch_size=32, validation_split=0.2, callbacks=[early_stop], verbose=1)

# 7. Evaluate
loss, accuracy = model.evaluate(X_test_scaled, y_test, verbose=0)
print(f"\n[+] Model Test Accuracy: {accuracy * 100:.2f}%")

# 8. Export TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open("PoultryGridAI.tflite", "wb") as f:
    f.write(tflite_model)

print("[+] PoultryGridAI.tflite created successfully.")