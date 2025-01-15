<template id="bootstrap-modal">
    <div v-show="show" :transition="transition">
        <div class="modal" @click.self="clickMask">
            <div class="modal-dialog" :class="modalClass">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <slot name="title">
                                {{ title }}
                            </slot>
                        </h5>
                        <button type="button" class="btn btn-default" data-dismiss="modal" aria-label="Close"
                            @click="cancel">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <!--Header-->
                    <!--                     <slot name="header">
                        <div class="modal-header">
                            <button type="button" class="close" aria-label="Close" @click="cancel"><span
                                    aria-hidden="true">&times;</span></button>
                            <h4 class="modal-title">
                                <slot name="title">
                                    {{ title }}
                                </slot>
                            </h4>
                        </div>
                    </slot> -->
                    <!--Container-->
                    <div class="modal-body">
                        <slot></slot>
                    </div>
                    <!--Footer-->
                    <div class="modal-footer">
                        <slot name="footer">
                            <button v-if="showOK" id="okBtn" type="button" :class="okClass" @click="ok">{{ okText
                                }}</button>
                            <button v-if="showCancel" type="button" :class="cancelClass" @click="cancel">{{ cancelText
                                }}</button>
                        </slot>
                    </div>
                </div>
            </div>
        </div>
        <div class="modal-backdrop show"></div>
    </div>
</template>

<script setup>

import { computed, onUnmounted, ref, watch } from 'vue';

/**
 * Bootstrap Style Modal Component for Vue
 * Depend on Bootstrap.css
 */
const emit = defineEmits(['ok', 'cancel'])
const props = defineProps({
    title: {
        type: String,
        default: 'Modal'
    },
    small: {
        type: Boolean,
        default: false
    },
    large: {
        type: Boolean,
        default: false
    },
    full: {
        type: Boolean,
        default: false
    },
    force: {
        type: Boolean,
        default: false
    },
    transition: {
        type: String,
        default: 'modal'
    },
    showOK: {
        type: Boolean,
        default: true
    },
    showCancel: {
        type: Boolean,
        default: true
    },
    okText: {
        type: String,
        default: 'OK'
    },
    cancelText: {
        type: String,
        default: 'Cancel'
    },
    okClass: {
        type: String,
        default: 'btn btn-primary'
    },
    cancelClass: {
        type: String,
        default: 'btn btn-danger btn-outline'
    },
    closeWhenOK: {
        type: Boolean,
        default: false
    },
    isModalOpen: {
        type: Boolean,
        default: false
    }
});
const duration = ref(null);

const modalClass = computed(() => {
    return {
        'modal-lg': props.large,
        'modal-sm': props.small,
        'modal-full': props.full
    }
});
const show = computed(() => {
    return props.isModalOpen;
})

defineExpose({ isModalOpen: props.isModalOpen  })

onUnmounted(() => {
    document.body.className = document.body.className.replace(/\s?modal-open/, '');
})

/*     created() {
        if (this.show) {
            document.body.className += ' modal-open';
        }
    }, */
const ok = function () {
    emit('ok');
    if (props.closeWhenOK) {
        show.value = false;
    }
}
const cancel = function () {
    emit('cancel');
}
const clickMask = function () {
    if (!props.force) {
        cancel();
    }
}

watch(() => show, function (value) {
    if (value) {
        document.body.className += ' modal-open';
    } else {
        window.setTimeout(() => {
            document.body.className = document.body.className.replace(/\s?modal-open/, '');
        }, duration.value || 0);
    }
})

</script>


<style scoped>
.modal {
    display: block;
}

.modal .btn {
    margin-bottom: 0px;
}

.modal-body,
.modal-footer,
.modal-header {
    background-color: #F5F5F5;
    color: #333333;
}

.modal-transition {
    transition: all .6s ease;
}

.modal-leave {
    border-radius: 1px !important;
}

.modal-transition .modal-dialog,
.modal-transition .modal-backdrop {
    transition: all .5s ease;
}

.modal-enter .modal-dialog,
.modal-leave .modal-dialog {
    opacity: 0;
    transform: translateY(-30%);
}

.modal-enter .modal-backdrop,
.modal-leave .modal-backdrop {
    opacity: 0;
}

#okBtn {
    margin-bottom: 0px;
}
</style>
