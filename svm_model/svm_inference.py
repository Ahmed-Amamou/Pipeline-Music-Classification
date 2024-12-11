import flask
from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os
import numpy as np
import librosa
import traceback
import pandas as pd

app = Flask(__name__)
CORS(app)

# Directory to store uploaded files
UPLOAD_FOLDER = './temp'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the SVM model and scaler
with open('svm_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# Audio processing constants
SAMPLE_RATE = 22050
DURATION = 30  # seconds

def extract_features(audio_path):
    """
    Extract audio features from a single audio file.
    Returns a dictionary of features matching the training process.
    """
    try:
        # Load audio file
        y, sr = librosa.load(audio_path, duration=DURATION, sr=SAMPLE_RATE)
        
        # Extract features
        features = {}
        
        # Spectral features
        features['spectral_centroids_mean'] = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0]))
        features['spectral_centroids_var'] = float(np.var(librosa.feature.spectral_centroid(y=y, sr=sr)[0]))
        
        features['spectral_rolloff_mean'] = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)[0]))
        features['spectral_rolloff_var'] = float(np.var(librosa.feature.spectral_rolloff(y=y, sr=sr)[0]))
        
        # Zero crossing rate
        features['zero_crossing_rate_mean'] = float(np.mean(librosa.feature.zero_crossing_rate(y)[0]))
        features['zero_crossing_rate_var'] = float(np.var(librosa.feature.zero_crossing_rate(y)[0]))
        
        # MFCC (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        for i in range(20):
            features[f'mfcc{i+1}_mean'] = float(np.mean(mfccs[i]))
            features[f'mfcc{i+1}_var'] = float(np.var(mfccs[i]))
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        features['chroma_mean'] = float(np.mean(chroma))
        features['chroma_var'] = float(np.var(chroma))
        
        # Tempo and rhythm features
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo)
        
        # Root Mean Square Energy
        features['rmse_mean'] = float(np.mean(librosa.feature.rms(y=y)[0]))
        features['rmse_var'] = float(np.var(librosa.feature.rms(y=y)[0]))
        
        return features
    
    except Exception as e:
        print(f"Error processing {audio_path}: {str(e)}")
        traceback.print_exc()
        return None

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if a file is in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        
        file = request.files['file']
        
        # Ensure the file has a valid filename
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Save the file to the upload folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        print(f"File uploaded and saved to: {filepath}")
        
        # Extract features from the uploaded file
        input_data = extract_features(filepath)
        
        if input_data is None:
            return jsonify({'error': 'Feature extraction failed'}), 400
        
        # Convert features to DataFrame for scaling
        
        input_df = pd.DataFrame([input_data])
        
        # Scale the features using the saved scaler
        input_scaled = scaler.transform(input_df)
        
        # Run prediction
        prediction = model.predict(input_scaled)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({'prediction': prediction.tolist()})
    
    except Exception as e:
        print("Prediction error:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)