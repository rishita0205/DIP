from flask import Flask, render_template, request, flash, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import os

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.secret_key = 'super secret key'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    print(f"The operation is {operation} and filename is {filename}")
    img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename = f"{filename.split('.')[0]}_gray.png"
        case "cwebp": 
            newFilename = f"{filename.split('.')[0]}.webp"
        case "cjpg": 
            newFilename = f"{filename.split('.')[0]}.jpg"
        case "cpng": 
            newFilename = f"{filename.split('.')[0]}.png"
    newFilepath = os.path.join(app.config['PROCESSED_FOLDER'], newFilename)
    cv2.imwrite(newFilepath, imgProcessed if operation == "cgray" else img)
    return newFilename

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            newFilename = processImage(filename, operation)
            flash(f"Your image has been processed and is available for <a href='/{app.config['PROCESSED_FOLDER']}/{newFilename}' target='_blank'>viewing</a> or <a href='/download/{newFilename}' target='_blank'>download</a>")
            return render_template("index.html")
    return render_template("index.html")

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
