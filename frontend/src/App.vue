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
          style="margin-bottom: 10px; margin-left: 15px; width: 120px;"
          icon="pi pi-microphone"
          iconPos="right"
        />
        <Button
          label="Transcrire"
          severity="info"
          rounded
          style="margin-left: 15px; width: 120px;"
          icon="pi pi-microchip-ai"
          iconPos="right"
        />
      </div>

      <div class="transcription">
        <Card>
          <template #title>Transcription</template>
          <template #content>
            <p class="m-0">
              Lorem ipsum dolor sit amet, consectetur adipisicing elit.
              Inventore sed consequuntur error repudiandae numquam deserunt
              quisquam repellat libero asperiores earum nam nobis, culpa ratione
              quam perferendis esse, cupiditate neque quas!
            </p>
          </template>
        </Card>

        <Button
          label="Télécharger"
          severity="info"
          rounded
          style="margin: 10px; width: 120px;"
          icon="pi pi-file-import"
          iconPos="right"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { Menubar, Button, Card } from "primevue";
const items = ref([
  {
    image: "/logo.jpg",
    url: "/",
  },
]);
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
.transcription {
  width: 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

</style>
