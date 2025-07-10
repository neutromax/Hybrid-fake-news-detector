# === backend.py ===
from flask import Flask, request, jsonify
import pickle
import os
from online_checker import check_news_online
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Load model and vectorizer
model_path = os.path.join("ml_model", "model.pkl")
vectorizer_path = os.path.join("ml_model", "tfidf.pkl")

with open(model_path, "rb") as m:
    model = pickle.load(m)

with open(vectorizer_path, "rb") as v:
    vectorizer = pickle.load(v)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        headline = data.get("news", "")
        if not headline:
            return jsonify({"error": "No news provided"}), 400

        # Offline prediction
        vectorized_input = vectorizer.transform([headline])
        offline_pred = model.predict(vectorized_input)[0]  # 'FAKE' or 'REAL'

        # Online check
        try:
            online_result = check_news_online(headline)  # custom checker
        except Exception as e:
            online_result = "No internet or error checking online."

        # Final decision logic
        if offline_pred == "FAKE" and "not found" in online_result.lower():
            verdict = "FAKE"
        elif offline_pred == "REAL" and "found" in online_result.lower():
            verdict = "REAL"
        else:
            verdict = "UNCERTAIN"

        return jsonify({
            "ml_prediction": offline_pred,
            "online_result": online_result,
            "final_verdict": verdict
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
