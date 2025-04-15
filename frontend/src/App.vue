<template>
  <div class="card">
    <div>
      <Menubar :model="items" style="background-color: var(--p-teal-500)">
        <template #item="{ item, props }">
          <a v-bind="props.action">
            <img
              v-if="item.image"
              :src="item.image"
              alt="CPTS"
              class="menu-icon"
            />
          </a>
        </template>
      </Menubar>
    </div>

    <div class="content">
      <div class="actions">
        <Button
          label="Enregistrer"
          severity="info"
          rounded
          style="margin-bottom: 10px; margin-left: 15px; width: 200px"
          icon="pi pi-microphone"
          iconPos="right"
          @click="startRecording"
          :disabled="isRecording"
        />

        <div class="transcription-button">
          <Button
            label="Transcrire depuis l'application"
            severity="info"
            rounded
            style="margin-left: 15px; margin-bottom: 15px; width: 200px"
            icon="pi pi-microchip-ai"
            iconPos="right"
            @click="transcribe"
            :disabled="!isRecording || isUploading"
          />
          <input
            type="file"
            accept="audio/*"
            ref="fileInput"
            style="display: none"
            @change="uploadAndTranscribeFile"
          />
          <Button
            label="Transcrire depuis un fichier"
            severity="info"
            rounded
            style="margin-left: 15px; width: 200px"
            icon="pi pi-upload"
            iconPos="right"
            @click="() => fileInput.click()"
            :disabled="isUploading"
          />
        </div>
      </div>

      <div class="transcription">
        <Card>
          <template #title>Transcription</template>
          <template #content>
            <div
              v-if="isUploading"
              style="display: flex; flex-direction: column; align-items: center"
            >
              <div
                ref="animationContainer"
                style="width: 150px; height: 150px"
              ></div>
              <p>Transcription en cours...</p>
            </div>
            <p class="m-0" v-else-if="transcription">
              {{ transcription }}
            </p>
            <p class="m-0" v-else>En attente de transcription...</p>
          </template>
        </Card>

        <Button
          label="Télécharger"
          severity="info"
          rounded
          style="margin: 10px; width: 120px"
          icon="pi pi-file-import"
          iconPos="right"
          @click="downloadTranscription"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick  } from "vue";
import { Menubar, Button, Card } from "primevue";
import axios from "axios";
import Vue3Lottie from "vue3-lottie";
import lottie from "lottie-web";
import loadingAnimationData from "@/assets/animation/Elia.json";

const animationContainer = ref(null);
let mediaRecorder;
let audioChunks = [];
const isRecording = ref(false);
const isUploading = ref(false);
const transcription = ref("");
const fileInput = ref(null);

watch(isUploading, async (val) => {
  if (val) {
    await nextTick();

    if (animationContainer.value) {
      lottieInstance = lottie.loadAnimation({
        container: animationContainer.value,
        renderer: "svg",
        loop: true,
        autoplay: true,
        animationData: loadingAnimationData,
      });
    }
  } else {
    if (lottieInstance) {
      lottieInstance.destroy();
      lottieInstance = null;
    }
  }
});

const items = ref([
  {
    image: "/logo.jpg",
    url: "/",
  },
]);

const startRecording = async () => {
  if (isRecording.value) return;

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      sendAudioToBackend(audioBlob);
    };

    mediaRecorder.start();
    isRecording.value = true;
  } catch (error) {
  }
};

const sendAudioToBackend = async (audioBlob) => {
  try {
    isUploading.value = true;
    const formData = new FormData();
    formData.append("audio", audioBlob, "audio.wav");

    const response = await axios.post(
      "http://localhost:5000/transcribe",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    if (response.data.transcription) {
      transcription.value = response.data.transcription;
    } else {
      transcription.value = "Erreur de transcription.";
    }
  } catch (error) {
    console.error("Erreur lors de l'envoi de l'audio:", error);
    transcription.value = "Erreur lors de l'envoi de l'audio.";
  } finally {
    isUploading.value = false;
  }
};

const transcribe = () => {
  if (!isRecording.value || !mediaRecorder) return;

  mediaRecorder.stop();
  isRecording.value = false;
};

const downloadTranscription = () => {
  if (!transcription.value) {
    alert("Aucune transcription à télécharger.");
    return;
  }

  const blob = new Blob([transcription.value], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "transcription.txt";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

const uploadAndTranscribeFile = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  isUploading.value = true;
  const formData = new FormData();
  formData.append("audio", file);

  try {
    const response = await axios.post(
      "http://localhost:5000/transcribe",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    if (response.data.transcription) {
      transcription.value = response.data.transcription;
    } else {
      transcription.value = "Erreur de transcription.";
    }
  } catch (error) {
    console.error("Erreur lors de l'envoi du fichier audio:", error);
    transcription.value = "Erreur lors de l'envoi du fichier audio.";
  } finally {
    isUploading.value = false;
  }
};
</script>

<style>
.menu-icon {
  width: 50px;
  height: 50px;
}

.content {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: stretch;
  height: 100vh;
}

.actions {
  width: 50%;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-items: left;
  padding: 20px;
}
.transcription-button {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-items: left;
}
.transcription {
  width: 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
}
</style>
