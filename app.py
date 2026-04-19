from flask import Flask, render_template, request, jsonify, redirect
import json
from sklearn import svm
import numpy as np
import serial
from svm import process_signature
import time

# --- Serial (Arduino) ---
ser = None

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

# --- SVM Model ---
clf = None

def train_model():
    global clf
    with open('signatures.json', 'r') as f:
        data = json.load(f)

    X = []
    for raw_signature in data:
        for segment_group in raw_signature:
            features = process_signature(segment_group)
            vector = list(features.values())
            X.append(vector)

    clf = svm.OneClassSVM(kernel='rbf', nu=0.25)
    clf.fit(X)

# --- Screen routes ---
@app.route('/')
def index():
    return redirect('/unlocked')

@app.route('/unlocked')
def unlocked():
    return render_template('unlocked.html')

@app.route('/set-password')
def set_password():
    return render_template('set_password.html')

@app.route('/plocking')
def plocking():
    return render_template('plocking.html')

@app.route('/checkSignature')
def checkSignature():
    return render_template('checkSignature.html')

# --- API routes ---
@app.route('/getSignatureSet', methods=['POST'])
def getSignatureSet():
    data = request.get_json()
    signatureSet = data['signatureSet']
    processSignatureDump(signatureSet)
    train_model()
    return jsonify({'status': 'success', 'redirect': '/plocking'})

@app.route('/lock', methods=['POST'])
def lock():
    s = get_serial()
    if s:
        s.write(b'lock\n')
    else:
        print("Serial not available")
    return jsonify({'status': 'locked'})

@app.route('/verify', methods=['POST'])
def verify():
    global clf
    if clf is None:
        try:
            train_model()
        except Exception as e:
            print(f"Could not train model: {e}")
            return jsonify({'genuine': False, 'error': 'No baseline signatures found'})

    try:
        data = request.get_json()
        raw_signature = data['signature']

        print("raw_signature type:", type(raw_signature))
        print("raw_signature:", raw_signature)

        # Unwrap nested lists safely
        while (
            isinstance(raw_signature, list) and
            len(raw_signature) == 1 and
            isinstance(raw_signature[0], list)
        ):
            raw_signature = raw_signature[0]

        features = process_signature(raw_signature)
        vector = np.array([list(features.values())])
        result = clf.predict(vector)
        is_genuine = bool(result[0] == 1)

        # Send signal to Arduino
        s = get_serial()
        if s:
            s.write(b'real\n' if is_genuine else b'fake\n')
        else:
            print("Serial not available")

        return jsonify({'genuine': is_genuine})

    except Exception as e:
        print(f"Verify error: {e}")
        return jsonify({'genuine': False, 'error': str(e)})

# --- Helper functions ---
def processSignatureDump(signatureSet):
    with open('signatures.json', 'w') as f:
        json.dump(signatureSet, f)

def processSignatureToTest(signature):
    with open('signature_to_test.json', 'w') as f:
        json.dump(signature, f)

if __name__ == "__main__":
    app.run(debug=True)