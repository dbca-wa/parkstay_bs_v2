<template lang="html">
    <div id="bulk-close">
        <modal okText="Close Campgrounds" @ok="closeCampgrounds" @cancel="close" :force="true" :isModalOpen="isModalOpen">
            <h4 slot="title">Bulk Close Campgrounds</h4>
            <div class="body">
                <alert ref="alertRef" type="danger">{{ errorString }}</alert>
                <form name="closeForm" class="form-horizontal">
                    <div class="row">
                    <div class="form-group">
                            <div class="col-md-4">
                                <label for="bc-campgrounds">Campgrounds</label>
                            </div>
                            <div class="col-md-8">
                                <select id="bc-campgrounds" class="form-control" name="campgrounds" placeholder="" multiple
                                    v-model="selected_campgrounds">
                                    <option v-for="c in campgrounds" :value="c.id">{{ c.name }}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="form-group">
                            <div class="col-md-4">
                                <label for="open_cg_range_start">Closure start: </label>
                            </div>
                            <div class="col-md-8">
                                <div class='input-group date' :id='close_cg_range_start'>
                                    <input name="closure_start" v-model="range_start" type='text'
                                        class="form-control" autocomplete="false" />
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="form-group">
                            <div class="col-md-4">
                                <label for="open_cg_range_start">Reopen on: </label>
                            </div>
                            <div class="col-md-8">
                                <div class='input-group date' :id='close_cg_range_end'>
                                    <input name="closure_end" v-model="range_end" type='text' class="form-control" autocomplete="false" />
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <reason type="close" v-model="reasonValue" :large="true"></reason>
                    <div v-show="requireDetails" class="row">
                        <div class="form-group">
                            <div class="col-md-4">
                                <label>Details: </label>
                            </div>
                            <div class="col-md-8">
                                <textarea name="closure_details" v-model="details" class="form-control"
                                    id="close_cg_details"></textarea>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </modal>
    </div>
</template>

<script setup>
import modal from '../bootstrap-modal.vue'
import reason from '../reasons.vue'
import alert from '../alert.vue'
import { $, getDateTimePicker, dateUtils, api_endpoints, helpers } from '../../../hooks.js'
import { computed, onMounted, ref, watch } from 'vue'
import { useStore } from "../../../apps/store.js";

const store = useStore()

const uid = crypto.randomUUID();
const close_cg_range_end = 'close_cg_range_end' + uid
const close_cg_range_start = 'close_cg_range_start' + uid

const isModalOpen = ref(false)
const alertRef = ref(null)
const closeEndPicker = ref(null)
const closeStartPicker = ref(null)
const reasonValue = ref('')
const range_start = ref('')
const range_end = ref('')
const details = ref('')
const errorString = ref('')
const selected_campgrounds = ref([])
const form = ref(null)

const requireDetails = computed(function () {
    return (reasonValue.value === '1')
})
const campgrounds = computed(function () {
    return store.getters.campgrounds
})

const emits = defineEmits(['close'])

const close = function () {
    emits('close')
    clearValues()
    isModalOpen.value = false;
}

const events = function () {
    const closeStartPickerElement = $('#' + close_cg_range_start)
    const closeEndPickerElement = $('#' + close_cg_range_end);

    closeStartPicker.value = getDateTimePicker(closeStartPickerElement, {
        restrictions: { minDate: new Date() }
    });
    closeEndPicker.value = getDateTimePicker(closeEndPickerElement, {
        useCurrent: false
    });
    closeStartPickerElement.on('change.td', function (e) {
        const date = closeStartPicker.value.dates.lastPicked;
        range_start.value = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
        if (date) {
            closeEndPicker.value.updateOptions({
                restrictions: { minDate: date }
            });
        }
    });
    closeEndPickerElement.on('change.td', function (e) {
        const date = closeEndPicker.value.dates.lastPicked;
        range_end.value = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    });
    addFormValidations();
    fetchCampgrounds();
    initSelectTwo();
}
const fetchCampgrounds = function () {
    if (campgrounds.value.length == 0) {
        store.dispatch("fetchCampgrounds");
    }
}
const initSelectTwo = function () {
    setTimeout(function () {
        $('#bc-campgrounds').select2({
            theme: 'bootstrap',
            allowClear: true,
            placeholder: "Select Campgrounds",
            tags: false,
        }).
            on("select2:select", function (e) {
                selected_campgrounds.value = $(e.currentTarget).val();
            }).
            on("select2:unselect", function (e) {
                selected_campgrounds.value = $(e.currentTarget).val();
            });
    }, 100)
}
const closeCampgrounds = function () {

    if (form.value.valid() && selected_campgrounds.value.length > 0) {
        alertRef.value.onShow(false)
        let data = {
            range_start: range_start.value,
            range_end: range_end.value,
            campgrounds: selected_campgrounds.value,
            closure_reason: reasonValue.value,
            status: '1'
        }
        if (reasonValue.value == '1') {
            data.details = details.value;
        }
        $.ajax({
            url: api_endpoints.bulk_close,
            method: 'POST',
            xhrFields: { withCredentials: true },
            data: data,
            headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
            dataType: 'json',
            success: function (data, stat, xhr) {
                store.dispatch("updateAlert", {
                    visible: true,
                    type: "success",
                    message: data
                });
                close();
            },
            error: function (resp) {
                store.dispatch("updateAlert", {
                    visible: true,
                    type: "danger",
                    message: helpers.apiError(resp)
                });
                close();
            }
        });
    } else {
        errorString.value = "Please, fill in all the fields in the form"
        alertRef.value.onShow(true)
    }

}
const addFormValidations = function () {
    form.value.validate({
        rules: {
            closure_start: "required",
            closure_status: "required",
            open_reason: "required",
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
            closure_status: "Select a closure reason from the options",
            closure_details: "Details required if Other reason is selected"
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
    range_start.value = "";
    range_end.value = "";
    selected_campgrounds.value = [];
    reasonValue.value = "";
    closeStartPicker.value.clear();
    closeEndPicker.value.clear();
}

watch(()=> isModalOpen.value, (val) => {
    if(val) {
        clearValues()
    }
})

defineExpose({ isModalOpen, initSelectTwo })

onMounted(() => {
    form.value = $(document.forms.closeForm);
    events();
})
</script>

<style lang="css">
.body {
    padding: 0 20px;
}

.select2-container {
    z-index: 100000;
}
</style>
