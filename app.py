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

   
    
    # Define paths for the temporary input (.m4a) and output (.wav) files
    filename = secure_filename(file.filename)
    m4a_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
      
    # Create a unique name for the WAV file to avoid conflicts
    wav_filename = os.path.splitext(filename)[0] + '.wav'
    wav_filepath = os.path.join(app.config['UPLOAD_FOLDER'], wav_filename)
    
    # filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    # file.save(filepath)

    try:
        # 1. Save the uploaded .m4a file
        file.save(m4a_filepath)
        print(f"Saved temporary file to {m4a_filepath}")
        

        # 2. Run the FFmpeg command to convert .m4a to .wav
        # The command overwrites the output file if it exists (-y)
        command = [
            'ffmpeg',
            '-i', m4a_filepath,
            '-y', # Overwrite output file if it exists
            wav_filepath
        ]
        
        print(f"Running FFmpeg command: {' '.join(command)}")
        subprocess.run(command, check=True, capture_output=True)
        print(f"Successfully converted to {wav_filepath}")

        result = predict_sound(wav_filepath)
        return jsonify({'prediction': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
          # 4. Clean up the temporary files
        print("Cleaning up temporary files...")
        if os.path.exists(m4a_filepath):
            os.remove(m4a_filepath)
        if os.path.exists(wav_filepath):
            os.remove(wav_filepath)

if __name__ == '__main__':
    app.run(
       host='0.0.0.0',
       port=8080,)
