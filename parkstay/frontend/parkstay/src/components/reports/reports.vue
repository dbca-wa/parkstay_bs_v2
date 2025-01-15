<template lang="html">
    <div id="report-form">
        <form method="get" ref="paymentsForm" action="/ledger/payments/api/report">
            <div class="well well-sm">
                <div class="row">
                    <div class="col-lg-12">
                        <div class="col-lg-12">
                            <h3 style="margin-bottom:20px;">Select Region</h3>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label for="">Region</label>
                                        <select class="form-control" name="region" v-model="region">
                                            <option value="">Kensington</option>
                                            <option v-for="r in regions" :value="r.code">{{ r.name }}</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6" v-show="region">
                                    <div class="form-group">
                                        <label for="">District</label>
                                        <select class="form-control" name="region" v-model="district">
                                            <option value="">All</option>
                                            <option v-for="d in selected_region.districts" :value="d.code">{{ d.name }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="well">
                <div class="row">
                    <div class="col-md-12">
                        <h3 style="margin-bottom:20px;">Payments Reports</h3>
                        <div class="row" v-show="!region">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label for="">Start Date</label>
                                    <div class="input-group date" id="accountsDateStartPicker">
                                        <input type="text" class="form-control" name="start" placeholder="DD/MM/YYYY"
                                            required>
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label for="">End Date</label>
                                    <div class="input-group date" id="accountsDateEndPicker">
                                        <input type="text" class="form-control" name="end" placeholder="DD/MM/YYYY"
                                            required>
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row" style="margin-top:20px;">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label for="">Bank Start Date</label>
                                    <div class="input-group date" id="flatDateStartPicker">
                                        <input type="text" class="form-control" name="banked_start"
                                            placeholder="DD/MM/YYYY" required>
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label for="">Bank End Date</label>
                                    <div class="input-group date" id="flatDateEndPicker">
                                        <input type="text" class="form-control" name="banked_end"
                                            placeholder="DD/MM/YYYY" required>
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                            </div>

                        </div>
                        <div class="row">
                            <div class="col-sm-6">
                                <button @click.prevent="generateByAccount()" class="btn btn-primary pull-left">Generate
                                    Report By Accounts</button>
                            </div>
                            <div class="col-sm-6 clearfix">
                                <button @click.prevent="generateFlatReport()" class="btn btn-primary pull-left">Generate
                                    Report Flat</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
        <form id="refund_form" ref="refund_form">
            <div class="well well-sm">
                <div class="row">
                    <div class="col-lg-12">
                        <div class="col-lg-12">
                            <h3 style="margin-bottom:20px;">Refunds Reports</h3>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="">Start Date</label>
                                <div class="input-group date" id="refundsStartPicker">
                                    <input type="text" class="form-control" name="refund_start_date"
                                        placeholder="DD/MM/YYYY">
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="">End Date</label>
                                <div class="input-group date" id="refundsEndPicker">
                                    <input type="text" class="form-control" name="refund_end_date"
                                        placeholder="DD/MM/YYYY">
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-lg-12">
                                <div class="col-sm-6">
                                    <button @click.prevent="generateRefundReport()"
                                        class="btn btn-primary pull-left">Generate Refund Reports</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
        <div class="well well-sm">
            <div class="row">
                <div class="col-lg-12">
                    <div class="row">
                        <div class="col-sm-12">
                            <div class="row">
                                <div class="col-sm-6">
                                    <form ref="booking_settlements_form">
                                        <h3 style="margin-bottom:20px;">Settlement Report</h3>
                                        <div class="form-group">
                                            <label for="">Date</label>
                                            <div class="input-group date" ref="bookingSettlementsDatePicker"
                                                id="bookingSettlementsDatePickerElement">
                                                <input type="text" class="form-control" name="booking_settlement_date"
                                                    placeholder="DD/MM/YYYY" required>
                                                <span class="input-group-addon">
                                                    <span class="glyphicon glyphicon-calendar"></span>
                                                </span>
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <button @click.prevent="getBookingSettlementsReport()"
                                                class="btn btn-primary pull-left">Generate Settlement Report</button>
                                        </div>
                                    </form>
                                </div>
                                <div class="col-sm-6">
                                    <form ref="bookings_form">
                                        <h3 style="margin-bottom:20px;">Bookings Report</h3>
                                        <div class="form-group">
                                            <label for="">Date</label>
                                            <div class="input-group date" ref="bookingsDatePicker"
                                                id="bookingsDatePickerElement">
                                                <input type="text" class="form-control" name="bookings_date"
                                                    placeholder="DD/MM/YYYY" required>
                                                <span class="input-group-addon">
                                                    <span class="glyphicon glyphicon-calendar"></span>
                                                </span>
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <button @click.prevent="getBookingsReport()"
                                                class="btn btn-primary pull-left">Generate Bookings Report</button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <form ref="oracle_form">
            <div class="well well-sm">
                <div class="row">
                    <div class="col-lg-12">
                        <div class="col-lg-12">
                            <h3 style="margin-bottom:20px;">Oracle Job</h3>
                        </div>
                        <div class="row">
                            <div class="col-lg-12">
                                <div class="col-sm-6">
                                    <div class="form-group">
                                        <label for="">Date</label>
                                        <div class="input-group date" ref="oracleDatePicker"
                                            id="oracleDatePickerElement">
                                            <input type="text" class="form-control" name="oracle_date"
                                                placeholder="DD/MM/YYYY" required>
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <button @click.prevent="runOracleJob()" class="btn btn-primary pull-left">Run
                                            Job</button>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                    <div class="checkbox">
                                        <label><input v-model="oracle_override" type="checkbox" value="">Override closed
                                            period check</label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { $, swal, getDateTimePicker, dateUtils, DateTime, api_endpoints, helpers } from "../../hooks.js"

const paymentsForm = ref(null)
const refund_form = ref(null)
const oracle_form = ref(null)
const oracleDatePicker = ref(null)
const booking_settlements_form = ref(null)
const bookings_form = ref(null)
const bookingSettlementsDatePicker = ref(null)
const bookingsDatePicker = ref(null)
const accountsDateStartPicker = ref(null)
const accountsDateEndPicker = ref(null)
const flatDateStartPicker = ref(null)
const flatDateEndPicker = ref(null)
const refundsStartPicker = ref(null)
const refundsEndPicker = ref(null)
const datepickerOptions = {
    useCurrent: false,
    display: {
        buttons: {
            clear: true,
        }
    },
}
const regions = ref([])
const region = ref("")
const district = ref("")
const selected_region = ref({
    code: '',
    name: '',
    districts: []
})
const oracle_override = ref(false)
watch(() => region.value, function (value) {
    district.value = '';
    if (value) {
        selected_region.value = regions.value.find(r => (r.code == value));
    } else {
        selected_region.value = {
            code: '',
            name: '',
            districts: []
        }
    }
})


const addEventListeners = function () {

    const accountsDateStartPickerElement = $('#accountsDateStartPicker')
    const flatDateStartPickerElement = $('#flatDateStartPicker')
    const refundsStartPickerElement = $('#refundsStartPicker')

    accountsDateStartPicker.value = getDateTimePicker(accountsDateStartPickerElement, datepickerOptions)
    flatDateStartPicker.value = getDateTimePicker(flatDateStartPickerElement, datepickerOptions)
    refundsStartPicker.value = getDateTimePicker(refundsStartPickerElement, datepickerOptions)

    accountsDateEndPicker.value = getDateTimePicker($('#accountsDateEndPicker'), datepickerOptions);
    flatDateEndPicker.value = getDateTimePicker($('#flatDateEndPicker'), datepickerOptions);
    refundsEndPicker.value = getDateTimePicker($('#refundsEndPicker'), datepickerOptions);
    oracleDatePicker.value = getDateTimePicker($('#oracleDatePickerElement'), datepickerOptions);
    bookingSettlementsDatePicker.value = getDateTimePicker($('#bookingSettlementsDatePickerElement'), datepickerOptions);
    bookingsDatePicker.value = getDateTimePicker($('#bookingsDatePickerElement'), datepickerOptions);

    flatDateStartPickerElement.on('hide.td', function (e) {
        const date = flatDateStartPicker.value.dates.lastPicked
        flatDateEndPicker.value.clear();
        if (date) {
            flatDateEndPicker.value.updateOptions({
                restrictions: {
                    minDate: date
                }
            });
        }
    });
    accountsDateStartPickerElement.on('hide.td', function (e) {
        const date = accountsDateStartPicker.value.dates.lastPicked
        accountsDateEndPicker.value.clear();
        if (date) {
            accountsDateEndPicker.value.updateOptions({
                restrictions: {
                    minDate: date
                }
            });
        }
    });
    refundsStartPickerElement.on('hide.td', function (e) {
        const date = refundsStartPicker.value.dates.lastPicked
        refundsEndPicker.value.clear();
        if (date) {
            refundsEndPicker.value.updateOptions({
                restrictions: {
                    minDate: date
                }
            });
        }
    });
    addFormValidations();
    fetchRegions();
}
const runOracleJob = function () {

    if (oracle_form.value.valid()) {
        const date = oracleDatePicker.value.dates.lastPicked
        let data = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
        let override = oracle_override.value ? 'true' : 'false';
        fetch('/api/oracle_job?date=' + data + '&override=' + override).then((response) => {
            swal({
                type: 'success',
                title: 'Job Success',
                text: 'The oracle job was completed successfully',
            })
        }).catch((error) => {
            swal({
                type: 'error',
                title: 'Oracle Job Error',
                text: helpers.apiVueResourceError(error),
            })
        })
    }
}
const getBookingSettlementsReport = function () {

    if (booking_settlements_form.value.valid()) {
        const date = bookingSettlementsDatePicker.value.dates.lastPicked
        let data = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
        var url = '/api/reports/booking_settlements?date=' + data;
        window.location.assign(url);
        /*$.valuehttp.get(url).then((response) => {
        },(error) => {
            swal({
                type: 'error',
                title: 'BPOINT Settlement Report Error', 
                text: helpers.apiVueResourceError(error), 
            })
        })*/
    }
}
const getBookingsReport = function () {

    if (bookings_form.value.valid()) {
        const date = bookingsDatePicker.value.dates.lastPicked
        let data = date ? dateUtils.formatDate(date, 'dd/MM/yyyy') : '';
        var url = '/api/reports/bookings?date=' + data;
        window.location.assign(url);
        /*$.valuehttp.get(url).then((response) => {
        },(error) => {
            swal({
                type: 'error',
                title: 'BPOINT Settlement Report Error', 
                text: helpers.apiVueResourceError(error), 
            })
        })*/
    }
}

const fetchRegions = function () {
    fetch('/ledger/payments/api/regions?format=json').then((response) => response.json()).then((data) => {
        regions.value = data;
    });
}
const generateFlatReport = function () {
    var values = generateValues();
    if (values) {
        values.flat = false;
        getReport(values);
    }
}
const generateValues = function () {
    if (paymentsForm.value.valid()) {
        var values = {
            "system": "S019",
            "start": (region.value) ? dateUtils.formatDate(new DateTime(flatDateStartPicker.value.dates.lastPicked).startOf('date'), 'yyyy-MM-dd H:mm:ss') :
                dateUtils.formatDate(new DateTime(accountsDateStartPicker.value.dates.lastPicked).startOf('date'), 'yyyy-MM-dd H:mm:ss'),
            "end": (region.value) ? dateUtils.formatDate(new DateTime(flatDateEndPicker.value.dates.lastPicked).startOf('date'), 'yyyy-MM-dd H:mm:ss') :
                dateUtils.formatDate(new DateTime(accountsDateEndPicker.value.dates.lastPicked).startOf('date'), 'yyyy-MM-dd H:mm:ss'),
            "banked_start": dateUtils.formatDate(new DateTime(flatDateStartPicker.value.dates.lastPicked).startOf('date'), 'yyyy-MM-dd H:mm:ss'),
            "banked_end": dateUtils.formatDate(new DateTime(flatDateEndPicker.value.dates.lastPicked).startOf('date'), 'yyyy-MM-dd H:mm:ss'),
        };
        if (region.value) {
            values.region = region.value;
            if (district.value) {
                values.district = district.value;
            }
        }
        return values;
    }
    return false;
}
const generateByAccount = function () {
    var values = generateValues();
    if (values) {
        values.items = true;
        getReport(values);
    }

}
const generateRefundReport = function () {
    let vm = this;

    if (refund_form.value.valid()) {
        var values = {
            "start": dateUtils.formatDate(refundsStartPicker.value.dates.lastPicked, 'dd/MM/yyyy'),
            "end": dateUtils.formatDate(refundsEndPicker.value.dates.lastPicked, 'dd/MM/yyyy'),
        }
        var url = api_endpoints.booking_refunds + "?" + $.param(values);
        window.location.assign(url);
    } else {
        console.log("invalid form");
    }

}
const getReport = function (values) {
    var url = "/ledger/payments/api/report?" + $.param(values);
    window.location.assign(url);
}
const addFormValidations = function () {
    let vm = this;
    paymentsForm.value.validate({
        rules: {
            start: {
                required: function () {
                    return region.value.length == 0;
                }
            },
            end: {
                required: function () {
                    return region.value.length == 0;
                }
            },
            banked_start: "required",
            banked_end: "required",
        },
        messages: {
            start: "Field is required",
            end: "Field is required",
            banked_end: "Field is required",
            banked_start: "Field is required",
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
    refund_form.value.validate({
        rules: {
            refund_start_date: {
                required: function () {
                    return region.value.length == 0;
                }
            },
            refund_end_date: {
                required: function () {
                    return region.value.length == 0;
                }
            }
        },
        messages: {
            refund_start_date: "Field is required",
            refund_end_date: "Field is required",
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
    oracle_form.value.validate({
        rules: {
            oracle_date: 'required',
        },
        messages: {
            oracle_date: "Field is required",
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
    booking_settlements_form.value.validate({
        rules: {
            booking_settlement_date: 'required',
        },
        messages: {
            booking_settlement_date: "Field is required",
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
    bookings_form.value.validate({
        rules: {
            bookings_date: 'required',
        },
        messages: {
            bookings_date: "Field is required",
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

</script>

<style lang="css"></style>
