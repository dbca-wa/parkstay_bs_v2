<template lang="html">
    <div id="bulkpricing">
        <div class="card p-3" id="applications">
            <div class="panel-heading" role="tab" id="applications-heading">
                <h4 class="panel-title">
                    Bulk Pricing
                </h4>
            </div>
            <div id="applications-collapse" class="" role="tabpanel" aria-labelledby="applications-heading">
                <loader :isLoading="isLoading">{{ loading.join(' , ') }}</loader>
                <div class="panel-body" v-show="!isLoading">
                    <alert :show="showError" :duration="7000" type="danger">{{ errorString }}</alert>
                    <alert :show="showSuccess" :duration="7000" type="success"><strong>Bulk pricing was successfull
                        </strong></alert>
                    <div class="round-box px-3 mt-4">
                        <div class="row">
                            <div class="col-lg-12">
                                <div class="row">
                                    <div class="col-md-3">
                                        <div class="radio">
                                            <label for="">Set price per : </label>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="radio">
                                            <label for="">
                                                <input class="form-check-input" type="radio" :value="priceOptions[1]"
                                                    v-model="setPrice">
                                                Park/Campground
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="radio">
                                            <label for="">
                                                <input class="form-check-input" type="radio" :value="priceOptions[2]"
                                                    v-model="setPrice">
                                                Campsite Type
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class=" round-box px-3 mt-4 ">
                        <div class="row">
                            <div class="col-lg-12">
                                <h3>Add New Pricing Period For {{ setPrice }}</h3><br />
                                <form name="bulkpricingForm" class="form-horizontal">
                                    <div class="form-group">
                                        <div class="col-md-2">
                                            <label class="control-label">{{ setPrice }}</label>
                                        </div>
                                        <div class="col-md-4" v-show="setPrice == priceOptions[0]">
                                            <select class="form-control">
                                                <option>Price Tarriff</option>
                                            </select>
                                        </div>
                                        <div class="col-md-4" v-show="setPrice == priceOptions[1]">
                                            <select name="tmpPark" v-show="!parks.length > 0" class="form-control">
                                                <option>Loading...</option>
                                            </select>
                                            <select name="park" v-if="parks.length > 0" class="form-control"
                                                v-model="bulkpricing.park">
                                                <option v-for="park in parks" :value="park.id">{{ park.name }}</option>
                                            </select>
                                        </div>
                                        <div class="col-md-4" v-show="setPrice == priceOptions[2]">
                                            <select name="tmpCampsiteType" v-show="!campsiteTypes.length > 0"
                                                class="form-control">
                                                <option>Loading...</option>
                                            </select>
                                            <select name="campsiteType" v-if="campsiteTypes.length > 0"
                                                @change="selectCampsiteType" class="form-control"
                                                v-model="bulkpricing.campsiteType">
                                                <option v-for="ct in campsiteTypes" :value="ct.id">{{ ct.name }}
                                                </option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="form-group"
                                        v-show="setPrice != priceOptions[2] && campgrounds.length > 0">
                                        <div class="col-md-2">
                                            <label class="control-label">Campground</label>
                                        </div>
                                        <div class="col-md-4">
                                            <select name="tmpCampground" v-show="!parks.length > 0"
                                                class="form-control">
                                                <option>Loading...</option>
                                            </select>
                                            <select name="campground" id="bulkpricingCampgrounds"
                                                v-if="parks.length > 0" class="form-control"
                                                v-model="bulkpricing.campgrounds" multiple="multiple">
                                                <option v-for="campground in campgrounds" :value="campground.id">{{
                                                    campground.name }}</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <div class="col-md-2">
                                            <label><i class="fa fa-question-circle" data-toggle="tooltip"
                                                    data-placement="bottom"
                                                    title="Select a rate to prefill the price fields otherwise use the manual entry">&nbsp;</i>Select
                                                Rate: </label>

                                        </div>
                                        <div class="col-sm-4">
                                            <select name="rate" v-model="selected_rate" class="form-control"
                                                title="testing">
                                                <option value="">Manual Entry</option>
                                                <option v-for="r in rates" :value="r.id">{{ r.name }}</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <div class="col-md-2">
                                            <label>Adult Price: </label>
                                        </div>
                                        <div class="col-md-4">
                                            <input :readonly="selected_rate != ''" name="adult"
                                                v-model="bulkpricing.adult" type='text' class="form-control"
                                                required="true" />
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <div class="col-md-2">
                                            <label>Concession Price: </label>
                                        </div>
                                        <div class="col-md-4">
                                            <input :readonly="selected_rate != ''" name="concession"
                                                v-model="bulkpricing.concession" type='text' class="form-control"
                                                required="true" />
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <div class="col-md-2">
                                            <label>Child Price: </label>
                                        </div>
                                        <div class="col-md-4">
                                            <input :readonly="selected_rate != ''" name="child"
                                                v-model="bulkpricing.child" type='text' class="form-control"
                                                required="true" />
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <div class="col-md-2">
                                            <label>Period start: </label>
                                        </div>
                                        <div class="col-md-4">
                                            <div class='input-group date'>
                                                <input name="period_start" v-model="bulkpricing.period_start"
                                                    type='text' class="form-control" required="true" />
                                                <span class="input-group-addon">
                                                    <span class="glyphicon glyphicon-calendar"></span>
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    <reason type="price" v-model="bulkpricing.reason" required="true"></reason>
                                    <div v-show="requireDetails">
                                        <div class="form-group">
                                            <div class="col-md-2">
                                                <label>Details: </label>
                                            </div>
                                            <div class="col-md-5">
                                                <textarea name="details" v-model="bulkpricing.details"
                                                    class="form-control" :required="requireDetails"></textarea>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="btn-group btn-group-sm pt-3">
                                        <button type="button" class="btn btn-primary"
                                            @click.prevent="sendData()">Save</button>
                                        <button type="button" class="btn btn-danger" @click="goBack()">Cancel</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card p-3 mt-4">

            <div class="panel-heading" role="tab" id="parkentry-heading">
                <h4 class="panel-title">
                    Park Entry
                </h4>
            </div>


            <div id="parkentry-collapse" class="" role="tabpanel" aria-labelledby="parkentry-heading">
                <div class="panel-body">
                    <div class="col-lg-12">
                        <price-history :addParkPrice="true" :dt_options="priceHistoryDt"
                            :dt_headers="priceHistoryDtHeaders" :object_id="34" level='park'></price-history>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import {
    $,
    api_endpoints,
    helpers,
    getDateTimePicker,
    dateUtils,
    Moment
}
    from '../../hooks.js'
import alert from '../utils/alert.vue'
import reason from '../utils/reasons.vue'
import loader from '../utils/loader.vue'
import priceHistory from '../utils/priceHistory/priceHistory.vue'
import { mapGetters } from 'vuex'
import { computed, onMounted, ref, watch } from 'vue'
import { useStore } from "../../apps/store.js";

const store = useStore()

const priceOptions = ['Price Tariff', 'Park', 'Campsite Type']
const priceHistoryDtHeaders = [
    "Period Start", "Period End", "Car", "Concession", "Motorbike", "Campervan", "Caravan", "Trailer", "GST", "Comment", "Action"
]
const setPrice = ref('')
const id = ref('')
const selected_rate = ref('')
const rates = ref([])
const errors = ref(false)
const errorString = ref('')
const loading = ref([])
const form = ref(null)
const bulkpricing = ref({
    reason: '',
    campgrounds: []
})
const campgrounds = ref([])
const campsiteTypes = ref([])
const showSuccess = ref(false)
const priceHistoryDt = ref({
    responsive: true,
    processing: true,
    ordering: false,
    deferRender: true,
    ajax: {
        url: api_endpoints.park_price_history(),
        dataSrc: ''
    },
    columns: [{
        data: 'period_start',
        mRender: function (data, type, full) {
            return Moment(data).format('DD/MM/YYYY');
        }

    }, {
        data: 'period_end',
        mRender: function (data, type, full) {
            if (data) {
                return Moment(data).format('DD/MM/YYYY');
            }
            else {
                return '';
            }
        }

    }, {
        data: 'vehicle'
    }, {
        data: 'concession'
    }, {
        data: 'motorbike'
    }, {
        data: 'campervan',
    }, {
        data: 'caravan',
    }, {
        data: 'trailer',
    }, {
        data: 'gst',
    }, {
        data: 'reason',
        mRender: function (data, type, full) {
            if (data.id == 1) {
                return data.text + ":" + full.details;
            } else {
                return data.text
            }
        }
    }, {
        data: 'editable',
        mRender: function (data, type, full) {
            if (data) {
                var id = full.id;
                var column = "<td ><a href='#' class='editPrice' data-rate=\"__RATE__\" >Edit</a><br/>"
                column += "<a href='#' class='deletePrice' data-rate=\"__RATE__\" >Delete</a></td>";
                column = column.replace(/__RATE__/g, id);
                return column;
            }
            else {
                return "";
            }
        }
    }],
    language: {
        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
    },
})

const emit = defineEmits(['updatePriceHistory', 'addPriceHistory'])

const showError = computed(function () {
    return errors.value;
})

const requireDetails = computed(function () {
    return bulkpricing.value.reason == '1';
})
const isLoading = computed(function () {
    if (loading.value.length > 0) {
        return true;
    }
    else {
        setTimeout(function (e) {
            $(form.value.park).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder: "Select Park"
            }).
                on("select2:select", function (e) {
                    var selected = $(e.currentTarget);
                    bulkpricing.value.park = selected.val();
                    selectPark();
                }).
                on("select2:unselect", function (e) {
                    var selected = $(e.currentTarget);
                    bulkpricing.value.park = "";
                });
        }, 100);
    }
})
const parks = computed(() => store.getters.parks)
const campsite_classes = computed(() => store.getters.campsite_classes)

watch(() => setPrice.value, function (value) {
    if (value == priceOptions[2]) {
        setTimeout(function () {
            $(form.value.campsiteType).select2({
                theme: 'bootstrap',
                allowClear: true,
                placeholder: "Select Campsite Type",
            }).
                on("select2:select", function (e) {
                    var selected = $(e.currentTarget);
                    bulkpricing.value.campsiteType = selected.val();
                }).
                on("select2:unselect", function (e) {
                    var selected = $(e.currentTarget);

                    bulkpricing.value.campsiteType = selected.val();
                });
        }, 100);
    }
})
watch(() => selected_rate.value, function (value) {
    if (value != '') {
        $.each(rates.value, function (i, rate) {
            if (rate.id == value) {
                bulkpricing.value.rate = rate.id;
                bulkpricing.value.adult = rate.adult;
                bulkpricing.value.concession = rate.concession;
                bulkpricing.value.child = rate.child;
            }
        });
    }
    else {
        delete bulkpricing.value.rate;
        bulkpricing.value.adult = '';
        bulkpricing.value.concession = '';
        bulkpricing.value.child = '';
    }
})
watch(() => campsite_classes, function (value) {
    availableCampsiteClasses();
})

const availableCampsiteClasses = function () {
    loading.value.push('Loading CampsiteTypes');
    campsiteTypes.value = [];
    $.each(campsite_classes.value, function (i, el) {
        el.can_add_rate ? campsiteTypes.value.push(el) : '';
    });
    if (campsiteTypes.value.length == 0) {
        campsiteTypes.value.push({
            id: "",
            name: ""
        });
    }
    loading.value.splice('Loading CampsiteTypes', 1);
}
const sendData = function () {
    if ($(form.value).valid()) {
        loading.value.push('Updating prices...');
        var data = JSON.parse(JSON.stringify(bulkpricing.value));
        var url = api_endpoints.bulkPricing();
        data.type = setPrice.value;
        $.ajax({
            beforeSend: function (xhrObj) {
                xhrObj.setRequestHeader("Content-Type", "application/json");
                xhrObj.setRequestHeader("Accept", "application/json");
            },
            method: "POST",
            url: url,
            xhrFields: { withCredentials: true },
            data: JSON.stringify(data),
            headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
            success: function (msg) {
                setTimeout(function () {
                    loading.value.splice('Updating prices...', 1);
                    bulkpricing.value = {
                        reason: '',
                        campgrounds: []
                    };
                    showSuccess.value = true;
                }, 500);
            },
            error: function (resp) {
                loading.value.splice('Updating prices...', 1);
                errors.value = true;
                errorString.value = resp;
            }
        });
    } else {
        errors.value = true;
        errorString.value = "Please fill all details";
    }
}
const close = function () {
    delete bulkpricing.value.original;
    errors.value = false;
    selected_rate.value = '';
    bulkpricing.value.period_start = '';
    bulkpricing.value.details = '';

    errorString.value = '';
    isOpen.value = false;
}
const selectPark = function () {
    var park = bulkpricing.value.park;
    campgrounds.value = [];
    $.each(parks.value, function (i, el) {
        if (el.id == park) {
            $.each(el.campgrounds, function (k, c) {
                c.price_level == 0 ? campgrounds.value.push(c) : null;
            })

            setTimeout(function (e) {
                $(form.value.campground).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    placeholder: {
                        text: "Select Campground",
                        selected: 'selected'
                    }
                }).
                    on("select2:select", function (e) {
                        var selected = $(e.currentTarget);
                        bulkpricing.value.campgrounds = selected.val();
                    }).
                    on("select2:unselect", function (e) {
                        var selected = $(e.currentTarget);

                        bulkpricing.value.campgrounds = selected.val();
                    });
            }, 100);
        };
    });

}
const selectCampsiteType = function () {

}
const loadParks = function () {
    var url = api_endpoints.parks;
    loading.value.push('Loading Parks');
    if (parks.value.length == 0) {
        store.dispatch("fetchParks");
    }
    loading.value.splice('Loading Parks', 1);

}
const addHistory = function () {
    if ($(form.value).valid()) {
        if (bulkpricing.value.id || bulkpricing.value.original) {
            emit('updatePriceHistory');
        } else {
            emit('addPriceHistory');
        }
    }
}
const fetchRates = function () {
    loading.value.push('Loading Rates');
    fetch(api_endpoints.rates).then((response) => response.json())
    .then((data) => {
        rates.value = data;
        loading.value.splice('Loading Rates', 1);
    }).catch(error=> {
        console.log(error)
    })
}
const fetchCampsiteTypes = function () {
    if (campsite_classes.value.length == 0) {
        store.dispatch("fetchCampsiteClasses");
    } else {
        availableCampsiteClasses();
    }
}
const goBack = function () {
    router.go(-1);
}
const addFormValidations = function () {
    $(form.value).validate({
        rules: {
            park: {
                required: {
                    depends: function (el) {
                        return setPrice.value == priceOptions[1];
                    }
                }
            },
            campground: {
                required: {
                    depends: function (el) {
                        return setPrice.value == priceOptions[1];
                    }
                }
            },
            campsiteType: {
                required: {
                    depends: function (el) {
                        return setPrice.value == priceOptions[2];
                    }
                }
            },
            adult: "required",
            concession: "required",
            child: "required",
            period_start: "required",
            open_reason: "required",
            details: {
                required: {
                    depends: function (el) {
                        return bulkpricing.value.reason === '1';
                    }
                }
            }
        },
        messages: {
            adult: "Enter an adult rate",
            concession: "Enter a concession rate",
            child: "Enter a child rate",
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
    $("i.fa").tooltip();
    form.value = document.forms.bulkpricingForm;
    loadParks();
    setPrice.value = priceOptions[1];
    const pickerElement = $(form.value.period_start).closest('.date');
    const picker = getDateTimePicker(pickerElement, {
        useCurrent: false,
        restrictions: { minDate: dateUtils.addDays(new Date(), 1) }
    });
    pickerElement.on('change.td', function (e) {
        const date = picker.dates.lastPicked
        bulkpricing.value.period_start = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
    });
    addFormValidations();
    fetchRates();
    fetchCampsiteTypes();
})
</script>
<style lang="css" scoped>
.editor {
    height: 200px;
}

.well:last-child {
    margin-bottom: 5px;
}
</style>
