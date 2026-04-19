from flask import Flask, render_template, request, jsonify, redirect
import json
from sklearn import svm
import numpy as np
import serial
from svm import process_signature
import time
from sklearn.preprocessing import StandardScaler
from src.signature_structure.signature import Signature
ser = None  # don't open at startup



def get_serial():
    global ser
    if ser is None or not ser.is_open:
        try:
            ser = serial.Serial('COM4', 9600, timeout=1)
            time.sleep(2)
        except serial.SerialException as e:
            print(f"Could not open serial port: {e}")
            return None
    return ser

# --- Flask app ---
app = Flask(__name__)

scaler=StandardScaler()

def train_model():
    global clfs
    with open('signatures.json', 'r') as f:
        data = json.load(f)
    
    stroke_features = {}
    
    for raw_signature in data:
        for segment_group in raw_signature:
            payload = {
                "strokes": [
                    {"points": [{"t": p['timestamp'], "x": p['x'], "y": p['y']} for p in segment]}
                    for segment in segment_group
                ]
            }
            sig = Signature.from_payload(payload)
            
            for k, segment in enumerate(sig.segments):
                speeds = [p.speed for p in segment.points[1:]]
                accel = [speeds[i+1] - speeds[i] for i in range(len(speeds)-1)]
                
                features = [
                    segment.duration,
                    segment.mean_speed,
                    segment.peak_speed,
                    max(accel) if accel else 0,
                    min(accel) if accel else 0,
                ]
                
                if k not in stroke_features:
                    stroke_features[k] = []
                stroke_features[k].append(features)
    
    for stroke_index, features in stroke_features.items():
        X = np.array(features)
        # scalers[stroke_index] = StandardScaler()          
        # X_scaled = scalers[stroke_index].fit_transform(X)        
        clf = svm.OneClassSVM(kernel='rbf', nu=0.1)
        clf.fit(X)
        clfs[stroke_index] = clf

# --- Screen routes ---
@app.route('/')
def index():
    return render_template('/set_password.html')

# make sure this exists in app.py
@app.route('/set_password')
def set_password():
    # clear old signatures
    with open('signatures.json', 'w') as f:
        json.dump([], f)
    # reset model
    global clfs, scalers
    clfs = {}
    scalers = {}
    return render_template('set_password.html')
@app.route('/unlocked')
def unlocked():
    return render_template('unlocked.html')


@app.route('/plocking')
def plocking():
    return render_template('plocking.html')


# --- API routes ---
@app.route('/getSignatureSet', methods=['POST'])
def getSignatureSet():
    data=request.get_json()
    signatureSet=data['signatureSet']
    processSignatureDump(signatureSet)

    return jsonify({'status':'success', 'redirect': '/plocking'}) #also brings user to the  checksignature page

def processSignatureDump(signatureSet):
    with open('signatures.json', 'w') as f:
        json.dump(signatureSet, f)

def processSignatureToTest(signature):
    with open('signature_to_test.json', 'w') as f:
        json.dump(signature, f)


scalers={}
clfs={}
@app.route('/checkSignature')
def checkSignature():
    return render_template("checkSignature.html")


@app.route('/verify', methods=['POST'])
def verify():
    global clfs,scalers 
    if not clfs:
        train_model()
    
    data = request.get_json()
    raw_signature = data['signature']
    if isinstance(raw_signature[0][0], list):
        raw_signature = raw_signature[0]
    
    payload = {
        "strokes": [
            {"points": [{"t": p['timestamp'], "x": p['x'], "y": p['y']} for p in segment]}
            for segment in raw_signature
        ]
    }
    sig = Signature.from_payload(payload)
    
    stroke_results = []
    for k, segment in enumerate(sig.segments):
        if k not in clfs:
            continue
        
        speeds = [p.speed for p in segment.points[1:]]
        accel = [speeds[i+1] - speeds[i] for i in range(len(speeds)-1)]
        
        features = np.array([[
            segment.duration,
            segment.mean_speed,
            segment.peak_speed,
            max(accel) if accel else 0,
            min(accel) if accel else 0,
        ]])
        # features_scaled = scalers[k].transform(features)  
        
        score = clfs[k].decision_function(features)[0]
        print(f'stroke {k}: score={score}')  # print raw score

        is_stroke_genuine = bool(score > -0.15)
        stroke_results.append(is_stroke_genuine)
        print(f'stroke {k}: {"genuine" if is_stroke_genuine else "forged"}')
        
    is_genuine = all(stroke_results)
    return jsonify({'genuine': is_genuine, 'strokes': stroke_results})



if __name__ == "__main__":
    app.run(debug=True)