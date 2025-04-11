import os
import base64
import uuid
from flask import Flask, redirect, request, render_template, send_file, jsonify
from PIL import Image
from io import BytesIO
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from supabase import create_client, Client
from flask_cors import CORS  # type: ignore
from datetime import timedelta
from flask import Flask, session

# === Flask App Setup ===
app = Flask(__name__)
CORS(app)  # Optional, useful during development with frontend frameworks

UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Gemini API Setup ===
API_KEY = "AIzaSyBZEgzKt0gYQLjKnZeDW8F9Ixe9AMFRKzY"
genai_client = genai.Client(api_key=API_KEY)

# === Options ===
color_options = ['olive green', 'navy blue', 'black', 'gray', 'beige', 'white', 'sky blue']
pattern_options = ['plain', 'stripes', 'checks']

# === Routes ===

@app.route("/", methods=["GET"])
def home():
    return render_template("tryon.html", 
                           image_path=None,
                           color_options=color_options,
                           pattern_options=pattern_options)

@app.route("/upload-image", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    filename = f"{uuid.uuid4().hex}_{image.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image.save(filepath)

    return jsonify({
        "image_path": "/" + filepath,  # So frontend can access it
        "detected_items": ['shirt', 'pant'],  # Optional stub
        "color_options": color_options,
        "pattern_options": pattern_options
    })

@app.route("/apply-style", methods=["POST"])
def apply_style():
    image_path = request.form.get("image_path")
    selected_items = request.form.getlist("selected_items[]")
    selected_color = request.form.get("selected_color")
    selected_pattern = request.form.get("selected_pattern")

    if not all([image_path, selected_items, selected_color, selected_pattern]):
        return jsonify({"error": "Missing required fields"}), 400

    abs_image_path = image_path.strip("/")  # To get file path on server
    img = Image.open(abs_image_path).resize((512, 512))

    prompt_parts = ["Keep face, pose, background the same."]
    if 'shirt' in selected_items:
        prompt_parts.append(f"Change shirt to {selected_color} with {selected_pattern} pattern.")
    if 'pant' in selected_items:
        prompt_parts.append(f"Change pants to {selected_color} with {selected_pattern} pattern.")
    prompt = " ".join(prompt_parts)

    response = genai_client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=[prompt, img],
        config=types.GenerateContentConfig(response_modalities=["text", "image"])
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            output_data = base64.b64decode(part.inline_data.data)
            result_filename = f"{uuid.uuid4().hex}_styled.png"
            result_path = os.path.join(OUTPUT_FOLDER, result_filename)
            with open(result_path, "wb") as f:
                f.write(output_data)
            return jsonify({"output_url": "/" + result_path})

    return jsonify({"error": "Image generation failed"}), 500

# === Run Server ===
if __name__ == '__main__':
    app.run(debug=True)
