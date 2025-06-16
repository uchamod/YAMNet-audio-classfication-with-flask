# app.py
from flask import Flask, request, jsonify
import os
from yamnet_utils import predict_sound
from flask_cors import CORS
import subprocess
from werkzeug.utils import secure_filename
import uuid
import tempfile
import logging

app = Flask(__name__)
CORS(app)

#configure logging
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

# Configure a folder to temporarily store uploads
UPLOAD_FOLDER = 'temp_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "YAMNet Audio Classification API is running."

@app.route('/predict', methods=['POST'])
def predict():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

   
    # Use temporary directory that gets automatically cleaned up
    with tempfile.TemporaryDirectory(prefix='yamnet_') as temp_dir:
        try:
            # Generate unique filenames
            unique_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            base_name = os.path.splitext(filename)[0]
            
            m4a_filepath = os.path.join(temp_dir, f"{base_name}_{unique_id}.m4a")
            wav_filepath = os.path.join(temp_dir, f"{base_name}_{unique_id}.wav")

            # Save the uploaded file
            file.save(m4a_filepath)
            logger.info(f"Saved temporary file to {m4a_filepath}")
            
            # Convert using FFmpeg
            command = [
                'ffmpeg',
                '-i', m4a_filepath,
                '-y',
                '-loglevel', 'error',
                wav_filepath
            ]

            subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"Successfully converted to {wav_filepath}")
            
            # Predict using the model
            result = predict_sound(wav_filepath)
            return jsonify({'prediction': result})
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg conversion failed: {e.stderr}")
            return jsonify({'error': 'Audio conversion failed'}), 500
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
        # Temporary directory and all files are automatically cleaned up here  
  
# Cleanup function to remove old files on startup (optional)
def cleanup_old_files():
    """Remove any leftover files from previous runs"""
    if os.path.exists(UPLOAD_FOLDER):
        try:
            for filename in os.listdir(UPLOAD_FOLDER):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    logger.info(f"Removed old file: {filepath}")
        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")

if __name__ == '__main__':
    # Clean up any leftover files from previous runs
    cleanup_old_files()
    app.run(
       host='0.0.0.0',
       port=8080,
      
       )
