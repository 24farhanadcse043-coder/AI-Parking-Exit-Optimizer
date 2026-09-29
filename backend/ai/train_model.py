import os

import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# --------------------------------------------------
# TRAINING DATA
# --------------------------------------------------

data = [
    [1, 1, 100, "LOW"],
    [2, 1, 120, "LOW"],
    [3, 2, 150, "LOW"],
    [4, 2, 180, "LOW"],
    [5, 3, 200, "LOW"],
    [6, 3, 100, "LOW"],
    [7, 4, 130, "LOW"],

    [8, 5, 160, "MEDIUM"],
    [9, 5, 190, "MEDIUM"],
    [10, 6, 220, "MEDIUM"],
    [11, 7, 110, "MEDIUM"],
    [12, 7, 140, "MEDIUM"],
    [13, 8, 170, "MEDIUM"],
    [14, 8, 200, "MEDIUM"],
    [15, 9, 230, "MEDIUM"],

    [16, 10, 120, "HIGH"],
    [18, 11, 150, "HIGH"],
    [20, 12, 180, "HIGH"],
    [22, 13, 210, "HIGH"],
    [25, 15, 240, "HIGH"],
    [30, 18, 130, "HIGH"],
    [35, 20, 160, "HIGH"],
    [40, 25, 200, "HIGH"],
    [45, 28, 270, "HIGH"]
]


# --------------------------------------------------
# CREATE DATAFRAME
# --------------------------------------------------

df = pd.DataFrame(
    data,
    columns=[
        "queue_length",
        "waiting_time",
        "distance",
        "congestion"
    ]
)

print("Dataset created successfully.")
print(f"Number of records: {len(df)}")


# --------------------------------------------------
# CONVERT TARGET LABELS
# --------------------------------------------------

congestion_mapping = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2
}

df["congestion"] = df["congestion"].map(congestion_mapping)


# --------------------------------------------------
# INPUT FEATURES
# --------------------------------------------------

X = df[
    [
        "queue_length",
        "waiting_time",
        "distance"
    ]
]


# --------------------------------------------------
# TARGET
# --------------------------------------------------

y = df["congestion"]


# --------------------------------------------------
# SPLIT DATA
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# CREATE RANDOM FOREST MODEL
# --------------------------------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# --------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------

model.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# TEST MODEL
# --------------------------------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

print("Model training completed.")
print(f"Model accuracy: {accuracy * 100:.2f}%")


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

model_directory = os.path.join(
    os.path.dirname(__file__),
    "model"
)

os.makedirs(
    model_directory,
    exist_ok=True
)


model_path = os.path.join(
    model_directory,
    "congestion_model.pkl"
)


joblib.dump(
    model,
    model_path
)


print("Model saved successfully.")
print(f"Model path: {model_path}")