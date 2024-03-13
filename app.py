from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import impedance
from impedance import preprocessing
from impedance.models.circuits import CustomCircuit
import matplotlib.pyplot as plt
from impedance.visualization import plot_nyquist
from io import BytesIO
import base64
app = Flask(__name__)
CORS(app)
@app.route("/get_image", methods=['POST'])
def hello_world():
    print(request.files)
    if 'file' not in request.files:
        return jsonify({ 'message': 'No file part in the request' }), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({ 'message': 'No file selected for uploading' }), 400
    frequencies, Z = preprocessing.readCSV(file)
    frequencies, Z = preprocessing.ignoreBelowX(frequencies, Z)
    circuit = 'R0-p(R1,C1)-p(R2-Wo1,C2)'
    initial_guess = [.01, .01, 100, .01, .05, 100, 1]
    circuit = CustomCircuit(circuit, initial_guess=initial_guess)
    circuit.fit(frequencies, Z)
    Z_fit = circuit.predict(frequencies)
    fig, ax = plt.subplots()
    plot_nyquist(Z, fmt='o', scale=10, ax=ax)
    plot_nyquist(Z_fit, fmt='-', scale=10, ax=ax)
    plt.legend(['Data', 'Fit'])
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return jsonify(text_data=circuit.parameters_.tolist(),image=image_base64)
if __name__ == "__main__":
    app.run(debug=True, port=5000)