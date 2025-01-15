<template lang="html">
    <div id="addBooking">
        <form v-show="!isLoading" name="bookingForm">
            <div class="row">
                <div class="col-lg-12">
                    <div class="well">
                        <div class="row">
                            <div class="col-md-12">
                                <div class="col-md-6">
                                    <h3 class="text-primary pull-left">Add internal booking for {{ campground.name }}</h3>
                                </div>
                            </div>
                            <div class="col-md-12">
                                <p>Internal bookings can be made for campsites closed to public bookings.<a
                                        target='_blank' v-bind:href="'/availability_admin/?site_id=' + campground.id">
                                        Check closures</a> before adding a closed site to a booking.</p>
                            </div>
                            <div class="col-md-12" v-if="(campground.site_type == 1) || (campground.site_type == 2)">
                                <p>To book closed sites, you must allocate specific site numbers/names - switch to the
                                    <router-link :to="{ name: 'booking-close-classes' }">full camp site list.</router-link>
                                    The allocated site number/name is for management purposes only - it will not be
                                    visible to the public.</p>
                            </div>
                            <div class="row">
                                <div class="col-md-12">
                                    <div class="form-group">
                                        <div class="col-md-12">
                                            <label class="control-label pull-left required" for="Dates">Dates: </label>
                                            <div class="col-md-3">
                                                <div class="input-group date" id="dateArrival">
                                                    <input type="text" class="form-control" name="arrival"
                                                        placeholder="Arrival">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="input-group date" id="datedeparture">
                                                    <input type="text" class="form-control" name="departure"
                                                        placeholder="Departure">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="col-md-4">
                                                <div class="form-group">
                                                    <label class="control-label pull-left required"
                                                        for="Campground">Guests: </label>
                                                    <div class="col-md-8">
                                                        <div class="dropdown guests">
                                                            <input type="text" class="form-control dropdown-toggle"
                                                                name="guests" placeholder="Guests"
                                                                data-toggle="dropdown" aria-haspopup="true"
                                                                aria-expanded="true" v-model="guestsText">
                                                            <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
                                                                <li v-for="guest in guestsPicker">
                                                                    <div class="row">
                                                                        <div class="col-sm-4">
                                                                            <span class="item">
                                                                                {{ guest.amount }} {{ guest.name }} <span
                                                                                    style="color:#888;font-weight:300;font-size:12px;">{{ guest.description }}</span>
                                                                            </span>
                                                                            <br /><a href="#" class="text-info"
                                                                                v-show="guest.helpText">{{ guest.helpText }}</a>
                                                                        </div>
                                                                        <div class="pull-right">
                                                                            <div class="btn-group btn-group-sm">
                                                                                <button type="button"
                                                                                    class="btn btn-guest"
                                                                                    @click.prevent.stop="addGuestCount(guest)"><span
                                                                                        class="glyphicon glyphicon-plus"></span></button>
                                                                                <button type="button"
                                                                                    class="btn btn-guest"
                                                                                    @click.prevent.stop="removeGuestCount(guest)"><span
                                                                                        class="glyphicon glyphicon-minus"></span></button>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                </li>
                                                            </ul>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-lg-12">
                                    <div id="campsite-booking" v-if="campground.site_type == 0">
                                        <div v-show="booking.campsites.length < 1" class="col-lg-12 text-center">
                                            <h2>No Campsites Available For The Provided Dates</h2>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-12">
                                    <div v-show="booking.campsites.length > 0">
                                        <div class="column table-scroll">
                                            <!-- v-model="selected_campsite" -->
                                            <table class="hover table table-striped table-bordered dt-responsive nowrap"
                                                cellspacing="0" width="100%" name="campsite">
                                                <thead>
                                                    <tr>
                                                        <th class="form-group">Campsite</th>
                                                        <th class="form-group">Status</th>
                                                        <th>Sites to book
                                                            <input class="checkbox" type="checkbox" id="selectAll"
                                                                v-model="selectAll" :disabled="isDisabled">
                                                        </th>
                                                    </tr>
                                                </thead>
                                                <tbody><template v-for="campsite in booking.campsites">
                                                        <tr>
                                                            <td class="form-group"> {{ campsite.name }} -
                                                                {{ campsite.type }}</td>
                                                            <td class="form-group"> {{ campsite.status }}</td>
                                                            <td>
                                                                <input class="checkbox" type="checkbox"
                                                                    :value="campsite.id"
                                                                    :disabled="campsite.status == 'booked' || campsite.status == 'closed & booked'"
                                                                    v-model="multibook_selected"
                                                                    @change="updatePrices()" number>
                                                            </td>
                                                        </tr>
                                                    </template>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-lg-12">
                                    <div id="campsite-class-booking"
                                        v-if="(campground.site_type == 1) || (campground.site_type == 2)">
                                        <div class="row">
                                            <div v-show="booking.campsite_classes.length < 1"
                                                class="col-lg-12 text-center">
                                                <h2>No Campsites Available For The Provided Dates</h2>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-12">
                                    <div v-show="booking.campsite_classes.length > 0">
                                        <div class="column table-scroll">
                                            <!-- v-model="selected_campsite_class" -->
                                            <table class="hover table table-striped table-bordered dt-responsive nowrap"
                                                cellspacing="0" width="100%" name="campsite-type">
                                                <thead>
                                                    <tr>
                                                        <th class="site">Campsite</th>
                                                        <th class="form-group">Status</th>
                                                        <th class="book">Availability</th>
                                                        <th class="numBook">Number of sites to book</th>
                                                    </tr>
                                                </thead>
                                                <tbody><template v-for="c in booking.campsite_classes">
                                                        <tr>
                                                            <td class="site"> {{ c.name }} </td>
                                                            <td class="site"> {{ c.status }} </td>
                                                            <td class="book"> {{ c.campsites.length }} available </td>
                                                            <td class="numBook">
                                                                <input type="number" id="numberRange" min="0"
                                                                    v-bind:max="c.campsites.length" class="form-control"
                                                                    v-model="c.selected_campsite_class"
                                                                    @change="updateCampsiteCount(c)">
                                                            </td>
                                                        </tr>
                                                    </template>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-lg-12">
                    <div class="well">
                        <div class="row">
                            <div class="col-lg-6">
                                <div class="row">
                                    <div class="col-lg-12">
                                        <h3 class="text-primary">Personal Details</h3>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-12">
                                        <div class="form-group">
                                            <label for="Email" class="required">Email</label>
                                            <input type="text" name="email" class="form-control" v-model="booking.email"
                                                list="matched_emails" @keyup="fetchUsers()">
                                            <datalist id="matched_emails">
                                                <option v-if="usersEmail" v-for="email in usersEmail" :value="email">
                                                </option>
                                            </datalist>
                                        </div>
                                    </div>
                                    <div class="col-md-6" v-show="false">
                                        <div class="form-group">
                                            <label for="Confirm Email" class="required">Confirm Email</label>
                                            <input type="text" name="confirm_email" class="form-control">
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="First Name" class="required">First Name</label>
                                            <input type="text" name="firstname" class="form-control"
                                                v-model="booking.firstname">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="Surname" class="required">Surname</label>
                                            <input type="text" name="surname" class="form-control"
                                                v-model="booking.surname">
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="Postcode" class="required">Postcode</label>
                                            <input type="text" name="postcode" class="form-control"
                                                v-model="booking.postcode">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="Country" class="required">Country</label>
                                            <select class="form-control" name="country" v-model="booking.country">
                                                <option v-for="c in countries" :value="c.iso_3166_1_a2">{{
                                                    c.printable_name }}
                                                </option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="Phone" class="required">Phone <span class="text-muted">(mobile
                                                    prefered)</span></label>
                                            <input type="text" name="phone" class="form-control"
                                                v-model="booking.phone">
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="row">
                                    <div class="col-lg-12">
                                        <h3 class="text-primary" v-if="park.entry_fee_required">Park Entry Fees
                                            <small>(${{ $filters.formatMoney(parkPrices.vehicle, 2) }}/per
                                                vehicle)</small>
                                        </h3>
                                        <h3 class="text-primary" v-else>Vehicle Details</h3>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-12">
                                        <div class="form-group">
                                            <label for="vehicles" class="required">Number of Vehicles</label>
                                            <div class="dropdown guests">
                                                <input type="number" min="0" max="10" name="vehicles"
                                                    class="form-control dropdown-toggle" data-toggle="dropdown"
                                                    aria-haspopup="true" aria-expanded="true" readonly="true"
                                                    v-model="booking.parkEntry.vehicles">
                                                <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
                                                    <li v-for="park_entry in parkEntryPicker">
                                                        <div class="row">
                                                            <div class="col-sm-8">
                                                                <span class="item">
                                                                    {{ park_entry.amount }} {{ park_entry.name }} <span
                                                                        style="color:#888;font-weight:300;font-size:12px;"></span>
                                                                </span>
                                                                <br /><a href="#" class="text-info"
                                                                    v-show="park_entry.helpText">{{ park_entry.helpText }}</a>
                                                            </div>
                                                            <div class="pull-right">
                                                                <div class="btn-group btn-group-sm">
                                                                    <button type="button" class="btn btn-guest"
                                                                        @click.prevent.stop="addVehicleCount(park_entry)"><span
                                                                            class="glyphicon glyphicon-plus"></span></button>
                                                                    <button type="button" class="btn btn-guest"
                                                                        @click.prevent.stop="removeVehicleCount(park_entry)"><span
                                                                            class="glyphicon glyphicon-minus"></span></button>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="row" v-for="(v, index) in parkEntryVehicles">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label class="required">{{ v.description }}</label>
                                            <input type="text" class="form-control" v-bind:name="'vehicleRego_' + index"
                                                required="required" v-model="v.rego" @change="validateRego">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="form-group" v-if="park.entry_fee_required">
                                            <label>Entry fee</label>
                                            <input type="checkbox" class="form-control" v-model="v.entry_fee"
                                                @change="updatePrices()">
                                        </div>
                                    </div>
                                </div>
                                <p v-if="park.entry_fee_required"><b>NOTE:</b> A vehicle entry fee is not required for
                                    the holder of
                                    a valid Park Pass.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-lg-12">
                    <div class="well">
                        <div class="row">
                            <div class="col-lg-6">
                                <div class="row">
                                    <div class="col-lg-12">
                                        <div class="form-group">
                                            <label for="Total Price">Total Price <span class="text-muted">(GST
                                                    inclusive.)</span></label>
                                            <div class="input-group">
                                                <span class="input-group-addon">AUD <i class="fa fa-usd"></i></span>
                                                <input type="text" class="form-control"
                                                    :placeholder="$filters.formatMoney(0, 2)"
                                                    v-bind:value="$filters.formatMoney(booking.price, 2)"
                                                    readonly="true">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-lg-12">
                                        <div class="form-group">
                                            <input type="checkbox" name="overrideCharge" class="form control"
                                                v-model="overrideCharge" />
                                            <label for="OverrideCharge">Override price charged </label>
                                            <div class="input-group" v-if="overrideCharge">
                                                <span class="input-group-addon">AUD <i class="fa fa-usd"></i></span>
                                                <input type="text" class="form-control" name="overridePrice"
                                                    :placeholder="$filters.formatMoney(0, 2)"
                                                    v-model="booking.override_price">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-lg-12">
                                        <div class="form-group" v-if="overrideCharge">
                                            <reason type="discount" name="overrideReason"
                                                v-model="booking.override_reason" :required="overrideCharge"></reason>
                                        </div>
                                        <div class="form-group" v-if="overrideCharge">
                                            <label class="control-label">Override reason detail:</label>
                                            <textarea id="reason_details" class="form-control"
                                                v-model="booking.override_reason_info" />
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-lg-12">
                                        <div class="form-group">
                                            <input type="checkbox" name="sendInvoice" class="form control"
                                                id="send_invoice" v-model="booking.send_invoice" />
                                            <label for="sendInvoice"><u>Don't</u> send invoice upon booking</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="row">
                                    <div class="col-lg-12">
                                        <p class="text-muted">
                                            Payments will need to be recorded against the booking once the booking is
                                            completed and
                                            the payment is received.
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="row">
                                    <div class="col-lg-12">
                                        <button type="button" class="btn btn-primary btn-lg pull-right"
                                            @click="bookNow()">
                                            Book</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
        <loader :isLoading="isLoading">{{ loading.join(' , ') }}...</loader>
        <modal :large="true" @cancel="finishBooking()" :force="true" :isModalOpen='isModalOpen'>
            <h1 slot="title">Tax Invoice</h1>
            <div class="row" height="500px">
                <div class="col-lg-12">
                    <iframe id="invoice_frame" width="100%" height="700px" class="embed-responsive-item"
                        frameborder="0"></iframe>
                </div>
            </div>
            <div slot="footer">
                <button id="okBtn" type="button" class="btn btn-default" @click="finishBooking()">Finalize
                    Booking</button>
            </div>
        </modal>
    </div>

</template>

<script setup>
import { $, getDateTimePicker, dateUtils, Moment, api_endpoints, formValidate, helpers, debounce, DateTime } from "../../hooks.js";
import loader from '../utils/loader.vue';
import modal from '../utils/bootstrap-modal.vue';
import reason from '../utils/reasons.vue';
import { computed, ref, watch, onMounted } from "vue";
import { useRouter, useRoute } from 'vue-router';
import { useStore } from "../../apps/store.js";

const router = useRouter()
const route = useRoute()

const store = useStore()
const overrideCharge = ref(false)
const isModalOpen = ref(false)
const bookingForm = ref(null)
const countries = ref([])
const selected_campsite = ref("")
const selected_arrival = ref("")
const selected_departure = ref("")
const priceHistory = ref(null)
const booking = ref({
    arrival: "",
    departure: "",
    guests: {
        adult: 2,
        concession: 0,
        child: 0,
        infant: 0
    },
    campground: "",
    campsites: [],
    campsite_classes: [],
    email: "",
    firstname: "",
    surname: "",
    postcode: "",
    country: "AU",
    phone: "",
    vehicle: "",
    price: "0",
    override_price: "0",
    override_reason: "",
    override_reason_info: "",
    send_invoice: true,
    parkEntry: {
        vehicles: 0,
    },
    entryFees: {
        vehicles: 0,
        motorbike: 0,
        concession: 0,
        entry_fee: 0,
        regos: []
    }
})
const loading = ref([])
const campground = ref({})
const guestsText = ref("")
const guestsPicker = ref([
    {
        id: "adult",
        name: "Adults (no concession)",
        amount: 2,
        description: ""
    },
    {
        id: "concession",
        name: "Concession",
        amount: 0,
        description: "",
        helpText: "accepted concession cards"
    },
    {
        id: "child",
        name: "Children",
        amount: 0,
        description: "Ages 6-16"
    },
    {
        id: "infant",
        name: "Infants",
        amount: 0,
        description: "Ages 0-5"
    },
])
const parkEntryPicker = ref([
    {
        id: "vehicle",
        name: "Vehicle",
        amount: 0,
        price: 0,
        description: "Vehicle Registration",
        rego: "",
        entry_fee: true
    },
    {
        id: "concession",
        name: "Concession",
        amount: 0,
        price: 0,
        description: "Concession Vehicle Registration",
        helpText: "accepted concession cards",
        rego: "",
        entry_fee: true
    },
    {
        id: "motorbike",
        name: "Motorbike",
        amount: 0,
        price: 0,
        description: "Motorbike Registration",
        rego: "",
        entry_fee: true
    }
])
const users = ref([])
const usersEmail = ref([])
const park = ref({
    entry_fee_required: false,
    entry_fee: 0
})
const parkEntryVehicles = ref([])
const parkPrices = ref({
    "id": null,
    "period_start": null,
    "period_end": null,
    "reason": 1,
    "details": "other",
    "vehicle": "0.00",
    "concession": "0.00",
    "motorbike": "0.00",
    "editable": false
})
const stayHistory = ref([])
const arrivalPicker = ref({})
const departurePicker = ref({})
const selected_campsite_class = ref(-1)
const booking_type = ref("campsite")
const booking_types = ref({
    CAMPSITE: "campsite",
    CLASS: "class"
})
const multibook_selected = ref([])


const isLoading = computed(function () {
    return loading.value.length > 0;
})
const maxEntryVehicles = computed(function () {
    var entries = (booking.value.parkEntry.vehicles <= 10) ? booking.value.parkEntry.vehicles : 10;
    booking.value.parkEntry.vehicles = entries;
    return entries;
})
const selectAll = computed({
    get: function () {
        return booking.value.campsites ? multibook_selected.value.length == booking.value.campsites.length : false;
    },
    set: function (value) {
        var selected = [];

        if (value) {
            booking.value.campsites.forEach(function (campsite) {
                selected.push(campsite.id);
            });
        }

        multibook_selected.value = selected;
        updatePrices();
    }
})
const selected_campsites = computed(function () {
    var results = [];
    if (booking_type.value == booking_types.value.CAMPSITE) {
        results = multibook_selected.value;
    } else {
        booking.value.campsite_classes.forEach(function (el) {
            for (var i = 0; i < el.selected_campsite_class; i++) {
                results.push(el.campsites[i]);
            }
        });
    }
    return results;
})
const isDisabled = computed(function () {
    var stat = [];
    booking.value.campsites.forEach(function (el) {
        stat.push(el.status);
    });
    return stat.find(function (value, index) {
        if (value == "booked" || value == "closed & booked") {
            return true;
        }
    });
})

watch(() => selected_campsite.value, function (value) {
    updatePrices();
})
watch(() => selected_campsite_class.value, function (value) {
    selected_campsite.value = booking.value.campsite_classes[value].campsites[0];
})
watch(() => selected_arrival.value, function (value) {
    if (booking.value.arrival) {
        $.each(stayHistory.value, function (i, his) {
            const interval = { start: dateUtils.parseDate(his.range_start, "dd/MM/yyyy", new Date()), end: dateUtils.parseDate(his.range_end, "dd/MM/yyyy", new Date()) }
            const arrivalDate = dateUtils.parseDate(booking.value.arrival, "yyyy-MM-dd", new Date());
            if (dateUtils.isWithinInterval(arrival, interval)) {
                console.log('updating departure date Options');
                departurePicker.value.updateOptions({
                    restrictions: {
                        maxDate: dateUtils.addDays(arrivalDate, his.max_days)
                    }
                })
                departurePicker.value.clear()
            }
        });
    }
    fetchSites();
    updatePrices();
})
watch(() => selected_departure.value, function (value) {
    fetchSites();
    updatePrices();
})
watch(() => booking_type.value, function (value) {
    fetchSites();
})


const fetchSites = function () {
    if (booking_type.value == booking_types.value.CAMPSITE) {
        fetchCampsites();
    }
    if (booking_type.value == booking_types.value.CLASS) {
        fetchCampsiteClasses();
    }
}
const validateRego = function (e) {
    formValidate.isNotEmpty(e.target);
}
const updatePrices = function () {
    booking.value.price = 0;
    var campsite_ids = selected_campsites.value;
    if (selected_campsite.value) {
        if (booking.value.arrival && booking.value.departure) {
            var arrival = Moment(booking.value.arrival, "YYYY-MM-DD");
            var departure = Moment(booking.value.departure, "YYYY-MM-DD");
            var nights = departure.diff(arrival, 'days');
            fetch(
                api_endpoints.campsites_current_price(),
                {
                    method: "POST",
                    body: {
                        campsites: campsite_ids,
                        arrival: arrival.format("YYYY-MM-DD"),
                        departure: departure.format("YYYY-MM-DD")
                    },
                    headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') }
                }
            ).then((response) => response.json()).then((data) => {
                priceHistory.value = null;
                priceHistory.value = data;
                generateBookingPrice();
            }).catch((error) => {
                console.log(error);
            });
        }
    }
}
const fetchCountries = function () {
    loading.value.push('fetching countries');
    fetch(api_endpoints.countries).then((response) => response.json()).then((data) => {
        countries.value = data;
        loading.value.splice('fetching countries', 1);
    }).catch((error) => {
        console.log(error);
        loading.value.splice('fetching countries', 1);
    });
}
const fetchCampsites = function () {
    if (selected_arrival.value && selected_departure.value) {
        loading.value.push('fetching campsites');
        fetch(api_endpoints.available_campsites(
            booking.value.campground,
            Moment(booking.value.arrival, "YYYY-MM-DD").format("YYYY/MM/DD"),
            Moment(booking.value.departure, "YYYY-MM-DD").format("YYYY/MM/DD")
        )).then((response) => response.json()).then((data) => {
            
            booking.value.campsites = data;
            if (booking.value.campsites.length > 0) {
                selected_campsite.value = booking.value.campsites[0].id;
            }
            loading.value.splice('fetching campsites', 1);
        }).catch((error) => {
            console.log(error);
            loading.value.splice('fetching campsites', 1);
        });
    }
}
const fetchCampsiteClasses = function () {
    if (selected_arrival.value && selected_departure.value) {
        loading.value.push('fetching campsite classes');
        fetch(api_endpoints.available_campsite_classes(
            booking.value.campground,
            Moment(booking.value.arrival, "YYYY-MM-DD").format("YYYY/MM/DD"),
            Moment(booking.value.departure, "YYYY-MM-DD").format("YYYY/MM/DD")
        )).then((response) => response.json()).then((data) => {
            booking.value.campsite_classes = data;
            if (booking.value.campsite_classes.length > 0) {
                selected_campsite.value = booking.value.campsite_classes[0].campsites[0];
                selected_campsite_class.value = 0;
            }
            loading.value.splice('fetching campsite classes', 1);
        }).catch((error) => {
            console.log(error);
            loading.value.splice('fetching campsite classes', 1);
        });
    }
}
const fetchCampground = function () {
    loading.value.push('fetching campground');
    var cgId = route.params.cg;
    fetch(api_endpoints.campground(cgId)).then((response) => response.json()).then((data) => {
        campground.value = data;
        booking.value.campground = campground.value.id;
        booking_type.value = (campground.value.site_type == 0) ? booking_types.value.CAMPSITE : booking_types.value.CLASS;
        fetchStayHistory();
        fetchCampsites();
        fetchPark();
        addEventListeners();
        loading.value.splice('fetching campground', 1);
    }).catch((error) => {
        console.log(error);
        loading.value.splice('fetching campground', 1);
    });
}
const fetchStayHistory = function () {
    loading.value.push('fetching stay history');
    fetch(api_endpoints.campgroundStayHistory(campground.value.id)).then((response) => response.json()).then((data) => {
        if (data.length > 0) {
            stayHistory.value = data;
        }
        loading.value.splice('fetching stay history', 1);
    }).catch((error) => {
        console.log(error);
        loading.value.splice('fetching stay history', 1);
    });
}
const fetchPark = function () {
    loading.value.push('fetching park');
    fetch(api_endpoints.park(campground.value.park)).then((response) => response.json()).then((data) => {
        park.value = data;
        loading.value.splice('fetching park', 1);
    }).catch((error) => {
        console.log(error);
        loading.value.splice('fetching park', 1);
    });
}
const addEventListeners = function () {
    const today = new DateTime().startOf('date')
    selected_arrival.value = today;
    booking.value.arrival = today;
    const arrivalElement = $(bookingForm.value.arrival).closest('.date');
    const departureElement = $(bookingForm.value.departure).closest('.date');

    arrivalPicker.value = getDateTimePicker(arrivalElement, {
        defaultDate: today,
        restrictions: { minDate: new today, }
    });
    departurePicker.value = getDateTimePicker(departureElement, {
        useCurrent: false,
    });

    arrivalElement.on('change.td', function (e) {
        booking.value.arrival = dateUtils.formatDate(arrivalPicker.value.dates.lastPicked, 'yyyy-MM-dd');
        selected_arrival.value = booking.value.arrival;
        selected_departure.value = "";
        booking.value.departure = "";
        var selected_date = e.date.clone();//Object.assign({},e.date);
        var minDate = selected_date.clone().add(1, 'days');
        var maxDate = minDate.clone().add(180, 'days');
        departurePicker.value.clear()
        departurePicker.value.updateOptions({
            restrictions: { minDate: minDate, maxDate: maxDate },
        })
    });
    departureElement.on('change.td', function (e) {
        if (departurePicker.value.dates.lastPicked) {
            booking.value.departure = dateUtils.formatDate(departurePicker.value.dates.lastPicked, 'yyyy-MM-dd');
            selected_departure.value = booking.value.departure;
        } else {
            booking.value.departure = null;
            selected_departure.value = booking.value.departure;
        }
    });
    fetch(api_endpoints.campgroundCampsites(campground.value.id)).then((response) => response.json()).then((_campsites) => {
        const campsites = _campsites;
        fetch(api_endpoints.campsite_current_price(campsites[0].id, Moment().format("YYYY-MM-DD"), Moment().add(1, 'days').format("YYYY-MM-DD")))
        .then((response) => response.json()).then((data) => {
            priceHistory.value = null;
            priceHistory.value = data;
            loading.value.splice('updating prices', 1);
        }).catch((error) => {
            console.log(error);
            loading.value.splice('updating prices', 1);
        });
    }, (error) => {
        console.log(error);
    });
}
const addGuestCount = function (guest) {
    guest.amount += 1;
    switch (guest.id) {
        case 'adult':
            booking.value.guests.adult = guest.amount;
            break;
        case 'concession':
            booking.value.guests.concession = guest.amount;
            break;
        case 'child':
            booking.value.guests.child = guest.amount;
            break;
        case 'infant':
            booking.value.guests.infant = guest.amount;
            break;
        default:
    }
    generateGuestCountText();
}
const removeGuestCount = function (guest) {
    guest.amount = (guest.amount > 0) ? guest.amount - 1 : 0;
    switch (guest.id) {
        case 'adult':
            booking.value.guests.adult = guest.amount;
            break;
        case 'concession':
            booking.value.guests.concession = guest.amount;
            break;
        case 'child':
            booking.value.guests.child = guest.amount;
            break;
        case 'infant':
            booking.value.guests.infant = guest.amount;
            break;
        default:
    }
    generateGuestCountText();
}
const generateGuestCountText = function () {
    var text = "";
    $.each(guestsPicker, function (i, g) {
        (i != guestsPicker.length - 1) ? (g.amount > 0) ? text += g.amount + " " + g.name + ",  " : "" : (g.amount > 0) ? text += g.amount + " " + g.name + " " : "";
    });
    guestsText.value = text.replace(/,\s*$/, "");
    generateBookingPrice();
}
const generateBookingPrice = function () {
    booking.value.price = 0;
    if (park.value.entry_fee_required) {
        fetchParkPrices(function () {
            $.each(priceHistory.value, function (i, price) {
                for (var guest in booking.value.guests) {
                    if (booking.value.guests.hasOwnProperty(guest)) {
                        booking.value.price += booking.value.guests[guest] * price.rate[guest];
                    }
                }
            });
            updateParkEntryPrices()
            booking.value.price = booking.value.price + booking.value.entryFees.entry_fee;
        });
    } else {
        $.each(priceHistory.value, function (i, price) {
            for (var guest in booking.value.guests) {
                if (booking.value.guests.hasOwnProperty(guest)) {
                    booking.value.price += booking.value.guests[guest] * price.rate[guest];
                }
            }
        });
    }
}
const updateParkEntryPrices = function () {
    booking.value.entryFees.entry_fee = 0;
    if (selected_campsite.value) {
        if (booking.value.arrival && booking.value.departure) {
            $.each(parkEntryVehicles.value, function (i, entry) {
                entry = JSON.parse(JSON.stringify(entry));
                if (parkPrices.value && entry.entry_fee) {
                    switch (entry.id) {
                        case 'vehicle':
                            booking.value.entryFees.entry_fee += parseInt(parkPrices.value.vehicle);
                            booking.value.entryFees.vehicle++;
                            break;
                        case 'motorbike':
                            booking.value.entryFees.entry_fee += parseInt(parkPrices.value.motorbike);
                            booking.value.entryFees.motorbike++;
                            break;
                        case 'concession':
                            booking.value.entryFees.entry_fee += parseInt(parkPrices.value.concession);
                            booking.value.entryFees.concession++;
                            break;
                    }
                }
            });
        }
    }
}
const fetchUsers = debounce(function (event) {
    fetch(api_endpoints.usersLookup(booking.value.email)).then((response) => response.json()).then((data) => {
        users.value = data;
        usersEmail.value = [];
        $.each(users.value, function (i, u) {
            usersEmail.value.push(u.email);
        });
        autofillUser();
    });
}, 1000)
const fetchParkPrices = function (calcprices) {
    if (booking.value.arrival) {
        fetch(api_endpoints.park_current_price(park.value.id, booking.value.arrival)).then((response) => response.json())
            .then((data) => {
            var resp = data;
            if (resp.constructor != Array) {
                parkPrices.value = data;
            } else {
                parkPrices.value.vehicle = "0.00";
                parkPrices.value.motorbike = "0.00";
                parkPrices.value.concession = "0.00";
            }
            calcprices();
        });
    } else {
        parkPrices.value.vehicle = "0.00";
        parkPrices.value.motorbike = "0.00";
        parkPrices.value.concession = "0.00";
        calcprices();
    }
}
const autofillUser = function (event) {
    $.each(users.value, function (i, user) {
        if (user.email == booking.value.email) {
            booking.value.firstname = user.first_name;
            booking.value.surname = user.last_name;
            booking.value.phone = user.mobile_number;
            if (user.profile_addresses[0]) {
                booking.value.postcode = user.profile_addresses[0].postcode;
                booking.value.country = user.profile_addresses[0].country;
            }
            return false;
        }
    })
}
const bookNow = function () {
    if (isFormValid()) {
        loading.value.push('processing booking');
        booking.value.entryFees = {
            vehicle: 0,
            motorbike: 0,
            concession: 0,
            entry_fee: 0,
            regos: []
        };
        $.each(parkEntryVehicles.value, function (i, entry) {
            entry = JSON.parse(JSON.stringify(entry));
            if (entry.rego != null || entry.rego != "null") {
                booking.value.entryFees.regos.push({
                    type: entry.id,
                    rego: entry.rego,
                    entry_fee: entry.entry_fee
                });
            }
            switch (entry.id) {
                case 'vehicle':
                    booking.value.entryFees.entry_fee += parseInt(parkPrices.value.vehicle);
                    booking.value.entryFees.vehicle++;
                    break;
                case 'motorbike':
                    booking.value.entryFees.entry_fee += parseInt(parkPrices.value.motorbike);
                    booking.value.entryFees.motorbike++;
                    break;
                case 'concession':
                    booking.value.entryFees.entry_fee += parseInt(parkPrices.value.concession);
                    booking.value.entryFees.concession++;
                    break;
            }
        });
        const bookingObject = {
            arrival: booking.value.arrival,
            departure: booking.value.departure,
            guests: booking.value.guests,
            campsites: selected_campsites.value,
            costs: {
                campground: priceHistory.value,
                parkEntry: parkPrices.value,
                total: booking.value.price
            },
            override_price: booking.value.override_price,
            override_reason: booking.value.override_reason,
            override_reason_info: booking.value.override_reason_info,
            do_not_send_invoice: booking.value.send_invoice,
            customer: {
                email: booking.value.email,
                first_name: booking.value.firstname,
                last_name: booking.value.surname,
                phone: booking.value.phone,
                country: booking.value.country,
                postcode: booking.value.postcode,
            },
            regos: booking.value.entryFees.regos
        }
        store.dispatch("updateAlert", {
            visible: false,
            type: "danger",
            message: ""
        });
        fetch(api_endpoints.bookings, {
            method: "POST",
            body: booking,
            headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        }).then((response) => response.json()).then((data) => {
            loading.value.splice('processing booking', 1);
            var frame = $('#invoice_frame');
            frame[0].src = '/ledger/payments/invoice/' + data.invoices[0];
            isModalOpen.value = false;
            router.push({ name: "booking-dashboard" });
        }).catch((error) => {
            let error_str = helpers.apiVueResourceError(error);
            store.dispatch("updateAlert", {
                visible: true,
                type: "danger",
                message: error_str
            });
            loading.value.splice('processing booking', 1);
        });
    }
}
const finishBooking = function () {
    isModalOpen.value = false;
    router.push({ name: "booking-dashboard" });
}
const isFormValid = function () {
    return ($(bookingForm.value).valid());
}
const noDuplicateRego = function (source) {
    var listRego = parkEntryVehicles.value.filter(function (el) {
        return el.rego == source.value;
    });
    return listRego.length <= 1;
}
const overrideChargeReason = function () {
    if (overrideCharge) {
        if (booking.value.override_price != null && booking.value.override_reason == "") {
            return false;
        }
    }
    return true;
}
const updateCampsiteCount = function (c) {
    c.selected_campsite_class = Math.max(0, Math.min(c.selected_campsite_class, c.campsites.length));
    updatePrices();
}
const addFormValidations = function () {
    var options = {
        rules: {
            arrival: "required",
            departure: "required",
            guests: "required",
            campsite: "required",
            email: {
                required: true,
                email: true
            },
            firstname: "required",
            surname: "required",
            phone: "required",
            postcode: "required",
            country: "required",
            price_level: "required",
            open_reason: "required",
            overrideReason: {
                required: {
                    depends: function (el) {
                        return overrideChargeReason(el);
                    }
                }
            }
        },
        messages: {
            firstname: "Fill in all details",
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
    };
    for (var i = 0; i < booking.value.parkEntry.vehicles; i++) {
        options.rules['vehicleRego_' + i] = {
            required: true,
            noDuplicateRego: true
        };
        options.messages['vehicleRego_' + i] = {
            required: 'Fill in vehicle details',
            noDuplicateRego: 'Duplicate regos not permitted.If unknown add number, e.g. Hire1, Hire2'
        };
    }
    var form = $(bookingForm.value);
    form.data('validator', null);
    $.validator.addMethod('noDuplicateRego', function (value, el) {
        return noDuplicateRego(el);
    });
    form.validate(options);
}
const addVehicleCount = function (park_entry) {
    var count = booking.value.parkEntry.vehicles
    if (park_entry.amount < 10 && count < 10) {
        park_entry.amount = (park_entry.amount < 10) ? park_entry.amount += 1 : park_entry.amount;
        booking.value.parkEntry.vehicles++;
        var new_entry = JSON.parse(JSON.stringify(park_entry));
        if (!entry_fee_required.value) {
            new_entry.entry_fee = false;
        }
        parkEntryVehicles.value.push(new_entry);
    }
    booking.value.price = booking.value.price - booking.value.entryFees.entry_fee;
    updateParkEntryPrices();
    booking.value.price = booking.value.price + booking.value.entryFees.entry_fee;
    addFormValidations();
}
const removeVehicleCount = function (park_entry) {
    var count = booking.value.parkEntry.vehicles
    if (park_entry.amount > 0 && count > 0) {
        var found = false;
        for (var i = park_entry.amount - 1; i >= 0; i--) {
            for (var j = parkEntryVehicles.value.length - 1; j >= 0; j--) {
                if (park_entry.description == parkEntryVehicles.value[j].description) {
                    park_entry.amount = (park_entry.amount > 0) ? park_entry.amount -= 1 : park_entry.amount;
                    parkEntryVehicles.value.splice(j, 1);
                    booking.value.parkEntry.vehicles--;
                    found = true;
                    break;
                }
            }
            if (found) {
                break;
            }
        }
    }
    booking.value.price = booking.value.price - booking.value.entryFees.entry_fee;
    updateParkEntryPrices();
    booking.value.price = booking.value.price + booking.value.entryFees.entry_fee;
    addFormValidations();
}

onMounted(function () {
    bookingForm.value = document.forms.bookingForm;
    fetchCampground();
    fetchCountries();
    generateGuestCountText();
    addFormValidations();
})

</script>

<style lang="css">
.pricing {
    margin-left: 25px;
    font-size: 20px;
}

.awesomplete {
    width: 100%;
}

.dropdown-menu:before {
    position: absolute;
    top: -12px;
    left: 12px;
    display: inline-block;
    border-right: 12px solid transparent;
    border-bottom: 12px solid #ccc;
    border-left: 12px solid transparent;
    border-bottom-color: rgba(46, 109, 164, 1);
    content: '';
}

.dropdown-menu {
    top: 120%;
    width: 300px;
}

.guests li {
    padding: 10px;
    margin-right: 10px;
    border-bottom: 1px solid #ccc;
}

.guests li:last-child {
    border-bottom: 0;
}

.guests.item {
    line-height: 2;
}

.btn-guest {
    color: #ccc;
    background-color: #fff;
    border-color: #ccc;
}

.required::after {
    content: '*';
    color: red;
}

.tab-content {
    padding: 15px 0px;
}

.nav-tabs {
    margin-top: 15px;
}
</style>
