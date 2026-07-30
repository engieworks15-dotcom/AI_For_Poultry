import joblib
import pandas
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, BatchNormalization, Dropout
from keras.callbacks import EarlyStopping

# 1. Load multi-compartment dataset
df = pandas.read_csv('coop_environmental_data.csv')

# 2. Feature Engineering: Calculate temperature deviation from compartment target
def get_temp_deviation(row):
    comp = row['compartment_id']
    if comp == 0:
        return abs(row['temperature'] - 37.5)  # Incubator target
    elif comp == 1:
        return abs(row['temperature'] - 36.8)  # Hatchery target
    else:
        ideal_coop_temp = 33.0 - (row['week'] - 1) * 2.4
        return abs(row['temperature'] - ideal_coop_temp)  # Coop target

df['temp_deviation'] = df.apply(get_temp_deviation, axis=1)

X = df[[
    'compartment_id', 
    'week', 
    'humidity', 
    'ammonia', 
    'temperature', 
    'light', 
    'ventilation_rate', 
    'temp_deviation'
]]
Y = df['status']

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# 4. Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

joblib.dump(scaler, 'scaler.pkl')

model = Sequential([
    Dense(64, activation='relu', input_shape=(8,)),
    BatchNormalization(),
    Dropout(0.2),
    
    Dense(32, activation='relu'),
    BatchNormalization(),
    
    Dense(16, activation='relu'),
    
    Dense(3, activation='softmax')
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

early_stop = EarlyStopping(
    monitor='val_loss', 
    patience=15, 
    restore_best_weights=True
)

history = model.fit(
    X_train_scaled, 
    y_train, 
    epochs=300, 
    batch_size=32, 
    validation_split=0.2,
    callbacks=[early_stop],
    verbose=1
)

# Evaluate Performance
loss, accuracy = model.evaluate(X_test_scaled, y_test, verbose=0)
print(f"\n[+] Model Test Accuracy: {accuracy * 100:.2f}%")

#Export to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open("PoultryGridAI.tflite", "wb") as f:
    f.write(tflite_model)

print("Training completed. God be with you!")