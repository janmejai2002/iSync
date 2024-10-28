from flask import Flask, render_template, request, send_file,jsonify, url_for, abort,redirect, flash
from werkzeug.utils import secure_filename
import os
from flask_socketio import SocketIO, emit
import zipfile
from datetime import datetime

app = Flask(__name__)
app.secret_key="chingalinga"
socketio = SocketIO(app)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

uploaded_images = []
uploaded_zip_files = []


# Variable to store the latest uploaded image URL
latest_image_url = None

# Create folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Add logging when clients connect or disconnect
@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@app.route('/')
def index():
    current_time = datetime.now().timestamp()
    return render_template('index.html', latest_image_url=uploaded_images, uploaded_zip_files=uploaded_zip_files, current_time=current_time
    )

# Image upload route
@app.route('/upload_image', methods=['POST'])
def upload_image():
    global latest_image_url
    if 'image' not in request.files:
        abort(400, 'No file part')
    file = request.files['image']
    if file.filename == '':
        abort(400, 'No selected file')

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Store the URL of the latest image
    latest_image_url = f'/static/uploads/{filename}'
    uploaded_images.append(latest_image_url)
    # Emit the update to all connected clients
    socketio.emit('new_image', latest_image_url)  # Emit here

    return jsonify({'image_url': latest_image_url})

import socket

# Get the local IP address

# ZIP file upload route
@app.route('/upload_zip', methods=['POST'])
def upload_zip():
    if 'zip_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['zip_file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and file.filename.endswith('.zip'):
        # Save the ZIP file
        zip_filename = secure_filename(file.filename)
        zip_filepath = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
        file.save(zip_filepath)

        # Add the uploaded ZIP file to the list
        uploaded_zip_files.append(f'/static/uploads/{zip_filename}')
  # Emit an update to refresh the ZIP file list on connected clients
        socketio.emit('new_zip', {'zip_url': f'/static/uploads/{zip_filename}'})
        
        flash('ZIP file uploaded successfully!')
        return redirect(url_for('index'))  # Redirect to the upload page
    
    flash('Invalid file type. Please upload a ZIP file.')
    return redirect(request.url)

# Route to serve uploaded ZIP files for download
@app.route('/download_zip/<string:filename>')
def download_zip(filename):
    zip_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(zip_filepath):
        return send_file(zip_filepath, as_attachment=True)
    abort(404, 'ZIP file not found')

# Route for latest image fetching
@app.route('/latest_image', methods=['GET'])
def get_latest_image():
    global latest_image_url
    if latest_image_url:
        return jsonify({'image_url': latest_image_url})
    return jsonify({'error': 'No image uploaded yet'}), 404

def get_local_ip():
    try:
        # Create a socket and connect to an external address to find the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to an external DNS server
        ip_address = s.getsockname()[0]
    except Exception as e:
        print(f"Error retrieving local IP address: {e}")
        ip_address = "127.0.0.1"  # Fallback to localhost if there's an error
    finally:
        s.close()
    return ip_address
    
if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"Flask server running at: http://{local_ip}:5000/")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)