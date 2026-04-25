import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

print("=" * 50)
print("  Health Risk Predictor — Model Training")
print("=" * 50)

# Load dataset
script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_dir, "dataset.csv")
df = pd.read_csv(dataset_path)

print(f"\n📊 Dataset loaded: {len(df)} samples")
print(f"   Features: {list(df.columns[:-1])}")
print(f"   Risk distribution:\n{df['risk'].value_counts().to_string()}")

# Features and target
feature_columns = ["age", "bp", "sugar", "cholesterol", "heart_rate", "bmi"]
X = df[feature_columns]
y = df["risk"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n🔀 Train/Test split: {len(X_train)} train, {len(X_test)} test")

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    class_weight="balanced"
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

risk_labels = {0: "Low", 1: "Normal", 2: "High"}
print(f"\n✅ Model Accuracy: {accuracy * 100:.1f}%")
print(f"\n📋 Classification Report:")
print(classification_report(
    y_test, y_pred,
    target_names=["Low Risk", "Normal Risk", "High Risk"]
))

# Feature importance
importances = dict(zip(feature_columns, model.feature_importances_))
print("📊 Feature Importance:")
for feat, imp in sorted(importances.items(), key=lambda x: x[1], reverse=True):
    print(f"   {feat}: {imp:.3f}")

# Save model
model_path = os.path.join(script_dir, "model.pkl")
model_metadata = {
    "model": model,
    "feature_columns": feature_columns,
    "risk_labels": risk_labels,
    "accuracy": accuracy
}
joblib.dump(model_metadata, model_path)

print(f"\n💾 Model saved to {model_path}")
print("=" * 50)