import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, get_recommendations, HealthInput

client = TestClient(app)


class TestHealthCheck:
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True

    def test_home_page(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "Health Risk Predictor" in response.text


class TestPrediction:
    def test_low_risk_prediction(self):
        payload = {
            "age": 25, "bp": 78, "sugar": 85,
            "cholesterol": 180, "heart_rate": 72, "bmi": 22.5
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] in ["Low", "Normal", "High"]
        assert "recommendations" in data
        assert "preventive_measures" in data
        assert "confidence" in data
        assert "probabilities" in data

    def test_high_risk_prediction(self):
        payload = {
            "age": 65, "bp": 170, "sugar": 260,
            "cholesterol": 310, "heart_rate": 108, "bmi": 35.0
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] in ["Low", "Normal", "High"]
        assert len(data["recommendations"]) > 0

    def test_invalid_input_age(self):
        payload = {
            "age": -5, "bp": 120, "sugar": 100,
            "cholesterol": 200, "heart_rate": 72, "bmi": 24.0
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Validation error

    def test_missing_field(self):
        payload = {"age": 30, "bp": 120}
        response = client.post("/predict", json=payload)
        assert response.status_code == 422


class TestRecommendations:
    def test_high_risk_recommendations(self):
        data = HealthInput(age=60, bp=170, sugar=250, cholesterol=300, heart_rate=100, bmi=34)
        result = get_recommendations("High", data)
        assert len(result["recommendations"]) > 0
        assert len(result["preventive_measures"]) > 0

    def test_low_risk_recommendations(self):
        data = HealthInput(age=25, bp=78, sugar=85, cholesterol=180, heart_rate=72, bmi=22)
        result = get_recommendations("Low", data)
        assert len(result["recommendations"]) > 0

    def test_bp_specific_advice(self):
        data = HealthInput(age=40, bp=150, sugar=90, cholesterol=190, heart_rate=75, bmi=24)
        result = get_recommendations("Normal", data)
        bp_advice = [r for r in result["recommendations"] if "blood pressure" in r.lower()]
        assert len(bp_advice) > 0

    def test_sugar_specific_advice(self):
        data = HealthInput(age=40, bp=120, sugar=200, cholesterol=190, heart_rate=75, bmi=24)
        result = get_recommendations("Normal", data)
        sugar_advice = [r for r in result["recommendations"] if "sugar" in r.lower()]
        assert len(sugar_advice) > 0
