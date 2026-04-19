from flask import Flask, render_template, request, jsonify, redirect
import json

app = Flask(__name__)

# Redirect root to unlocked screen
@app.route('/')
def index():
    return redirect('/unlocked')

# --- Screen routes ---
@app.route('/unlocked')
def unlocked():
    return render_template('unlocked.html')

@app.route('/set-password')
def set_password():
    return render_template('set_password.html')

@app.route('/plocking')
def plocking():
    return render_template('plocking.html')

@app.route('/plocked')
def plocked():
    return render_template('plocked.html')

# --- Existing API routes (unchanged) ---
@app.route('/getSignatureSet', methods=['POST'])
def getSignatureSet():
    data = request.get_json()
    signatureSet = data['signatureSet']
    processSignature(signatureSet)
    return jsonify({'status': 'success'})

# --- New API routes for enroll/verify ---
@app.route('/enroll', methods=['POST'])
def enroll():
    data = request.get_json()
    signatures = data['signatures']
    processSignature(signatures)
    return jsonify({'message': 'Enrolled successfully'})

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    signature = data['signature']
    # TODO: plug in your SVM/DTW comparison logic here
    # match = your_comparison_function(signature)
    match = True  # placeholder
    return jsonify({'match': match, 'score': None})

def processSignature(signatureSet):
    with open('signatures.json', 'w') as f:
        json.dump(signatureSet, f)

if __name__ == "__main__":
    app.run(debug=True)