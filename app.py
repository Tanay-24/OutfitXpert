from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, session
import os
import base64
from PIL import Image
from werkzeug.utils import secure_filename
import uuid
from google import genai
from google.genai import types
from supabase import create_client, Client
from flask_cors import CORS
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow frontend to talk to backend
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=1)

# Supabase credentials
SUPABASE_URL = "https://mzynuqwtyavpghgwbjut.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16eW51cXd0eWF2cGdoZ3dianV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIyMTMzNzAsImV4cCI6MjA1Nzc4OTM3MH0.aHu5ymolJxMwcNztAhWtyAtqWn6X50B9ScuQPJwgv_Q"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Gemini client setup
API_KEY = "AIzaSyBZEgzKt0gYQLjKnZeDW8F9Ixe9AMFRKzY"
genai_client = genai.Client(api_key=API_KEY)

# Directories
UPLOAD_FOLDER = "uploads"
STATIC_UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Styling options
color_options = ['olive green', 'navy blue', 'black', 'gray', 'beige', 'dark brown', 'white', 'sky blue', 'red', 'charcoal']
pattern_options = ['plain', 'stripes', 'checks', 'floral', 'graphic', 'denim style']
type_options = ['formal', 'casual', 'jeans', 'chinos']
change_options = ['Shirt only', 'Pants only', 'Shirt and Pants']

# Auth
# Redirect to Google Auth
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")

    if not email or not password or not full_name:
        return jsonify({"error": "All fields are required."}), 400

    try:
        # Sign up user with Supabase
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name
                }
            }
        })

        user = response.user
        if user:
            session["user_id"] = user.id
            session["username"] = full_name
            session["generation_count"] = 0
            return jsonify({"message": "Signup successful!"}), 200
        else:
            return jsonify({"error": "Signup failed."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        user = result.user
        session["user_id"] = user.id
        session["username"] = user.user_metadata.get("full_name", "User")
        session["generation_count"] = 0

        return jsonify({
            "message": "Login successful!",
            "username": session["username"]
        }), 200

    except Exception as e:
        return jsonify({"error": "Invalid credentials or login error."}), 401


@app.route("/login/google")
def login_google():
    redirect_url = "http://localhost:5000/welcome"
    url = f"{SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to={redirect_url}"
    return redirect(url)


@app.route("/finalize_google_login", methods=["POST"])
def finalize_google_login():
    data = request.json
    access_token = data.get("access_token")
    if not access_token:
        return jsonify({"error": "Access token missing"}), 400

    try:
        user_info = supabase.auth.get_user(access_token)
        user = user_info.user
        session["user_id"] = user.id
        session["username"] = user.user_metadata.get("full_name", "User")
        session["generation_count"] = 0
        return jsonify({
            "message": "Google login successful!",
            "username": session["username"]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401


# Route to handle the logout
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()  # Clear the session when logging out
    return redirect(url_for('index'))  # Redirect to the index page after logout
    
# Index/Home Route
@app.route("/", methods=["GET", "POST"])
def index():
    output_image_path = None
    output_filename = None
    message = None
    output_image_paths = []  # For storing paths of all generated images

    if request.method == "POST":
        session.permanent = True
        session["generation_count"] = session.get("generation_count", 0) + 1

        if session["generation_count"] > 2:
            message = "You've reached your free limit. Please log in to generate more outfits."
            return render_template("index.html", color_options=color_options, pattern_options=pattern_options,
                                   type_options=type_options, change_options=change_options, output_image_path=None,
                                   output_images=[], output_filename=None, message=message)

        image_file = request.files["image"]
        change = request.form.get("change")
        shirt_color = request.form.get("shirt_color")
        shirt_pattern = request.form.get("shirt_pattern")
        shirt_type = request.form.get("shirt_type")
        pant_color = request.form.get("pant_color")
        pant_pattern = request.form.get("pant_pattern")
        pant_type = request.form.get("pant_type")

        if image_file:
            prompt = "Keep everything including the pose, background, face, and existing clothing unchanged."
            if change == "Shirt only":
                prompt = f"Keep everything the same except the shirt. Change the shirt to {shirt_color}, {shirt_pattern}, {shirt_type}."
            elif change == "Pants only":
                prompt = f"Keep everything the same except the pants. Change the pants to {pant_color}, {pant_pattern}, {pant_type}."
            elif change == "Shirt and Pants":
                prompt = f"Keep face, background, and pose the same. Change shirt to {shirt_color}, {shirt_pattern}, {shirt_type} and pants to {pant_color}, {pant_pattern}, {pant_type}."

            try:
                img_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
                image_file.save(img_path)
                img = Image.open(img_path)

                # Generate multiple outfit variations
                for i in range(3):  # Adjust the number of variations as needed
                    modified_prompt = f"{prompt} (Variation {i + 1})"
                    response = genai_client.models.generate_content(
                        model="gemini-2.0-flash-exp-image-generation",
                        contents=[modified_prompt, img],
                        config=types.GenerateContentConfig(response_modalities=["text", "image"])
                    )

                    for part in response.candidates[0].content.parts:
                        if part.inline_data:
                            output_data = base64.b64decode(part.inline_data.data)
                            output_filename = f"styled_output_{i + 1}.png"
                            output_image_path = f"/static/outputs/{output_filename}"
                            with open(os.path.join(OUTPUT_FOLDER, output_filename), "wb") as f:
                                f.write(output_data)
                            output_image_paths.append(output_image_path)

            except Exception as e:
                print(f"Error: {e}")

    output_images = [f"/{OUTPUT_FOLDER}/{f}" for f in os.listdir(OUTPUT_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    return render_template("index.html", color_options=color_options, pattern_options=pattern_options,
                           type_options=type_options, change_options=change_options,
                           output_image_path=output_image_path, output_images=output_images,
                           output_filename=output_filename, message=message, output_image_paths=output_image_paths)

# Download
@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    return send_file(path, mimetype='image/png', as_attachment=True, download_name=filename) if os.path.exists(path) else ("File not found", 404)

# Clear output history
@app.route("/clear-history", methods=["POST"])
def clear_history():
    try:
        for file in os.listdir(OUTPUT_FOLDER):
            if file.endswith(('.png', '.jpg', '.jpeg')):
                os.remove(os.path.join(OUTPUT_FOLDER, file))
        return "History cleared", 200
    except Exception as e:
        return f"Error: {e}", 500

# Welcome Page
@app.route("/welcome")
def welcome():
    username = session.get("username", "User")
    return render_template("welcome.html", username=username)

@app.route("/update_options")
def update_options():
    category = request.args.get("category", "men").lower()
    selected = fashion_options.get(category, fashion_options["men"])

    return jsonify({
        "color_options": selected["color"],
        "pattern_options": selected["pattern"],
        "type_options": selected["type"]
    })

fashion_options = {
    "men": {
        "color": ['olive green', 'navy blue', 'black', 'gray', 'beige', 'dark brown', 'white', 'sky blue', 'red', 'charcoal'],
        "pattern": ['plain', 'stripes', 'checks', 'floral', 'graphic', 'denim style'],
        "type": ['formal', 'casual', 'jeans', 'chinos']
    },
    "women": {
        "color": ['rose pink', 'lavender', 'mint green', 'ivory', 'peach', 'coral', 'teal', 'gold', 'wine red', 'turquoise', 'maroon', 'silver', 'bronze', 'fuchsia', 'champagne'],
        "pattern": ['floral', 'paisley', 'polka dots', 'lace', 'abstract', 'animal print', 'embroidered', 'mesh', 'glitter', 'sequin', 'tie-dye', 'chevron', 'pleated', 'satin', 'geometric'],
        "type": ['blouse', 'dress', 'kurti', 'skirt', 'saree', 'gown', 'jumpsuit', 'lehenga', 'top', 'jeans', 'salwar', 'palazzo', 'shrug', 'crop top', 'tunic']
    },
    "children": {
        "color": ['baby blue', 'lemon yellow', 'mint green', 'peach', 'sky blue', 'light pink', 'lavender', 'aqua', 'teal', 'bright red', 'purple', 'lime green', 'tan', 'cream', 'orange'],
        "pattern": ['cartoon', 'animal print', 'dots', 'stripes', 'floral', 'superhero', 'clouds', 'stars', 'rainbow', 'blocks', 'vehicles', 'toys', 'nature', 'character print', 'camouflage'],
        "type": ['romper', 'jumpsuit', 't-shirt', 'shorts', 'dungaree', 'hoodie', 'frock', 'pajamas', 'jacket', 'coat', 'sweater', 'joggers', 'skirt', 'onesie', 'vest']
    },
    "girls": {
        "color": ['pink', 'purple', 'white', 'peach', 'blue', 'yellow', 'mint', 'coral', 'red', 'green', 'aqua', 'lavender', 'rose gold', 'sky blue', 'beige'],
        "pattern": ['hearts', 'unicorn', 'fairy', 'glitter', 'floral', 'frills', 'princess', 'cartoon', 'abstract', 'rainbow', 'dots', 'animals', 'lace', 'stripes', 'shiny'],
        "type": ['frock', 'dress', 'skirt', 'top', 'gown', 'jumpsuit', 'jeans', 'leggings', 'kurti', 'jacket', 'shrug', 'blouse', 'palazzo', 'hoodie', 'onesie']
    },
    "boys": {
        "color": ['blue', 'green', 'red', 'gray', 'yellow', 'white', 'black', 'navy', 'orange', 'brown', 'olive', 'aqua', 'mustard', 'cream', 'maroon'],
        "pattern": ['stripes', 'checks', 'superhero', 'vehicles', 'cartoon', 'animals', 'graphic', 'camouflage', 'stars', 'dots', 'solid', 'characters', 'sports', 'robots', 'plaid'],
        "type": ['shirt', 't-shirt', 'jacket', 'hoodie', 'sweater', 'shorts', 'jeans', 'joggers', 'tracksuit', 'vest', 'coat', 'kurta', 'blazer', 'dungaree', 'pajamas']
    }
}

color_options = ['olive green', 'navy blue', 'black', 'gray', 'beige', 'dark brown', 'white', 'sky blue', 'red', 'charcoal']
pattern_options = ['plain', 'stripes', 'checks', 'floral', 'graphic', 'denim style']
type_options = ['formal', 'casual', 'jeans', 'chinos']
change_options = ['Shirt only', 'Pants only', 'Shirt and Pants', 'Jacket only', 'Hat only', 'Shirt, Pants, Jacket and Hat']

@app.route("/tryon", methods=["GET", "POST"])
def tryon():
    output_image_path = None
    output_filename = None
    message = None
    output_image_paths = []  # For storing paths of all generated images

    category = request.form.get("category", "men").lower()
    selected_options = fashion_options.get(category, fashion_options["men"])

    if request.method == "POST":
        session.permanent = True
        image_file = request.files.get("image")
        change = request.form.get("change")

        if not change:
            gender = request.form.getlist("gender")
            age = request.form.getlist("age")
            message = "Simple virtual try-on submitted successfully."
            output_image_path = "static/output_image.jpg"
            output_filename = "output_image.jpg"
        else:
            # Get all clothing options for shirt, pant, jacket, hat
            options = {}
            for item in ["shirt", "pant", "jacket", "hat"]:
                options[item] = {
                    "color": request.form.get(f"{item}_color"),
                    "pattern": request.form.get(f"{item}_pattern"),
                    "type": request.form.get(f"{item}_type")
                }

            if image_file:
                prompt = "Keep everything including the pose, background, face, and existing clothing unchanged."

                if change == "Shirt only":
                    prompt = f"Keep everything the same except the shirt. Change the shirt to {options['shirt']['color']}, {options['shirt']['pattern']}, {options['shirt']['type']}."
                elif change == "Pants only":
                    prompt = f"Keep everything the same except the pants. Change the pants to {options['pant']['color']}, {options['pant']['pattern']}, {options['pant']['type']}."
                elif change == "Shirt and Pants":
                    prompt = (
                        f"Keep face, background, and pose the same. "
                        f"Change shirt to {options['shirt']['color']}, {options['shirt']['pattern']}, {options['shirt']['type']} "
                        f"and pants to {options['pant']['color']}, {options['pant']['pattern']}, {options['pant']['type']}."
                    )
                elif change == "Jacket only":
                    prompt = f"Keep everything the same except the jacket. Change the jacket to {options['jacket']['color']}, {options['jacket']['pattern']}, {options['jacket']['type']}."
                elif change == "Hat only":
                    prompt = f"Keep everything the same except the hat. Change the hat to {options['hat']['color']}, {options['hat']['pattern']}, {options['hat']['type']}."
                elif change == "Shirt, Pants, Jacket and Hat":
                    prompt = (
                        f"Keep face, background, and pose the same.\n"
                        f"Change shirt to {options['shirt']['color']}, {options['shirt']['pattern']}, {options['shirt']['type']},\n"
                        f"pants to {options['pant']['color']}, {options['pant']['pattern']}, {options['pant']['type']},\n"
                        f"jacket to {options['jacket']['color']}, {options['jacket']['pattern']}, {options['jacket']['type']},\n"
                        f"and hat to {options['hat']['color']}, {options['hat']['pattern']}, {options['hat']['type']}."
                    )

                print("Generated prompt:", prompt)

                try:
                    img_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
                    image_file.save(img_path)
                    img = Image.open(img_path)

                    # Generate multiple outfit variations
                    for i in range(3):  # Adjust the number of variations as needed
                        modified_prompt = f"{prompt} (Variation {i + 1})"
                        response = genai_client.models.generate_content(
                            model="gemini-2.0-flash-exp-image-generation",
                            contents=[modified_prompt, img],
                            config=types.GenerateContentConfig(response_modalities=["text", "image"])
                        )

                        for part in response.candidates[0].content.parts:
                            if part.inline_data:
                                output_data = base64.b64decode(part.inline_data.data)
                                output_filename = f"styled_tryon_output_{i + 1}.png"
                                output_image_path = f"/static/outputs/{output_filename}"
                                with open(os.path.join(OUTPUT_FOLDER, output_filename), "wb") as f:
                                    f.write(output_data)
                                output_image_paths.append(output_image_path)

                    message = "Your customized try-on variations are ready!"

                except Exception as e:
                    print(f"Error: {e}")
                    message = "Something went wrong while generating the styled images."

    return render_template("tryon.html",
                           fashion_options=fashion_options,
                           color_options=selected_options["color"],
                           pattern_options=selected_options["pattern"],
                           type_options=selected_options["type"],
                           category=category,
                           change_options=change_options,
                           output_image_path=output_image_path,
                           output_filename=output_filename,
                           message=message,
                           output_image_paths=output_image_paths)

if __name__ == '__main__':
    app.run(debug=True)
