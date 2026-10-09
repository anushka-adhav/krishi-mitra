from flask import Flask, request, jsonify,send_from_directory
from flask_cors import CORS
from PIL import Image
import numpy as np
import io

app = Flask(__name__,static_folder="../frontend",static_url_path="")
CORS(app)
@app.route("/")
def home():
    return send_from_directory(app.static_folder,"index.html")

def recommend_crop(rgb):
    r, g, b = rgb
    if r < 90 and g < 90 and b < 90:
        return {"soil_type": "Black Soil (Regur)", "crops": ["Cotton", "Soybean", "Sugarcane"]}
    elif r > 130 and r > g and r > b:
        return {"soil_type": "Red Soil", "crops": ["Groundnut", "Bajra", "Ragi"]}
    elif r > 150 and g > 120 and b < 120:
        return {"soil_type": "Alluvial Soil", "crops": ["Wheat", "Rice", "Sugarcane"]}
    elif r > 100 and r < 160 and g < 100:
        return {"soil_type": "Laterite Soil", "crops": ["Cashew", "Tea", "Coffee"]}
    else:
        return {"soil_type": "Mixed/Unknown Soil", "crops": ["Maize", "Pulses"]}

def get_dominant_color(image):
    image = image.resize((50, 50))
    arr = np.array(image.convert("RGB"))
    pixels = arr.reshape(-1, 3)
    return pixels.mean(axis=0)

@app.route("/predict", methods=["POST"])
def predict():
    files = request.files.getlist("image")
    if not files or len(files) == 0:
        return jsonify({"error": "No image uploaded"}), 400
    if len(files) > 3:
        return jsonify({"error": "Maximum 3 images allowed"}), 400

    all_colors = []
    for file in files:
        image = Image.open(io.BytesIO(file.read()))
        color = get_dominant_color(image)
        all_colors.append(color)

    avg_color = np.mean(all_colors, axis=0)
    rgb = tuple(int(c) for c in avg_color)

    result = recommend_crop(rgb)
    result["detected_rgb"] = rgb
    result["images_used"] = len(files)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
