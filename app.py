from flask import Flask, render_template,request,jsonify
import json
from sklearn import svm
import numpy as np
import serial
from svm import process_signature
import time

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

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/getSignatureSet', methods=['POST'])
def getSignatureSet():
    data=request.get_json()
    signatureSet=data['signatureSet']
    processSignatureDump(signatureSet)

    return jsonify({'status':'success', 'redirect': '/checkSignature'}) #also brings user to the  checksignature page

def processSignatureDump(signatureSet):
    with open('signatures.json', 'w') as f:
        json.dump(signatureSet, f)

def processSignatureToTest(signature):
    with open('signature_to_test.json', 'w') as f:
        json.dump(signature, f)

clf = None  # global model
@app.route('/checkSignature')
def checkSignature():
    return render_template("checkSignature.html")



@app.route('/verify', methods=['POST'])
def verify():
    global clf
    if clf is None:
        train_model()
    
    data = request.get_json()
    raw_signature = data['signature']  # [[segment1, segment2]]
    # unwrap if needed
    if isinstance(raw_signature[0][0], list):
        raw_signature = raw_signature[0]
    
    features = process_signature(raw_signature)
    vector = np.array([list(features.values())])
    result = clf.predict(vector)
    is_genuine = bool(result[0] == 1)  # convert numpy bool to Python bool

    s = get_serial()
    if s:
        s.write(b'real\n' if is_genuine else b'fake\n')  # b'' for bytes
    else:
        print("Serial not available")
    
    
    return jsonify({'genuine': is_genuine})

# def getGenuineOrNot(signature):
#     with open('signature_to_test.json', 'w') as f:
#         json.dump(signature, f)



if __name__ == "__main__":
    app.run(debug=True)
