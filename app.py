from flask import Flask, request, render_template, send_file, redirect, url_for,send_from_directory
import os
import zipfile
from werkzeug.utils import secure_filename
from flask_sslify import SSLify
from OpenSSL import SSL


app = Flask(__name__)
sslify = SSLify(app)

UPLOAD_FOLDER = 'zdjecia'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_images():
    file_paths = [os.path.join(app.config['UPLOAD_FOLDER'], filename) for filename in os.listdir(app.config['UPLOAD_FOLDER'])]
    with zipfile.ZipFile('zdjecia.zip', 'w') as zip_file:
        for file_path in file_paths:
            zip_file.write(file_path, os.path.basename(file_path))

#@app.route('/')
#def index():
#   return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Brak pliku w formularzu!'
    
    files = request.files.getlist('file')

    for file in files:
        if file.filename == '':
            return 'Brak wybranego pliku!'
        
        if file and allowed_file(file.filename):
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            return 'Niedozwolone rozszerzenie pliku!'
    
    # Po zakończeniu przesyłania, kompresujemy przesłane pliki
    compress_images()
    
    # Przekierowanie użytkownika na stronę główną po przesłaniu plików
    return redirect(url_for('gallery'))

@app.route('/download')
def download_zip():
    return send_file('zdjecia.zip', as_attachment=True)
@app.route('/')
def gallery():
    images = os.listdir('zdjecia')
    return render_template('gallery.html', images=images)

@app.route('/images/<path:path>')
def send_image(path):
    return send_from_directory('zdjecia', path)
if __name__ == '__main__':
    context = ('ssl/certyfikat.crt', 'ssl/private.key')
    app.run(host='0.0.0.0', port=443, ssl_context=context)