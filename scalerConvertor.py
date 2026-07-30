import joblib

scaler = joblib.load('scaler.pkl')
print("float MEAN[] = {" + ", ".join(f"{m:.6f}f" for m in scaler.mean_) + "};")
print("float SCALE[] = {" + ", ".join(f"{s:.6f}f" for s in scaler.scale_) + "};")