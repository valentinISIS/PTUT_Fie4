import torch
from flask import Flask, request, jsonify
from pydub import AudioSegment
from transformers import AutoProcessor, SeamlessM4Tv2Model
import torchaudio

# Initialisation de Flask
app = Flask(__name__)

# Charger le modèle et le processeur SeamlessM4Tv2
processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
model.eval()


# Fonction pour convertir les fichiers MP3 en WAV 16 kHz
def convert_audio(input_file):
    audio = AudioSegment.from_mp3(input_file)
    audio = audio.set_frame_rate(16000).set_channels(1)  # Convertir en 16 kHz et mono
    temp_wav_file = "/tmp/temp_audio.wav"
    audio.export(temp_wav_file, format="wav")
    return temp_wav_file


# Fonction pour transcrire l'audio
def transcribe_audio(file_path):
    try:
        # Charger l'audio
        audio_input, samplerate = torchaudio.load(file_path)

        # Vérifier et convertir en 16 kHz si nécessaire
        if samplerate != 16000:
            raise ValueError("Le modèle Seamless nécessite un audio échantillonné à 16 kHz.")

        # Préparer l'entrée pour le modèle
        audio_inputs = processor(audios=audio_input, sampling_rate=16000, return_tensors="pt")

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

        # Sauvegarder temporairement l'audio
        audio_path = "/tmp/input_audio.mp3"
        audio_file.save(audio_path)

        # Convertir l'audio en WAV 16 kHz
        wav_file = convert_audio(audio_path)

        # Transcrire l'audio
        transcription = transcribe_audio(wav_file)

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
