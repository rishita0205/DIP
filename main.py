from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import os

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'static/processed'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.secret_key = 'super secret key'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(input_filepath, operation):
    img = cv2.imread(input_filepath)
    filename = os.path.basename(input_filepath)
    new_filename = f"{filename.split('.')[0]}_{operation}.png"
    new_filepath = os.path.join(app.config['PROCESSED_FOLDER'], new_filename)

    if operation == "cgray":
        img_processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif operation == "rotate":
        img_processed = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif operation == "cwebp":
        new_filename = f"{filename.split('.')[0]}.webp"
        new_filepath = os.path.join(app.config['PROCESSED_FOLDER'], new_filename)
        cv2.imwrite(new_filepath, img)
        return new_filename
    elif operation == "cjpg":
        new_filename = f"{filename.split('.')[0]}.jpg"
        new_filepath = os.path.join(app.config['PROCESSED_FOLDER'], new_filename)
        cv2.imwrite(new_filepath, img)
        return new_filename
    elif operation == "cpng":
        new_filename = f"{filename.split('.')[0]}.png"
        new_filepath = os.path.join(app.config['PROCESSED_FOLDER'], new_filename)
        cv2.imwrite(new_filepath, img)
        return new_filename
    else:
        img_processed = img

    cv2.imwrite(new_filepath, img_processed)
    return new_filename

@app.route("/process_chain", methods=["POST"])
def process_chain():
    data = request.get_json()
    filename = data['filename']
    operations = data['operations']
    if allowed_file(filename):
        input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        for operation in operations:
            new_filename = process_image(input_filepath, operation)
            input_filepath = os.path.join(app.config['PROCESSED_FOLDER'], new_filename)
        return jsonify({"processed_filename": new_filename})
    return jsonify({"error": "Invalid file or operation"})


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"filename": filename})
    return jsonify({"error": "Invalid file type"})

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    filename = data['filename']
    operation = data['operation']
    if allowed_file(filename):
        new_filename = process_image(filename, operation)
        return jsonify({"processed_filename": new_filename})
    return jsonify({"error": "Invalid file or operation"})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5001)