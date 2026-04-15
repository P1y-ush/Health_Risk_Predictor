from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()

model = joblib.load("ml/model.pkl")

def get_recommendation(risk):
    if risk == "High":
        return "Consult doctor, reduce sugar, exercise"
    elif risk == "Normal":
        return "Maintain healthy lifestyle"
    else:
        return "Keep doing good habits"

@app.get("/")
def home():
    return {"message": "Health API Running"}

@app.post("/predict")
def predict(data: dict):
    values = np.array(list(data.values())).reshape(1, -1)
    result = model.predict(values)[0]

    if result == 0:
        risk = "Low"
    elif result == 1:
        risk = "Normal"
    else:
        risk = "High"

    return {
        "risk": risk,
        "recommendation": get_recommendation(risk)
    }