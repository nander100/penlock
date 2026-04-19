import json

import joblib
import numpy as np
from sklearn import svm
from sklearn.model_selection import LeaveOneOut
from sklearn.preprocessing import StandardScaler

from src.signature_structure.signature import Signature


FEATURE_KEYS = [
    'duration',
    'peak_speed_position',
    'lowest_speed_position',
    'max_speed',
    'min_speed',
    'peak_accel_position',
    'peak_decel_position',
    'max_acceleration',
    'max_deceleration',
]


def normalize_speeds(speeds: list[float]) -> list[float]:
    if not speeds:
        return []
    min_s = min(speeds)
    max_s = max(speeds)
    if max_s == min_s:
        return [0.0] * len(speeds)
    return [(s - min_s) / (max_s - min_s) for s in speeds]


def signature_speed_profile(sig: Signature) -> dict:
    all_speeds = []
    for segment in sig.segments:
        all_speeds.extend(p.speed for p in segment.points[1:])

    peak_index = all_speeds.index(max(all_speeds))
    n = len(all_speeds)
    return {
        'peak_speed_position': peak_index / n,
        'lowest_speed_position': all_speeds.index(min(all_speeds)) / n,
        'max_speed': max(all_speeds),
        'min_speed': min(all_speeds),
    }


def signature_acceleration_profile(sig: Signature) -> dict:
    all_accelerations = []
    for segment in sig.segments:
        speeds = [p.speed for p in segment.points[1:]]
        all_accelerations.extend(
            speeds[i + 1] - speeds[i] for i in range(len(speeds) - 1)
        )

    if not all_accelerations:
        return {
            'peak_accel_position': 0.0,
            'peak_decel_position': 0.0,
            'max_acceleration': 0.0,
            'max_deceleration': 0.0,
        }

    normalized = normalize_speeds(all_accelerations)
    n = len(normalized)
    return {
        'peak_accel_position': normalized.index(max(normalized)) / n,
        'peak_decel_position': normalized.index(min(normalized)) / n,
        'max_acceleration': max(all_accelerations),
        'max_deceleration': min(all_accelerations),
    }


def process_signature(raw_signature) -> dict:
    if isinstance(raw_signature[0][0], list):
        raw_signature = raw_signature[0]
    payload = {
        "strokes": [
            {"points": [{"t": p['timestamp'], "x": p['x'], "y": p['y']} for p in segment]}
            for segment in raw_signature
        ]
    }
    sig = Signature.from_payload(payload)

    features = {'duration': sig.total_duration}
    features.update(signature_acceleration_profile(sig))
    features.update(signature_speed_profile(sig))
    return features


def to_vector(features: dict) -> list[float]:
    return [features[k] for k in FEATURE_KEYS]


# ------------------------------------------------------------------ #
# Training
# ------------------------------------------------------------------ #

with open('signatures.json', 'r') as f:
    data = json.load(f)

all_features = [process_signature(raw) for raw in data]
X = np.array([to_vector(f) for f in all_features])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

clf = svm.OneClassSVM(kernel='rbf', nu=0.1)
clf.fit(X_scaled)

# ------------------------------------------------------------------ #
# Leave-one-out cross-validation (false-reject rate on own signatures)
# ------------------------------------------------------------------ #

loo = LeaveOneOut()
false_rejects = 0
for train_idx, test_idx in loo.split(X_scaled):
    cv_clf = svm.OneClassSVM(kernel='rbf', nu=0.1)
    cv_clf.fit(X_scaled[train_idx])
    if cv_clf.predict(X_scaled[test_idx])[0] == -1:
        false_rejects += 1

frr = false_rejects / len(X_scaled)
print(f'Leave-one-out false-reject rate: {frr:.1%} ({false_rejects}/{len(X_scaled)})')

# ------------------------------------------------------------------ #
# Persist model
# ------------------------------------------------------------------ #

joblib.dump({'clf': clf, 'scaler': scaler}, 'penlock_model.pkl')
print('Model saved to penlock_model.pkl')


# ------------------------------------------------------------------ #
# Prediction helper (used by app.py at verify time)
# ------------------------------------------------------------------ #

def predict_signature(raw_signature) -> str:
    features = process_signature(raw_signature)
    vector = np.array([to_vector(features)])
    vector_scaled = scaler.transform(vector)
    result = clf.predict(vector_scaled)
    return 'genuine' if result[0] == 1 else 'forged'
