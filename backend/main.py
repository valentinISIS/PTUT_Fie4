import os
import tempfile
import torch
from flask import Flask, request, jsonify
from transformers import AutoProcessor, SeamlessM4Tv2Model
import torchaudio
from flask_cors import CORS
import subprocess
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/transcribe": {"origins": "http://localhost:5173"}})

processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
model.eval()

# Paramètres pour le chunking
CHUNK_SIZE_SECONDS = 30  # Taille de chaque segment en secondes
SAMPLE_RATE = 16000

@app.route('/transcribe', methods=['POST'])
def process_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "Aucun fichier audio trouvé"}), 400

        audio_file = request.files['audio']

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as uploaded_temp_file:
            uploaded_wav_path = uploaded_temp_file.name
            audio_file.save(uploaded_wav_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as converted_temp_file:
            converted_wav_path = converted_temp_file.name
            try:
                subprocess.run([
                    'ffmpeg',
                    '-i', uploaded_wav_path,
                    '-acodec', 'pcm_s16le',
                    '-ac', '1',
                    '-ar', str(SAMPLE_RATE),
                    '-y',
                    converted_wav_path
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"Erreur ffmpeg: {e.stderr.decode()}")
                os.unlink(uploaded_wav_path)
                os.unlink(converted_wav_path)
                return jsonify({"error": "Erreur lors de la conversion audio"}), 500

        print(f"Fichier WAV converti : {converted_wav_path}")

        transcription = transcribe_large_audio(converted_wav_path)

        os.unlink(uploaded_wav_path)
        os.unlink(converted_wav_path)

        if transcription is not None:
            return jsonify({"transcription": transcription}), 200
        else:
            return jsonify({"error": "Erreur de transcription"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def transcribe_large_audio(file_path):
    try:
        audio_input, samplerate = torchaudio.load(file_path)
        if samplerate != SAMPLE_RATE:
            raise ValueError(f"Échantillonage incorrect: attendu {SAMPLE_RATE} Hz, obtenu {samplerate} Hz.")

        duration = audio_input.shape[1] / samplerate
        num_chunks = int(np.ceil(duration / CHUNK_SIZE_SECONDS))
        full_transcription = ""

        for i in range(num_chunks):
            start_sample = int(i * CHUNK_SIZE_SECONDS * samplerate)
            end_sample = int(min((i + 1) * CHUNK_SIZE_SECONDS * samplerate, audio_input.shape[1]))
            chunk = audio_input[:, start_sample:end_sample]

            inputs = processor(audios=chunk, sampling_rate=SAMPLE_RATE, return_tensors="pt")
            with torch.no_grad():
                output_tokens = model.generate(**inputs, tgt_lang="fra", generate_speech=False)
                transcription = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
                full_transcription += transcription + " " # Ajouter un espace entre les segments

        return full_transcription.strip()

    except Exception as e:
        print(f"Erreur lors de la transcription du fichier volumineux {file_path}: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)