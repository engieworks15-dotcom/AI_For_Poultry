import joblib
import numpy as np
import tensorflow as tf

# ========================================================
# TEST ROW INPUT (MANUALLY EDIT FOR VERIFICATION)
# ========================================================
test_row = {
    'day': 21,                
    'week': 3,                
    'humidity': 60.0,         
    'ammonia': 10.0,          
    'temperature': 28.2,      
    'light': 15.0,            
    'ventilation_rate': 1.5 
}

def run_test_inference(data):
    day = data['day']
    week = data['week']
    
    target_temp = 33.0 - (week - 1) * 2.4
    temp_dev = abs(data['temperature'] - target_temp)

    raw_features = np.array([[
        data['day'],
        data['week'],
        data['humidity'],
        data['ammonia'],
        data['temperature'],
        data['light'],
        data['ventilation_rate'],
        temp_dev
    ]], dtype=np.float32)

    scaler = joblib.load('scaler.pkl')
    scaled_features = scaler.transform(raw_features).astype(np.float32)

    # 4. TFLite Interpreter
    interpreter = tf.lite.Interpreter(model_path="PoultryGridAI.tflite")
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], scaled_features)
    interpreter.invoke()

    probabilities = interpreter.get_tensor(output_details[0]['index'])[0]
    predicted_class = np.argmax(probabilities)

    status_labels = {0: "NORMAL", 1: "WARNING", 2: "DANGER"}

    print("\n--- INFERENCE RESULT ---")
    print(f"Day: {day} | Temp: {data['temperature']}°C | Target: {target_temp}°C")
    print(f"Probabilities -> Normal: {probabilities[0]:.2%}, Warning: {probabilities[1]:.2%}, Danger: {probabilities[2]:.2%}")
    print(f"Evaluated Status: {status_labels[predicted_class]} ({predicted_class})")

run_test_inference(test_row)