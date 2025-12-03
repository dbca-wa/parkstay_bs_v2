<template>
    <bootstrapModal title="(Temporarily) close campsite" :large=true @ok="addClosure()" @cancel="close()" :isModalOpen='isModalOpen'>

        <div class="modal-body">
            <form id="closeCGForm" class="form-horizontal">
                <div class="row">
                    <alert v-model:show="showError" type="danger">{{ errorString }}</alert>
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required" for="open_cg_range_start">
                                <span class="bi bi-calendar3"></span>
                                Closure start: 
                            </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' id='close_cg_range_start'>
                                <input name="closure_start" v-model="formdata.range_start" type='text' class="form-control" autocomplete="off"/>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label" for="open_cg_range_start">
                                <span class="bi bi-calendar3"></span>
                                Reopen on: 
                            </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' id='close_cg_range_end'>
                                <input name="closure_end" v-model="formdata.range_end" type='text' class="form-control" autocomplete="off" />
                            </div>
                        </div>
                    </div>
                </div>
                <reason-component type="close" name="closure_reason" v-model="reason" :required="true"></reason-component>
                <div v-show="requireDetails" class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required" for="open_cg_details">Details: </label>
                        </div>
                        <div class="col-md-5">
                            <textarea name="closure_details" v-model="formdata.details" class="form-control"
                                id="close_cg_details"></textarea>
                        </div>
                    </div>
                </div>
            </form>
        </div>

    </bootstrapModal>
</template>

<script setup>
import bootstrapModal from '../../utils/bootstrap-modal.vue'
import reasonComponent from '../../utils/reasons.vue'
import { $, getDateTimePicker, dateUtils, helpers } from '../../../hooks.js'
import alert from '../../utils/alert.vue'
import { computed, onMounted, ref, watch } from 'vue'

const reason = ref('')
const formdata = ref({
    campsite: '',
    status: 1,
    range_start: '',
    range_end: '',
    closure_reason: '',
    details: ''
})
const closeStartPicker = ref('')
const closeEndPicker = ref('')
const errors = ref(false)
const errorString = ref('')
const form = ref('')
const isOpen = ref(false)

const emit = defineEmits(['closeCampsite'])

const showError = computed(function () {
    return errors.value;
})
const isModalOpen = computed(function () {
    return isOpen.value;
})
const requireDetails = computed(function () {
    return (formdata.value.closure_reason === 1);
})

watch(()=> reason, (value) => {
    formdata.value.closure_reason = value ? value.value : undefined;
}, { deep: true})

watch(() => isOpen.value, (val) => {
    helpers.formUtils.resetFormValidation(form.value)
})


const close = function () {
    isOpen.value = false;
    formdata.value = {
        status: 1,
        range_start: '',
        range_end: '',
        closure_reason: '',
        details: ''
    };
    reason.value = "";
}
const addClosure = function () {
    if (form.value.valid()) {
        emit('closeCampsite');
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
                        return requireDetails.value;
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

defineExpose({ formdata, isOpen, errors, errorString, close })

onMounted(() => {
    const closeStartPickerElement = $('#close_cg_range_start');
    const closeEndPickerElement = $('#close_cg_range_end');
    closeStartPicker.value = getDateTimePicker(closeStartPickerElement, {
        restrictions: { minDate: new Date() }
    });
    closeEndPicker.value = getDateTimePicker(closeEndPickerElement, {
        useCurrent: false
    });
    closeStartPickerElement.on('change.td', function (e) {
        const date = closeStartPicker.value.dates.lastPicked;
        formdata.value.range_start = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
        if (date) {
            closeEndPicker.value.updateOptions({
                restrictions: { minDate: date }
            });
        }
    });
    closeEndPickerElement.on('change.td', function (e) {
        const date = closeEndPicker.value.dates.lastPicked;
        formdata.value.range_end = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    });
    form.value = $('#closeCGForm');
    addFormValidations();
})

</script>
