from sklearn import svm
import json
from src.signature_structure.signature import Signature


#good metrics:
#max_acccel



def normalize_speeds(speeds):
    min_s = min(speeds)
    max_s = max(speeds)
    if max_s == min_s:
        return [0.0] * len(speeds)
    return [(s - min_s) / (max_s - min_s) for s in speeds]

def speed_profile_features(speeds):
    normalized = normalize_speeds(speeds)
    peak_index = normalized.index(max(normalized))
    n = len(normalized)
    
    return {
        'peak_position': peak_index / n,        # where peak is 0.0-1.0
        'end_speed': normalized[-1],             # how fast pen exits
    }

def signature_speed_profile(sig):
    all_speeds = []
    for segment in sig.segments:
        speeds = [p.speed for p in segment.points[1:]]  # sip first point
        all_speeds.extend(speeds)
    
    peak_index = all_speeds.index(max(all_speeds))
    n = len(all_speeds)
    
    return {
        'peak_speed_position': peak_index / n,  # where peak occurs 0-1
        'lowest_speed_position': all_speeds.index(min(all_speeds)) / n,  
        'max_speed': max(all_speeds),
        'min_speed': min(all_speeds),
    }

def signature_acceleration_profile(sig):
    all_accelerations = []
    for segment in sig.segments:
        points = segment.points
        speeds = [p.speed for p in segment.points[1:]]  #skip first
        accelerations = [
            speeds[i+1] - speeds[i]
            for i in range(len(speeds)-1)
        ]
        all_accelerations.extend(accelerations)
    
    normalized = normalize_speeds(all_accelerations)
    peak_index = normalized.index(max(normalized))
    n = len(normalized)
    
    return {
        'peak_accel_position': peak_index / n,
        'peak_decel_position': normalized.index(min(normalized)) / n, 
        'max_acceleration': max(all_accelerations),
        'max_deceleration': min(all_accelerations),

    }

def process_signature(raw_signature): #returns featuers of a signature
    payload = {
        "strokes": [
            {
                "points": [
                    {"t": p['timestamp'], "x": p['x'], "y": p['y']}
                    for p in segment
                ]
            }
            for segment in raw_signature
        ]
    }
    
    sig = Signature.from_payload(payload)
    
    sig_features = {
        'duration': sig.total_duration,
    }
    
    accel = signature_acceleration_profile(sig)
    for key, val in accel.items():
        sig_features[key] = val
    
    speed = signature_speed_profile(sig)
    for key, val in speed.items():
        sig_features[key] = val
    
    return sig_features


import numpy as np
'''

all_features=[]
# build feature vectors from all_features
X = []
for sig_features in all_features:
    vector = [
        sig_features['duration'],
        sig_features['peak_speed_position'],
        sig_features['lowest_speed_position'],
        sig_features['max_speed'],
        sig_features['min_speed'],
        sig_features['peak_accel_position'],
        sig_features['peak_decel_position'],
        sig_features['max_acceleration'],
        sig_features['max_deceleration'],
    ]
    X.append(vector)

X = np.array(X)

# one class SVM - only needs genuine signatures, no forged needed
clf = svm.OneClassSVM(kernel='rbf', nu=0.1)
clf.fit(X)


with open('signature_to_test.json', 'r') as f:
    data = json.load(f)
signature_to_test = data[0] 
check_sig_features=process_signature(signature_to_test)

def predict_signature(new_sig_features):
    vector = np.array([[
        new_sig_features['duration'],
        new_sig_features['peak_speed_position'],
        new_sig_features['lowest_speed_position'],
        new_sig_features['max_speed'],
        new_sig_features['min_speed'],
        new_sig_features['peak_accel_position'],
        new_sig_features['peak_decel_position'],
        new_sig_features['max_acceleration'],
        new_sig_features['max_deceleration'],
    ]])
    
    result = clf.predict(vector)
    return 'genuine' if result[0] == 1 else 'forged'

predictions = clf.predict(X)


# import statistics

# all_features = []

# for i, raw_signature in enumerate(data):
#     for j, segment_group in enumerate(raw_signature):
#         payload = {
#             "strokes": [
#                 {
#                     "points": [
#                         {"t": p['timestamp'], "x": p['x'], "y": p['y']}
#                         for p in segment
#                     ]
#                 }
#                 for segment in segment_group
#             ]
#         }
        
#         sig = Signature.from_payload(payload)

#         sig_features = {
#             'duration': sig.total_duration,
#             #'mean_speed': sig.mean_speed,
#             #'stroke_count': sig.stroke_count,
#         }

#         accel = signature_acceleration_profile(sig)
#         for key, val in accel.items():
#             sig_features[key] = val

#         speed = signature_speed_profile(sig)
#         for key, val in speed.items():
#             sig_features[key] = val

#         all_features.append(sig_features)

# # compute variance and mean for each feature
# print('\n--- Variance and Mean across signatures ---')
# stdevs = {}
# keys = all_features[0].keys()
# for key in keys:
#     values = [f[key] for f in all_features]
#     if len(values) > 1:
#         var = statistics.stdev(values)
#         mean = statistics.mean(values)
#         stdevs[key] = var
#         coeffVariance=var/(mean+0.00000001)
#         print(f'  {key}: mean={mean:.4f}, coeffVariance={var:.6f}')

# # print least varying metric
# least_varying = min(stdevs, key=stdevs.get)
# filtered_variances = {k: v for k, v in stdevs.items() if k != 'stroke_count'}

# sort by cv and get top 5 least varying
# sorted_metrics = sorted(filtered_variances.items(), key=lambda x: x[1])

#put these metrics into an svm
'''