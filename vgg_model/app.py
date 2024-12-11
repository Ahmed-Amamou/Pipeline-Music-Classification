import os
import numpy as np
import pickle
import librosa
import tensorflow as tf
from flask import Flask, request, jsonify
from flask_cors import CORS

# Constants (match those in your training script)
SAMPLE_RATE = 22050
DURATION = 30
N_MELS = 224
HOP_LENGTH = 512
N_FFT = 2048

app = Flask(__name__)
CORS(app)  # Enable CORS to allow cross-origin requests

# Load the VGG model and label encoder
model = tf.keras.models.load_model('vgg19_music_classifier.h5')
with open('label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

def create_spectrogram(file):
    """Create mel-spectrogram from audio file"""
    try:
        # Load audio file
        y, sr = librosa.load(file, duration=DURATION, sr=SAMPLE_RATE)
        
        # Create mel spectrogram
        mel_spect = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_mels=N_MELS,
            n_fft=N_FFT,
            hop_length=HOP_LENGTH
        )
        
        # Convert to log scale
        mel_spect_db = librosa.power_to_db(mel_spect, ref=np.max)
        
        # Normalize
        mel_spect_norm = (mel_spect_db - mel_spect_db.min()) / (mel_spect_db.max() - mel_spect_db.min())
        
        # Resize to match VGG19 input size (224x224)
        if mel_spect_norm.shape[1] < 224:
            pad_width = 224 - mel_spect_norm.shape[1]
            mel_spect_norm = np.pad(mel_spect_norm, ((0,0), (0,pad_width)), mode='constant')
        else:
            mel_spect_norm = mel_spect_norm[:, :224]
        
        # Stack the same spectrogram 3 times to create 3 channels
        mel_spect_norm = np.stack([mel_spect_norm] * 3, axis=-1)
        
        return mel_spect_norm
    
    except Exception as e:
        print(f"Error processing audio file: {str(e)}")
        return None

@app.route('/predict', methods=['POST'])
def predict():
    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    try:
        # Create spectrogram
        spectrogram = create_spectrogram(file)
        
        if spectrogram is None:
            return jsonify({'error': 'Unable to process the audio file'}), 400
        
        # Reshape for prediction (add batch dimension)
        spectrogram = np.expand_dims(spectrogram, axis=0)
        
        # Make prediction
        prediction = model.predict(spectrogram)
        
        # Get the predicted genre and confidence
        predicted_genre_index = np.argmax(prediction[0])
        predicted_genre = label_encoder.inverse_transform([predicted_genre_index])[0]
        confidence = float(prediction[0][predicted_genre_index])
        
        return jsonify({
            'prediction': predicted_genre,
            'confidence': confidence
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)