from flask import Flask, render_template,request,jsonify
import json


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/getSignatureSet', methods=['POST'])
def getSignatureSet():
    data=request.get_json()
    signatureSet=data['signatureSet']
    processSignature(signatureSet)

    return jsonify({'status':'success'})


def processSignature(signatureSet):
    with open('signatures.json', 'w') as f:
        json.dump(signatureSet, f)


if __name__ == "__main__":
    app.run(debug=True)
