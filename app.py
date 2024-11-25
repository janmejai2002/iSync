from flask import Flask, render_template, request, send_file,jsonify, url_for, abort,redirect, flash
from werkzeug.utils import secure_filename
import os
from flask_socketio import SocketIO
import json
from dotenv import load_dotenv
import uuid
load_dotenv()

def save_uploaded_files():
    data = {
        'images': uploaded_images,
        'zip_files': uploaded_zip_files
    }
    with open('uploaded_files.json', 'w') as f:
        json.dump(data, f)

def load_uploaded_files():
    global uploaded_images, uploaded_zip_files
    try:
        with open('uploaded_files.json', 'r') as f:
            data = json.load(f)
            uploaded_images = data.get('images', [])
            uploaded_zip_files = data.get('zip_files', [])
    except FileNotFoundError:
        uploaded_images = []
        uploaded_zip_files = []

from flask_cors import CORS


app = Flask(__name__, static_url_path='/static')
CORS(app) 

app.secret_key=os.environ.get('FLASK_SECRET_KEY')
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
    load_uploaded_files()  # Load the saved files
    return render_template('index.html', 
                         uploaded_images=uploaded_images,
                         uploaded_zip_files=uploaded_zip_files)
# Modify your upload_image route
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

    latest_image_url = f'/static/uploads/{filename}'
    uploaded_images.append(latest_image_url)
    save_uploaded_files()  # Save after upload
    socketio.emit('new_image', latest_image_url)

    return jsonify({'image_url': latest_image_url})


@app.route('/upload_from_extension', methods=['POST'])
def upload_from_extension():
    try:
        # Detailed logging of incoming request
        print("Received upload request")
        print("Headers:", request.headers)
        print("Content Type:", request.content_type)
        print("Files:", request.files)

        # Check if file is present
        if 'file' not in request.files:
            print("No file part in the request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            print("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        # Generate a unique and safe filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Full path for saving
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the file
        file.save(file_path)
        
        print(f"File saved successfully: {file_path}")
        latest_image_url = file_path
        uploaded_images.append(latest_image_url)
        save_uploaded_files()
        socketio.emit('new_image', latest_image_url)
        return jsonify({
            'message': 'File uploaded successfully', 
            'filename': unique_filename,
            'path': file_path
        }), 200
    
    except Exception as e:
        # Print full traceback for debugging
        print("Error during file upload:")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': 'File upload failed',
            'details': str(e)
        }), 500

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
    
    if file:


        zip_filename = f"{uuid.uuid4()}{secure_filename(file.filename)}"  
        zip_filepath = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
        file.save(zip_filepath)

        uploaded_zip_files.append(f'/static/uploads/{zip_filename}')
        save_uploaded_files()  # Save after upload
        socketio.emit('new_zip', {'zip_url': f'/static/uploads/{zip_filename}'})
        
        flash('file uploaded successfully!')
        return redirect(url_for('index'))
    
    return redirect(request.url)

# Route to serve uploaded ZIP files for download
@app.route('/download_zip/<string:filename>')
def download_zip(filename):
    zip_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(zip_filepath):
        return send_file(zip_filepath, as_attachment=True)
    abort(404, 'ZIP file not found')

from flask import jsonify, send_file
import os
from img2pdf_ import stitch_all, get_document
# PDF Conversion Route
@app.route('/convert_to_pdf', methods=['POST'])
def convert_to_pdf():
    data = request.get_json()
    selected_images = data.get('selected_images', [])
    print(selected_images)
    image_paths = [os.path.join(app.root_path, 'static', 'uploads', os.path.basename(url)) for url in selected_images]
    image_paths.reverse()
    if not selected_images:
        return jsonify({'error': 'No images selected for PDF conversion'}), 400

    # Ensure all image paths are valid
    # image_paths = [os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(url)) for url in selected_images]

    try:
        combined_image = stitch_all(image_paths)
        if combined_image is None:
            return jsonify({'error': 'Failed to combine images'}), 500

        pdf_filename =  f"{str(uuid.uuid4())[0:5]}"

        # Create PDF document
        output_pdf = get_document(combined_image, pdf_filename)

        # Send the generated PDF as a response
        return send_file(output_pdf, as_attachment=True, download_name=pdf_filename)
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({'error': 'Failed to generate PDF'}), 500

@app.route('/upload_book', methods=['POST'])
def upload_book():
    if 'book_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    book_file = request.files['book_file']
    filename = secure_filename(book_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    book_file.save(file_path)

    uploaded_zip_files.append(f'/static/uploads/{filename}')
    save_uploaded_files()  # Save after upload
    socketio.emit('new_zip', {'zip_url': f'/static/uploads/{filename}'})

    return jsonify({'message': 'Book uploaded successfully'}), 200

# Route for latest image fetching
@app.route('/latest_image', methods=['GET'])
def get_latest_image():
    global latest_image_url
    if latest_image_url:
        return jsonify({'image_url': latest_image_url})
    return jsonify({'error': 'No image uploaded yet'}), 404


@app.route('/clear_images', methods=['POST'])
def clear_images():
    global uploaded_images, uploaded_zip_files
    
    # Clear the lists of uploaded files
    uploaded_images = []
    uploaded_zip_files = []
    
    # Save the empty state to the JSON file
    # save_uploaded_files()
    
    try:
        # Clear the JSON file by writing empty lists
        with open('uploaded_files.json', 'w') as f:
            json.dump({'images': [], 'zip_files': []}, f)
        socketio.emit('images_cleared')
        return jsonify({'message': 'Images cleared successfully'}), 200
    except Exception as e:
        print(f"Error clearing images : {e}")
        return jsonify({'error': 'Failed to clear images'}), 500
 

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
    
@app.before_request
def initialize():
    load_uploaded_files()

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"Flask server running at: http://{local_ip}:5000/")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)