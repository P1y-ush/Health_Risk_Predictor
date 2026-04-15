import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

print("Starting training...")

# Dummy dataset
data = {
    "age": [25, 45, 60, 30, 50],
    "bp": [80, 140, 160, 90, 150],
    "sugar": [90, 200, 250, 100, 220],
    "risk": [0, 2, 2, 1, 2]
}

df = pd.DataFrame(data)

X = df[["age", "bp", "sugar"]]
y = df["risk"]

model = RandomForestClassifier()
model.fit(X, y)

# Ensure ml folder exists
os.makedirs("ml", exist_ok=True)

# Save model
joblib.dump(model, "ml/model.pkl")

print("✅ Model saved successfully at ml/model.pkl")