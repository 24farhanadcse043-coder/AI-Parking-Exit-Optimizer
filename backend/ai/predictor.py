import os

import joblib
import pandas as pd


# --------------------------------------------------
# MODEL PATH
# --------------------------------------------------

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "model",
    "congestion_model.pkl"
)


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# CONGESTION LABELS
# --------------------------------------------------

CONGESTION_LABELS = {
    0: "LOW",
    1: "MEDIUM",
    2: "HIGH"
}


# --------------------------------------------------
# PREDICT CONGESTION
# --------------------------------------------------

def predict_congestion(
    queue_length,
    waiting_time,
    distance
):

    input_data = pd.DataFrame(
        [
            {
                "queue_length": queue_length,
                "waiting_time": waiting_time,
                "distance": distance
            }
        ]
    )

    prediction = model.predict(input_data)

    prediction_value = int(prediction[0])

    return CONGESTION_LABELS.get(
        prediction_value,
        "UNKNOWN"
    )