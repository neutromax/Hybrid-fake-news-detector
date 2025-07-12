from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import os
from online_checker import check_news_online  # ✅ Import fixed
from online_checker import check_news_online


# Flask app setup
app = Flask(__name__, static_folder="frontend")
CORS(app)

# Load ML model and TF-IDF vectorizer
model_path = os.path.join("ml_model", "model.pkl")
vectorizer_path = os.path.join("ml_model", "tfidf.pkl")

with open(model_path, "rb") as m:
    model = pickle.load(m)

with open(vectorizer_path, "rb") as v:
    vectorizer = pickle.load(v)

# === Serve HTML ===
@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

# === Serve GIFs (from /frontend/gifs) ===
@app.route("/gifs/<path:filename>")
def serve_gifs(filename):
    return send_from_directory(os.path.join(app.static_folder, "gifs"), filename)

# === Predict route (main logic) ===
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        headline = data.get("news", "").strip()

        if not headline:
            return jsonify({"error": "No news headline provided."}), 400

        # Offline ML prediction
        vectorized_input = vectorizer.transform([headline])
        offline_pred = model.predict(vectorized_input)[0]  # 'FAKE' or 'REAL'

        # Online similarity check
        try:
            online_result = check_news_online(headline)
        except Exception as e:
            print(f"❌ Error during online check: {e}")
            online_result = "No internet or error checking online."

        lower_online = online_result.lower()

        # 🔄 Improved verdict logic
        if "fake" in lower_online and "real" not in lower_online:
            online_verdict = "FAKE"
        elif any(word in lower_online for word in ["real", "covered", "found", "verified", "confirmed"]):
            online_verdict = "REAL"
        else:
            online_verdict = "UNCERTAIN"

        # 🧠 Final verdict: sync or fallback
        if offline_pred == online_verdict:
            verdict = offline_pred
        elif online_verdict != "UNCERTAIN":
            verdict = online_verdict
        else:
            verdict = offline_pred if offline_pred != "UNCERTAIN" else "UNCERTAIN"

        # 🔍 Log results to terminal
        print(f"\n🔍 Headline: {headline}")
        print(f"🧠 Offline Prediction: {offline_pred}")
        print(f"🌐 Online Result: {online_result}")
        print(f"✅ Final Verdict: {verdict}\n")

        return jsonify({
            "ml_prediction": offline_pred,
            "online_result": online_result,
            "final_verdict": verdict
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# === Start server ===
if __name__ == '__main__':
    app.run(debug=True)
