<template>
  <div v-show="showError" :class="{
    'alert': true,
    'alert-success': (type == 'success'),
    'alert-warning': (type == 'warning'),
    'alert-info': (type == 'info'),
    'alert-danger': (type == 'danger'),
    'top': (placement === 'top'),
    'top-right': (placement === 'top-right')
  }" transition="fade" :style="{ width: width }" role="alert">
    <button v-show="dismissable" type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"@click="showError = false"></button>
    <slot></slot>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
const props = defineProps({
  type: {
    type: String
  },
  dismissable: {
    type: Boolean,
    default: false
  },
  show: {
    type: Boolean,
    default: false,
  },
  duration: {
    type: Number,
    default: 0
  },
  width: {
    type: String
  },
  placement: {
    type: String
  }
})

const showError = ref(props.show)

const onShow = (value) => {
  showError.value = value === true
}

const afterShow = (val) => {
  if (val && Boolean(props.duration)) {
    setTimeout(() => { showError.value = false }, props.duration)
  }
}

defineExpose({ onShow })

watch(
  () => props.show,
  (val) => {showError.value = val}
)

watch(
  () => showError.value,
  afterShow
)
</script>

<style>
.fade-transition {
  transition: opacity .3s ease;
}

.fade-enter,
.fade-leave {
  height: 0;
  opacity: 0;
}

.alert.top {
  position: fixed;
  top: 30px;
  margin: 0 auto;
  left: 0;
  right: 0;
  z-index: 1050;
}

.alert.top-right {
  position: fixed;
  top: 30px;
  right: 50px;
  z-index: 1050;
}
</style>
