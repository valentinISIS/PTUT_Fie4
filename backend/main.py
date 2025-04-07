import tempfile
import os
import torch
from flask import Flask, request, jsonify
from pydub import AudioSegment
from transformers import AutoProcessor, SeamlessM4Tv2Model
import torchaudio
from flask_cors import CORS

# Initialisation de Flask
app = Flask(__name__)

# Autoriser les requêtes CORS depuis n'importe quelle origine (optionnellement, vous pouvez spécifier les origines autorisées)
CORS(app, resources={r"/transcribe": {"origins": "http://localhost:5173"}})

# Charger le modèle et le processeur SeamlessM4Tv2
processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
model.eval()


def convert_audio(input_file):
    # Charger le fichier audio MP3
    print("break1")
    audio = AudioSegment.from_mp3(input_file)

    print("break2")
    # Convertir l'audio en 16 kHz et mono
    audio = audio.set_frame_rate(16000).set_channels(1)

    print("break3")
    # Créer un fichier temporaire WAV avec tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
        wav_path = temp_wav_file.name  # Le chemin du fichier temporaire

        # Exporter l'audio au format WAV dans le fichier temporaire
        audio.export(wav_path, format="wav")

    return wav_path


# Fonction pour transcrire l'audio
def transcribe_audio(file_path):
    try:
        print("breakDance1")
        # Charger l'audio
        audio_input, samplerate = torchaudio.load(file_path)

        print("breakDance2")
        # Vérifier et convertir en 16 kHz si nécessaire
        if samplerate != 16000:
            raise ValueError("Le modèle Seamless nécessite un audio échantillonné à 16 kHz.")

        print("breakDance3")
        # Préparer l'entrée pour le modèle
        audio_inputs = processor(audios=audio_input, sampling_rate=16000, return_tensors="pt")

        print("breakDance4")
        # Générer la transcription
        with torch.no_grad():
            output_tokens = model.generate(**audio_inputs, tgt_lang="fra", generate_speech=False)
            transcription = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

        return transcription
    except Exception as e:
        print(f"Erreur lors de la transcription de {file_path}: {e}")
        return None, None


@app.route('/transcribe', methods=['POST'])
def process_audio():
    try:
        # Vérifier que le fichier audio est dans la requête
        if 'audio' not in request.files:
            return jsonify({"error": "Aucun fichier audio trouvé"}), 400

        audio_file = request.files['audio']

        # Créer un fichier temporaire sécurisé
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            audio_path = temp_audio_file.name  # Le chemin du fichier temporaire
            audio_file.save(audio_path)

        print("breakpoint3")
        # Convertir l'audio en WAV 16 kHz
        wav_file = convert_audio(audio_path)

        print("breakpoint4")
        # Transcrire l'audio
        transcription = transcribe_audio(wav_file)

        print("breakpoint5")
        if transcription is not None:
            return jsonify({
                "transcription": transcription,
            })
        else:
            return jsonify({"error": "Erreur de transcription"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
