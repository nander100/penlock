from flask import Flask, render_template, request, jsonify
import json
import time
from svm import predict_signature

try:
    import serial as pyserial
except ImportError:
    pyserial = None

ser = None  # don't open at startup

def get_serial():
    global ser
    if pyserial is None or not hasattr(pyserial, 'Serial'):
        return None
    if ser is None or not ser.is_open:
        try:
            ser = pyserial.Serial('COM4', 9600, timeout=1)
            time.sleep(2)
        except Exception as e:
            print(f"Could not open serial port: {e}")
            return None
    return ser

app = Flask(__name__)

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

@app.route('/checkSignature')
def checkSignature():
    return render_template("checkSignature.html")



@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    raw_signature = data['signature']
    if isinstance(raw_signature[0][0], list):
        raw_signature = raw_signature[0]

    is_genuine = predict_signature(raw_signature) == 'genuine'

    s = get_serial()
    if s:
        s.write(b'real\n' if is_genuine else b'fake\n')
    else:
        print("Serial not available")

    return jsonify({'genuine': is_genuine})

# def getGenuineOrNot(signature):
#     with open('signature_to_test.json', 'w') as f:
#         json.dump(signature, f)



if __name__ == "__main__":
    app.run(debug=True)
