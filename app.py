from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins

@app.route("/generate_resume", methods=["POST"])
def generate_resume():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    return jsonify({"resume": "Generated Resume Text"})  # Example response

if __name__ == "__main__":
    app.run(debug=True)
