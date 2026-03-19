"""
model.py — EcoPersona AI
Handles ML model training and prediction using Decision Tree Classifier.
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os


# ── Encodings ──────────────────────────────────────────────────────────────
TRANSPORT_MAP = {
    "bicycle": 0,
    "electric": 1,
    "public": 2,
    "car": 3,
    "flight": 4,
}

FOOD_MAP = {
    "vegan": 0,
    "vegetarian": 1,
    "pescatarian": 2,
    "omnivore": 3,
    "meat_heavy": 4,
}

SHOPPING_MAP = {
    "minimal": 0,
    "moderate": 1,
    "frequent": 2,
    "heavy": 3,
}

IMPACT_MAP = {"Low": 0, "Medium": 1, "High": 2}
IMPACT_REVERSE = {0: "Low", 1: "Medium", 2: "High"}


# ── Feature Engineering ────────────────────────────────────────────────────
def encode_features(transport, food, shopping, electricity, distance):
    """Convert raw inputs into numerical feature vector."""
    return [[
        TRANSPORT_MAP.get(transport, 3),
        FOOD_MAP.get(food, 3),
        SHOPPING_MAP.get(shopping, 1),
        float(electricity),
        float(distance),
    ]]


# ── Model Training ─────────────────────────────────────────────────────────
def load_and_train(data_path="data.csv"):
    """Load dataset, encode, train Decision Tree, return model + accuracy."""
    df = pd.read_csv(data_path)

    df["transport_enc"] = df["transport"].map(TRANSPORT_MAP)
    df["food_enc"]      = df["food"].map(FOOD_MAP)
    df["shopping_enc"]  = df["shopping"].map(SHOPPING_MAP)
    df["impact_enc"]    = df["impact_level"].map(IMPACT_MAP)

    feature_cols = ["transport_enc", "food_enc", "electricity", "shopping_enc", "distance"]
    X = df[feature_cols].values
    y = df["impact_enc"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = DecisionTreeClassifier(
        max_depth=6,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
    )
    model.fit(X_train, y_train)

    preds   = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds)

    return model, accuracy


# ── Prediction ─────────────────────────────────────────────────────────────
def predict_impact(model, transport, food, shopping, electricity, distance):
    """Predict impact level (Low / Medium / High) for given lifestyle inputs."""
    features = encode_features(transport, food, shopping, electricity, distance)
    pred_enc = model.predict(features)[0]
    proba    = model.predict_proba(features)[0]
    return IMPACT_REVERSE[pred_enc], proba


# ── Feature Importance ─────────────────────────────────────────────────────
def get_feature_importance(model):
    """Return feature names and their importance scores."""
    names       = ["Transport", "Food & Diet", "Electricity", "Shopping", "Distance"]
    importances = model.feature_importances_
    return dict(zip(names, importances))
