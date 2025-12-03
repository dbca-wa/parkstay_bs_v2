<template id="bulkCloseCampsites">
    <bootstrapModal title="(Temporarily) bulk close campsites" :large=true @ok="addClosure()" @cancel="close()" :isModalOpen='isModalOpen'>

        <div class="modal-body">
            <form id="bulkCloseCGForm" class="form-horizontal">
                <div class="row">
                    <alert v-model:show="showError" type="danger">{{ errorString }}</alert>
                    <div class="form-group">
                        <div class="col-md-8">
                            <label for="bcs-campsites">Campsites affected:</label>
                        </div>
                        <div class="col-md-4">
                            <select class="form-control" id="bcs-campsites" name="campsites" placeholder="" multiple
                                v-model="formdata.campsites">
                                <option v-for="c in campsites" v-bind:value="c.id">{{ c.name }} - {{ c.type }}</option>
                            </select>

                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required" for="close_bcs_range_start">
                                <span class="bi bi-calendar3"></span>
                                Closure start: 
                            </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' id='close_bcs_range_start'>
                                <input name="closure_start" id="closure_start" v-model="formdata.range_start" type='text' class="form-control" autocomplete="off"/>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label" for="close_bcs_range_end">
                                <span class="bi bi-calendar3"></span>
                                Reopen on: 
                            </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' id='close_bcs_range_end'>
                                <input name="closure_end" id="closure_end" v-model="formdata.range_end" type='text' class="form-control" autocomplete="off"/>
                            </div>
                        </div>
                    </div>
                </div>
                <reason-component type="close" ref="reason" name="closure_reason" v-model="reason" :required="true"></reason-component>
                <div v-show="requireDetails" class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label class="form-label required" for="close_bcs_details">Details: </label>
                        </div>
                        <div class="col-md-5">
                            <textarea name="closure_details" v-model="formdata.details" class="form-control"
                                id="close_bcs_details"></textarea>
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

const props = defineProps(['campsites'])

const id = ref('')
const current_closure = ref('')
const reason = ref('')
const formdata = ref({
    status: 1,
    range_start: '',
    range_end: '',
    closure_reason: '',
    details: '',
    campsites: [],
})
const closeStartPicker = ref(null)
const closeEndPicker = ref(null)
const errors = ref(false)
const isOpen = ref(false)
const errorString = ref('')
const form = ref(null)

const emit = defineEmits(['close', 'bulkCloseCampsites'])

const showError = computed(function () {
    return errors.value;
})
const requireDetails = computed(function () {
    return formdata.value.closure_reason === 1;
})
const isModalOpen = computed(function () {
    return isOpen.value;
})

watch(() => reason.value, (value) => {
    formdata.value.closure_reason = value;
})

watch(() => isOpen.value, (val) => {
    helpers.formUtils.resetFormValidation(form.value)
})

const addClosure = function () {
    
    // const validNumCampsites = formdata.value.campsites > 0
    const element = $('#bcs-campsites')
    const  validNumCampsites = $('#bcs-campsites').val().length;
    console.log("ADDCC")
    console.log(formdata.value.campsites);
    helpers.formUtils.removeErrorMessage(element)
    if (validNumCampsites > 0) {
    } else {
        helpers.formUtils.appendErrorMessage(element, 'Select the campsites to be closed')
    }
    if (form.value.valid() && validNumCampsites ) {
        emit('bulkCloseCampsites');
    }
}
const close = function () {
    emit('close');
}
const initSelectTwo = function () {
    setTimeout(function () {
        $('#bcs-campsites').select2({
            theme: 'bootstrap',
            allowClear: true,
            placeholder: "Select campsites",
            tags: false,
        }).
            on("select2:select", function (e) {
                formdata.value.campsites = $(e.currentTarget).val();
            }).
            on("select2:unselect", function (e) {
                formdata.value.campsites = $(e.currentTarget).val();
            });
    }, 100)
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

defineExpose({ isOpen })

onMounted(function () {
    const closeStartPickerElement = $('#close_bcs_range_start');
    const closeEndPickerElement = $('#close_bcs_range_end');
    closeStartPicker.value = $('#close_bcs_range_start');
    closeEndPicker.value = $('#close_bcs_range_end');
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
    form.value = $('#bulkCloseCGForm');
    addFormValidations();
    initSelectTwo();
})
</script>
