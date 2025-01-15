<template id="PriceHistoryDetail">
    <bootstrapModal :title="title" :large=true @ok="addHistory()" @close="close()" :isModalOpen="isModalOpen" @cancel="close()">

        <div class="modal-body">
            <form name="priceForm" class="form-horizontal">
                <alert v-model:show="showError" type="danger">{{ errorString }}</alert>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label><i class="fa fa-question-circle" data-toggle="tooltip" data-placement="bottom"
                                    title="Select a rate to prefill the price fields otherwise use the manual entry"></i>Select
                                Rate: </label>
                        </div>
                        <div class="col-md-4">
                            <select name="rate" v-model="selected_rate" class="form-control">
                                <option value="">Manual Entry</option>
                                <option v-for="r in rates" :value="r.id">{{ r.name }}</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label>Adult Price: </label>
                        </div>
                        <div class="col-md-4">
                            <input :readonly="selected_rate != ''" name="adult" v-model="priceHistory.adult" type='text'
                                class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label>Concession Price: </label>
                        </div>
                        <div class="col-md-4">
                            <input :readonly="selected_rate != ''" name="concession" v-model="priceHistory.concession"
                                type='text' class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label>Child Price: </label>
                        </div>
                        <div class="col-md-4">
                            <input :readonly="selected_rate != ''" name="child" v-model="priceHistory.child" type='text'
                                class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label>Infant Price: </label>
                        </div>
                        <div class="col-md-4">
                            <input :readonly="selected_rate != ''" name="infant" v-model="priceHistory.infant"
                                type='text' class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label>Period start: </label>
                        </div>
                        <div class="col-md-4">
                            <div class='input-group date'>
                                <input name="period_start" v-model="priceHistory.period_start" type='text'
                                    class="form-control" />
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <reason type="price" v-model="priceHistory.reason"></reason>
                <div v-show="requireDetails" class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label>Details: </label>
                        </div>
                        <div class="col-md-5">
                            <textarea name="details" v-model="priceHistory.details" class="form-control"></textarea>
                        </div>
                    </div>
                </div>


                <div class="row">
                    <div class="form-group">
                        <div class="col-md-2">
                            <label>Booking Policy: {{ priceHistory.booking_policy }}</label>
                        </div>
                        <div class="col-md-4">
                            <select name="rate" v-model="priceHistory.booking_policy" class="form-control">
                                <option value="">Select Booking Policy</option>
                                <option v-for="p in booking_policy.dataitems" :value="p.id">{{ p.policy_name }}</option>
                            </select>
                        </div>
                    </div>
                </div>
            </form>
        </div>
    </bootstrapModal>
</template>

<script setup>
import bootstrapModal from '../bootstrap-modal.vue'
import reason from '../reasons.vue'
import { $, getDateTimePicker, dateUtils, api_endpoints } from '../../../hooks.js'
import alert from '../alert.vue'
import { computed, onMounted, ref, watch } from 'vue';

const emit = defineEmits(['addPriceHistory', 'updatePriceHistory'])

const props = defineProps({
    priceHistory: {
        type: Object,
        required: true
    },
});
const id = ref('')
const selected_rate = ref('')
const title = ref('')
const rates = ref([])
const booking_policy = ref([])
const priceHistory = ref(props.priceHistory)
const current_closure = ref('')
const closeStartPicker = ref('')
const showDetails = ref(false)
const closeEndPicker = ref('')
const errors = ref(false)
const errorString = ref('')
const form = ref('')
const isOpen = ref(false)

const showError = computed(function () {
    return errors.value;
})
const isModalOpen = computed(function () {
    return isOpen.value;
})
const closure_id = computed(function () {
    return props.priceHistory.id ? props.priceHistory.id : '';
})
const requireDetails = computed(function () {
    return props.priceHistory.closure_reason === '1';
})

watch(() => selected_rate.value, function (value) {
    if (value != '') {
        $.each(rates.value, function (i, rate) {
            if (rate.id == value) {
                console.log("SELECTED RATE");
                console.log(rate);
                priceHistory.value.rate = rate.id;
                priceHistory.value.adult = rate.adult;
                priceHistory.value.concession = rate.concession;
                priceHistory.value.child = rate.child;
                priceHistory.value.infant = rate.infant;
                console.log("RATE POLICY");
                // console.log(rate.booking_policy_id);
                // vm.priceHistory.booking_policy = rate.bookingpolicyid;
            }
        });
    }
    else {
        delete priceHistory.value.rate;
        priceHistory.value.adult = '';
        priceHistory.value.concession = '';
        priceHistory.value.child = '';
        priceHistory.value.infant = '';
        priceHistory.value.booking_policy = '';
    }
})


const close = function () {
    delete priceHistory.value.original;
    errors.value = false;
    selected_rate.value = '';
    priceHistory.value.period_start = '';
    priceHistory.value.details = '';

    errorString.value = '';
    isOpen.value = false;
}

const addHistory = function () {
    if ($(form.value).valid()) {
        if (priceHistory.value.id || priceHistory.value.original) {
            emit('updatePriceHistory', priceHistory.value);
        } else {
            emit('addPriceHistory', priceHistory.value);
        }
    }
}
const fetchRates = function () {

    fetch(api_endpoints.rates).then((response) => response.json()).then((data) => {
        rates.value = data;
    });
}
const fetchBookingPolicy = function () {

    console.log("fetchBookingPolicy 1");
    console.log(api_endpoints.booking_policy);
    fetch(api_endpoints.booking_policy).then((response) => response.json()).then((data) => {
        booking_policy.value = data;
        console.log("fetchBookingPolicy");
        console.log(booking_policy.value);
    });

}
const addFormValidations = function () {
    $(form.value).validate({
        rules: {
            adult: "required",
            concession: "required",
            child: "required",
            infant: "required",
            period_start: "required",
            details: {
                required: {
                    depends: function (el) {
                        return priceHistory.value.reason === '1';
                    }
                }
            }
        },
        messages: {
            adult: "Enter an adult rate",
            concession: "Enter a concession rate",
            child: "Enter a child rate",
            infant: "Enter a infant rate",
            period_start: "Enter a start date",
            details: "Details required if Other reason is selected"
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


onMounted(function () {
    $('[data-toggle="tooltip"]').tooltip()
    form.value = document.forms.priceForm;
    const pickerElement = $(form.value.period_start)
    const picker = getDateTimePicker(pickerElement, {
        useCurrent: false,
        restrictions: { minDate: dateUtils.addDays(new Date(), 1) }
    });
    pickerElement.on('change.td', function (e) {
        const date = picker.dates.lastPicked
        priceHistory.value.period_start = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    });
    addFormValidations();
    fetchBookingPolicy();
    fetchRates();
})

defineExpose({ title, isOpen, errorString, errors, selected_rate})
</script>
<style lang="css" scoped></style>
