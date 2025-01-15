<template id="pkCgOpen">
    <bootstrapModal title="Open campground" :large=true @ok="addOpen()" @cancel="close()" :isModalOpen='isModalOpen'>

        <div class="modal-body">
            <form id="openCGForm" class="form-horizontal">
                <div class="row">
                    <alert v-model:show="showError" type="danger"></alert>
                    <div class="form-group">
                        <div class="col-md-2">
                            <label for="open_cg_current_closure">Current Closure: </label>
                        </div>
                        <div class="col-md-4">
                            <input id='open_cg_current_closure' v-model="current_closure" disabled type='text'
                                class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label for="open_cg_range_end">Reopen on: </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date' id='open_cg_range_end'>
                                <input name="open_start" v-model="formdata.range_end" type='text'
                                    class="form-control" />
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                <reason type="close" v-model="formdata.closure_reason"></reason>
                <div v-show="requireDetails" class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label for="open_cg_details">Details: </label>
                        </div>
                        <div class="col-md-5">
                            <textarea name="open_details" v-model="formdata.details" class="form-control"
                                id="open_cg_details"></textarea>
                        </div>
                    </div>
                </div>
            </form>
        </div>

    </bootstrapModal>
</template>

<script setup>
import bootstrapModal from '../utils/bootstrap-modal.vue'
import reason from '../utils/reasons.vue'
import { $, bus, getDateTimePicker, dateUtils, api_endpoints, helpers } from '../../hooks.js'
import alert from '../utils/alert.vue'
import { computed, onMounted, ref } from 'vue'

const id = ref('')
const current_closure = ref('')
const formdata = ref({
    range_end: '',
    closure_reason: '',
    details: ''
})
const picker = ref('')
const errors = ref(false)
const isOpen = ref(false)
const errorString = ref('')
const form = ref('')

const showError = computed(function () {
    return errors.value;
})
const isModalOpen = computed(function () {
    return isOpen.value;
})
const requireDetails = computed(function () {
    return (formdata.value.closure_reason === '1');
})

const emit = defineEmits(['isOpenOpenCG', 'refreshCGTable'])

const close = function () {
    emit('isOpenOpenCG', false);
    isOpen.value = false
}
const addOpen = function () {
    if (form.value.valid()) {
        sendData();
    }
}
const sendData = function () {
    var data = formdata.value;
    const date = picker.value.dates.lastPicked
    data.range_end = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    $.ajax({
        url: api_endpoints.campground_booking_ranges_detail(id.value),
        method: 'PATCH',
        xhrFields: { withCredentials: true },
        data: data,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        dataType: 'json',
        success: function (data, stat, xhr) {
            close();
            emit('refreshCGTable');
        },
        error: function (data) {
            errors.value = true;
            errorString.value = helpers.apiError(data);
        }
    });

}
const addFormValidations = function () {
    form.value.validate({
        rules: {
            open_start: "required",
            open_reason: "required",
            open_details: {
                required: {
                    depends: function (el) {
                        return requireDetails.value;
                    }
                }
            }
        },
        messages: {
            open_start: "Enter a reopening date",
            open_reason: "Select an open reason from the options",
            open_details: "Details required if Other reason is selected"
        },
        showErrors: function (errorMap, errorList) {

            $.each(this.validElements(), function (index, element) {
                var $element = $(element);
                $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
            });

            // destroy tooltips on valid elements
            $("." + this.settings.validClass).tooltip("destroy");

            // add or update tooltips
            for (var i = 0; i < errorList.length; i++) {
                var error = errorList[i];
                $(error.element)
                    .tooltip({
                        trigger: "focus"
                    })
                    .attr("data-original-title", error.message)
                    .parents('.form-group').addClass('has-error');
            }
        }
    });
}

const clearValues = () => {
    picker.value.clear();
    formdata.value.closure_reason = "";
    formdata.value.details = "";
}

defineExpose({ formdata, isOpen, errors, errorString, close })

onMounted(function () {
    bus.on('openCG', function (data) {
        id.value = data.id;
        current_closure.value = data.closure;
        clearValues();
    });

    const pickerElement = $('#open_cg_range_end');
    picker.value = getDateTimePicker(pickerElement, {
        useCurrent: false,
        restrictions: { minDate: dateUtils.addDays(new Date(), 1) }
    });
    pickerElement.on('change.td', function (e) {
        const date = picker.value.dates.lastPicked
        formdata.value.range_end = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    });
    form.value = $('#openCGForm');
    addFormValidations();
})
</script>
