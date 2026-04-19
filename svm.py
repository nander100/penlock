from sklearn import svm
import json
from src.signature_structure.signature import Signature

with open('signatures.json', 'r') as f:
    data = json.load(f)


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

def signature_acceleration_profile(sig):
    all_accelerations = []
    for segment in sig.segments:
        points = segment.points
        speeds = [p.speed for p in points]
        accelerations = [
            speeds[i+1] - speeds[i]
            for i in range(len(speeds)-1)
        ]
        all_accelerations.extend(accelerations)
    
    normalized = normalize_speeds(all_accelerations)
    peak_index = normalized.index(max(normalized))
    n = len(normalized)
    
    return {
        'global_peak_accel_position': peak_index / n,
        'global_max_acceleration': max(all_accelerations),
        'global_max_deceleration': min(all_accelerations),
        'global_mean_acceleration': sum(all_accelerations) / len(all_accelerations),
    }

import statistics

all_features = []

for i, raw_signature in enumerate(data):
    for j, segment_group in enumerate(raw_signature):
        payload = {
            "strokes": [
                {
                    "points": [
                        {"t": p['timestamp'], "x": p['x'], "y": p['y']}
                        for p in segment
                    ]
                }
                for segment in segment_group
            ]
        }
        
        sig = Signature.from_payload(payload)

        sig_features = {
            'duration': sig.total_duration,
            'mean_speed': sig.mean_speed,
            'stroke_count': sig.stroke_count,
        }

        global_accel = signature_acceleration_profile(sig)
        for key, val in global_accel.items():
            sig_features[key] = val

        for k, segment in enumerate(sig.segments):
            speeds = list(segment.speed_profile)
            profile = speed_profile_features(speeds)
            for key, val in profile.items():
                sig_features[f'stroke{k}_{key}'] = val

        # global acceleration already added above
        global_accel = signature_acceleration_profile(sig)
        for key, val in global_accel.items():
            sig_features[key] = val
        all_features.append(sig_features)

# compute variance and mean for each feature
print('\n--- Variance and Mean across signatures ---')
stdevs = {}
keys = all_features[0].keys()
for key in keys:
    values = [f[key] for f in all_features]
    if len(values) > 1:
        var = statistics.stdev(values)
        mean = statistics.mean(values)
        stdevs[key] = var
        coeffVariance=var/mean
        print(f'  {key}: mean={mean:.4f}, coeffVariance={var:.6f}')

# print least varying metric
least_varying = min(stdevs, key=stdevs.get)
filtered_variances = {k: v for k, v in stdevs.items() if k != 'stroke_count'}

# sort by cv and get top 5 least varying
sorted_metrics = sorted(filtered_variances.items(), key=lambda x: x[1])

print('\n--- Top 5 least varying metrics ---')
for key, val in sorted_metrics[:5]:
    print(f'  {key}: {val:.3f}')
