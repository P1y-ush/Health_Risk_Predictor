from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import pandas as pd
import logging
import os
import json
from datetime import datetime, timezone

# ── Structured Logging ────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger("health-predictor")


def log_json(level, message, **kwargs):
    """Structured JSON logging for ELK ingestion."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "service": "health-risk-predictor",
        "message": message,
        **kwargs
    }
    logger.info(json.dumps(entry))


# ── App Setup ─────────────────────────────────────────────────────
app = FastAPI(
    title="AI Health Risk Predictor",
    description="ML-powered health risk prediction with personalized recommendations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ── Load ML Model ─────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(BASE_DIR), "ml", "model.pkl")
model_data = joblib.load(MODEL_PATH)
model = model_data["model"]
feature_columns = model_data["feature_columns"]
risk_labels = model_data["risk_labels"]
model_accuracy = model_data["accuracy"]

log_json("INFO", "Model loaded successfully", accuracy=f"{model_accuracy*100:.1f}%")


# ── Pydantic Models ───────────────────────────────────────────────
class HealthInput(BaseModel):
    age: float = Field(..., ge=1, le=120, description="Age in years")
    bp: float = Field(..., ge=40, le=250, description="Blood pressure (systolic)")
    sugar: float = Field(..., ge=30, le=500, description="Blood sugar level (mg/dL)")
    cholesterol: float = Field(..., ge=80, le=500, description="Cholesterol (mg/dL)")
    heart_rate: float = Field(..., ge=30, le=200, description="Heart rate (bpm)")
    bmi: float = Field(..., ge=10, le=60, description="Body Mass Index")


# ── Recommendation Engine ─────────────────────────────────────────
def get_recommendations(risk_level, input_data):
    """Generate personalized health recommendations based on risk level and input values."""
    recommendations = []
    preventive_measures = []

    # ── Risk-specific advice ──
    if risk_level == "High":
        recommendations.extend([
            "⚠️ Consult a healthcare professional immediately for a comprehensive health assessment.",
            "📋 Schedule regular health checkups (at least every 3 months).",
            "💊 Discuss medication options with your doctor if not already on treatment.",
        ])
        preventive_measures.extend([
            "Monitor blood pressure and sugar levels daily.",
            "Follow a strict low-sodium, low-sugar diet plan.",
            "Engage in 30 minutes of supervised moderate exercise daily.",
        ])
    elif risk_level == "Normal":
        recommendations.extend([
            "👍 Your health indicators are within acceptable range, but stay vigilant.",
            "📋 Schedule regular checkups every 6 months.",
            "🏃 Maintain an active lifestyle with regular exercise.",
        ])
        preventive_measures.extend([
            "Continue balanced diet with adequate fruits and vegetables.",
            "Aim for 150 minutes of moderate exercise per week.",
            "Practice stress management techniques like meditation.",
        ])
    else:  # Low risk
        recommendations.extend([
            "🌟 Excellent! Your health indicators show low risk.",
            "✅ Continue your current healthy lifestyle.",
            "📋 Annual health checkups are recommended.",
        ])
        preventive_measures.extend([
            "Maintain your balanced diet and exercise routine.",
            "Stay hydrated — drink 8 glasses of water daily.",
            "Ensure 7-8 hours of quality sleep each night.",
        ])

    # ── Parameter-specific advice ──
    if input_data.bp > 130:
        recommendations.append("🩸 Your blood pressure is elevated. Reduce sodium intake and manage stress.")
    if input_data.sugar > 140:
        recommendations.append("🍬 Your sugar level is above normal. Limit refined carbs and sugary foods.")
    if input_data.cholesterol > 220:
        recommendations.append("🫀 Cholesterol is high. Increase fiber intake, reduce saturated fats.")
    if input_data.bmi > 28:
        recommendations.append("⚖️ Your BMI indicates overweight. Focus on portion control and regular cardio.")
    if input_data.bmi < 18.5:
        recommendations.append("⚖️ Your BMI is underweight. Consult a nutritionist for a balanced meal plan.")
    if input_data.heart_rate > 100:
        recommendations.append("💓 Elevated resting heart rate. Practice relaxation and aerobic exercises.")
    if input_data.age > 50:
        recommendations.append("👴 Age-related risks increase. Prioritize regular screenings and bone density checks.")

    return {
        "recommendations": recommendations,
        "preventive_measures": preventive_measures
    }


# ── Routes ────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web UI."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "model_accuracy": f"{model_accuracy * 100:.1f}"
    })


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {
        "status": "healthy",
        "service": "health-risk-predictor",
        "model_loaded": model is not None,
        "accuracy": f"{model_accuracy * 100:.1f}%",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/predict")
async def predict(data: HealthInput):
    """Predict health risk level and provide personalized recommendations."""
    try:
        # Prepare features as DataFrame with feature names
        values = pd.DataFrame([[
            data.age, data.bp, data.sugar,
            data.cholesterol, data.heart_rate, data.bmi
        ]], columns=feature_columns)

        # Predict
        result = model.predict(values)[0]
        probabilities = model.predict_proba(values)[0]
        risk_level = risk_labels[result]

        # Get recommendations
        advice = get_recommendations(risk_level, data)

        # Build response
        response = {
            "risk_level": risk_level,
            "confidence": f"{max(probabilities) * 100:.1f}%",
            "probabilities": {
                "Low": f"{probabilities[0] * 100:.1f}%",
                "Normal": f"{probabilities[1] * 100:.1f}%",
                "High": f"{probabilities[2] * 100:.1f}%"
            },
            "recommendations": advice["recommendations"],
            "preventive_measures": advice["preventive_measures"],
            "input_summary": data.model_dump()
        }

        log_json("INFO", "Prediction made",
                 risk=risk_level,
                 confidence=response["confidence"],
                 input=data.model_dump())

        return response

    except Exception as e:
        log_json("ERROR", "Prediction failed", error=str(e))
        return {"error": str(e)}, 500