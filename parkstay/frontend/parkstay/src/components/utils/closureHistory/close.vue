<template id="Close">
    <bootstrapModal :title="title" :large="true" @ok="addClosure()" @cancel="close()" :isModalOpen='isModalOpen'>

        <div class="modal-body">
            <form name="closeForm" class="form-horizontal">
                <div class="row">
                    <alert v-model:show="showError" type="danger">{{ errorString }}</alert>
                    <div class="form-group">
                        <div class="col-md-6">
                            <label class="form-label required">
                                <span class="bi bi-calendar3"></span>
                                Closure start:
                            </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' :id='close_cg_range_start'>
                                <input name="closure_start" v-model="statusHistoryRef.range_start" type='text' class="form-control" autocomplete="off"/>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-6">
                            <label class="form-label">
                                <span class="bi bi-calendar3"></span>
                                Reopen on:
                            </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' :id='close_cg_range_end'>
                                <input name="closure_end" v-model="statusHistoryRef.range_end" type='text' class="form-control" autocomplete="off"/>
                            </div>
                        </div>
                    </div>
                </div>
                <reason type="close" v-model="statusHistoryRef.closure_reason" :required="true"></reason>
                <div v-show="requireDetails" class="row">
                    <div class="form-group">
                        <div class="col-md-6">
                            <label class="form-label required">Details: </label>
                        </div>
                        <div class="col-md-4">
                            <textarea name="closure_details" v-model="statusHistoryRef.details" class="form-control"
                                id="close_cg_details"></textarea>
                        </div>
                    </div>
                </div>
            </form>
        </div>

    </bootstrapModal>
</template>

<script setup>
import { $, getDateTimePicker, dateUtils, helpers, Moment } from '../../../hooks.js'
import bootstrapModal from '../bootstrap-modal.vue'
import alert from '../alert.vue'
import reason from '../reasons.vue'
import { computed, onMounted, ref, watch } from 'vue'

const props = defineProps({
    statusHistory: {
        type: Object,
        required: true,
    },
    title: {
        type: String,
        required: true
    }
})

const emits = defineEmits(['inFocus', 'submit'])

const id = ref('')
const uid = crypto.randomUUID();
const close_cg_range_start = 'close_cg_range_start' + uid
const close_cg_range_end = 'close_cg_range_end' + uid
const current_closure = ref('')
const showDetails = ref(false)
const errors = ref(false)
const errorString = ref('')
const form = ref(null);
const statusHistoryRef = ref({
    id: '',
    range_start: '',
    range_end: '',
    status: '',
    details: '',
    reason: '',
    closure_reason: '',
})
const isOpen = ref(false)
const closeStartPicker = ref(null)
const closeEndPicker = ref(null)


const showError = computed(function () {
    return errors.value;
})
const isModalOpen = computed(function () {
    return isOpen.value;
})
const closure_id = computed(function () {
    return statusHistoryRef.value.id ? statusHistoryRef.value.id : '';
})
const requireDetails = computed(function () {
    return statusHistoryRef.value.closure_reason === 1;
})

watch(() => isOpen.value, (val) => {
    if (val) {
        statusHistoryRef.value = props.statusHistory
        if (statusHistoryRef.value.range_start) {
            closeStartPicker.value.updateOptions({
                defaultDate: moment(statusHistoryRef.value.range_start, "DD/MM/YYYY").toDate(),
            });
        }
        if (statusHistoryRef.value.range_end) {
            closeEndPicker.value.updateOptions({
                defaultDate: moment(statusHistoryRef.value.range_end, "DD/MM/YYYY").toDate(),
            });
        }
    }
    helpers.formUtils.resetFormValidation(form.value)
})

const close = function () {
    errors.value = false;
    errorString.value = '';
    isOpen.value = false;
    statusHistoryRef.value.id = '';
    statusHistoryRef.value.range_start = '';
    statusHistoryRef.value.range_end = '';
    statusHistoryRef.value.status = '1';
    statusHistoryRef.value.details = '';
    statusHistoryRef.value.reason = '';
    statusHistoryRef.value.closure_reason = '';

    closeEndPicker.value.clear();
    closeStartPicker.value.clear();
}
const addClosure = function () {
    if (form.value.valid()) {
        if (!closure_id.value) {
            emits('closeRange');
        } else {
            emits('updateRange');
        }
    }
}
const addFormValidations = function () {
    form.value.validate({
        rules: {
            closure_start: "required",
            closure_reason: "required",
            closure_details: {
                required: {
                    depends: function (el) {
                        return requireDetails;
                    }
                }
            }
        },
        messages: {
            closure_start: "Enter a start date",
            closure_reason: "Select a closure reason from the options",
            closure_details: "Details required if Other reason is selected"
        },
        showErrors: helpers.formUtils.utilShowFormErrors
    });
}

onMounted(() => {
    statusHistoryRef.value.status = 1;
    statusHistoryRef.value.reason = '';

    form.value = $(document.forms.closeForm)
    const closeStartPickerElement = $('#' + close_cg_range_start)
    const closeEndPickerElement = $('#' + close_cg_range_end)
    closeStartPicker.value = getDateTimePicker(closeStartPickerElement, {
        restrictions: { minDate: new Date() }
    });
    closeEndPicker.value = getDateTimePicker(closeEndPickerElement, {
        useCurrent: false
    });
    closeStartPickerElement.on('change.td', function (e) {
        const date = closeStartPicker.value.dates.lastPicked;
        statusHistoryRef.value.range_start = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
        if (date) {
            closeEndPicker.value.updateOptions({
                restrictions: { minDate: date }
            });
        }
    });
    closeEndPickerElement.on('change.td', function (e) {
        const date = closeEndPicker.value.dates.lastPicked;
        statusHistoryRef.value.range_end = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    });

    addFormValidations();

})

defineExpose({ close, closure_id, statusHistoryRef, isOpen, errors, errorString })

</script>
