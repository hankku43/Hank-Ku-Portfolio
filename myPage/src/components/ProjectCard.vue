<template>
  <n-card class="qa-card glass" hoverable>
    <template #header>
      <div class="project-header">
        <span class="project-tag">{{ project.tag }}</span>
        <h3 class="card-title">{{ project.name }}</h3>
      </div>
    </template>
    <div class="card-body">
      <p>{{ project.desc }}</p>
    </div>
  </n-card>
</template>

<script setup>
import { NCard } from 'naive-ui';
defineProps({
  project: Object
});
</script>

<style scoped>


/* 這裡放原本 .qa-card, .glass, .project-tag 的樣式 */
.glass { background: transparent; transition: all 0.4s; }
.glass :deep(.n-card__body) { 
  background: rgba(255, 255, 255, 0.5) !important; 
  border-radius: 12px; 
}
.mode-dark .glass :deep(.n-card__body) { background: rgba(7, 18, 38, 0.5) !important; }

.project-tag {
  font-size: 12px; color: #3b82f6; 
  background: rgba(59, 130, 246, 0.1);
  padding: 2px 8px; border-radius: 8px;
}
/* ... 其他相關 Card 樣式 ... */
</style>