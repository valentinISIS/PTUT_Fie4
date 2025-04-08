import os
import tempfile
import torch
from flask import Flask, request, jsonify
from transformers import AutoProcessor, SeamlessM4Tv2Model
import torchaudio
from flask_cors import CORS
import subprocess

# Initialisation de Flask
app = Flask(__name__)

# Autoriser les requêtes CORS depuis n'importe quelle origine
CORS(app, resources={r"/transcribe": {"origins": "http://localhost:5173"}})

# Charger le modèle et le processeur SeamlessM4Tv2
processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
model.eval()

@app.route('/transcribe', methods=['POST'])
def process_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "Aucun fichier audio trouvé"}), 400

        audio_file = request.files['audio']

        # Créer un fichier temporaire pour le fichier uploadé
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as uploaded_temp_file:
            uploaded_wav_path = uploaded_temp_file.name
            audio_file.save(uploaded_wav_path)

        # Créer un fichier temporaire pour le fichier converti
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as converted_temp_file:
            converted_wav_path = converted_temp_file.name

            # Convertir l'audio en PCM 16 kHz mono avec ffmpeg
            try:
                subprocess.run([
                    'ffmpeg',
                    '-i', uploaded_wav_path,
                    '-acodec', 'pcm_s16le',
                    '-ac', '1',
                    '-ar', '16000',
                    '-y',  # Overwrite output file if it exists
                    converted_wav_path
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de la conversion avec ffmpeg: {e.stderr.decode()}")
                os.unlink(uploaded_wav_path)
                os.unlink(converted_wav_path)
                return jsonify({"error": "Erreur lors de la conversion audio"}), 500

        print(f"Fichier WAV converti : {converted_wav_path}")

        # Transcrire l'audio converti
        transcription = transcribe_audio(converted_wav_path)

        # Nettoyer les fichiers temporaires
        #os.unlink(uploaded_wav_path)
        #os.unlink(converted_wav_path)

        if transcription is not None:
            return jsonify({"transcription": transcription}), 200
        else:
            return jsonify({"error": "Erreur de transcription"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def transcribe_audio(file_path):
    try:
        print(f"Tentative de chargement de : {file_path}")
        audio_input, samplerate = torchaudio.load(file_path)
        print(f"Audio chargé avec samplerate : {samplerate}")
        if samplerate != 16000:
            raise ValueError(f"Le modèle Seamless nécessite un audio échantillonné à 16 kHz, mais le fichier a {samplerate} Hz.")
        audio_inputs = processor(audios=audio_input, sampling_rate=16000, return_tensors="pt")
        with torch.no_grad():
            output_tokens = model.generate(**audio_inputs, tgt_lang="fra", generate_speech=False)
            transcription = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
        return transcription
    except Exception as e:
        print(f"Erreur lors de la transcription de {file_path}: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)