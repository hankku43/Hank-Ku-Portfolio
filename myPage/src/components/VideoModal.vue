<template>
  <n-modal :show="show" @update:show="$emit('update:show', $event)" style="width: 90vw; max-width: 1120px;">
    <div class="modal-video-wrap">
      <video
        v-if="show"
        :src="'/videos/demo.mp4'"
        controls
        autoplay
        class="demo-video"
      ></video>
    </div>
  </n-modal>
</template>

<script setup>
import { NModal } from 'naive-ui';
defineProps(['show']);
defineEmits(['update:show']);
</script>

<style scoped>
.modal-video-wrap {
  width: 80vw;
  max-width: 1120px;
  margin: 0 auto;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}
.demo-video {
  width: 100%;
  display: block;
}
</style>
