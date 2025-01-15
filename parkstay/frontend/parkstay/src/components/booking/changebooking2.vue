<template lang="html">
    <div id="changeBooking">
        <form v-show="!isLoading" name="bookingForm">
            <div class="row">
                <div class="col-lg-12">
                    <div class="well">
                        <div class="row">
                            <div class="col-md-12">
                                <h3 class="text-primary">{{ booking.full_name }}</h3>
                            </div>
                            <div class="col-md-8 col-md-offset-1">
                                <div class="row form-horizontal">
                                    <div class="col-md-12">
                                        <div class="form-group">
                                            <div class="col-md-4">
                                                <label class="control-label pull-left required" for="Dates">Campground:
                                                </label>
                                            </div>
                                            <div class="col-md-8">
                                                <select @change="updateCampground" class="form-control"
                                                    name="campground" v-model="booking.campground">
                                                    <option v-for="c in onlineCampgrounds" :value="c.id">{{ c.name }}
                                                    </option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="form-group"
                                            v-if="booking.campground != null || booking.campground != ''">
                                            <div class="col-md-4">
                                                <label class="control-label pull-left required" for="Dates">Camp Site:
                                                </label>
                                            </div>
                                            <div class="col-md-8" v-if="campsites.length > 0"></div>
                                            <div class="col-md-8">
                                                <select class="form-control" style="width: 100%;" id="multi-campsites"
                                                    name="campground" placeholder="" multiple
                                                    v-model="selected_campsites">
                                                    <option v-for="c in campsites" v-bind:value="c.id">{{ c.name }} -
                                                        {{ c.status }}</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="col-md-8" v-else>
                                            <h4>Sorry, no available campsites were found.</h4>
                                        </div>
                                        <div class="form-group">
                                            <div class="col-md-4">
                                                <label class="control-label pull-left required" for="Dates">Dates:
                                                </label>
                                            </div>
                                            <div class="col-md-4">
                                                <div class="input-group date" id="dateArrival">
                                                    <input type="text" class="form-control" name="arrival"
                                                        placeholder="Arrival" v-model="selected_arrival">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="col-md-4">
                                                <div class="input-group date" id="datedeparture">
                                                    <input type="text" class="form-control" name="departure"
                                                        placeholder="Departure" v-model="selected_departure">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <div class="col-md-4">
                                                <label class="control-label pull-left required" for="Campground">Guests:
                                                </label>
                                            </div>
                                            <div class="col-md-8">
                                                <div class="dropdown guests">
                                                    <input type="text" readonly class="form-control dropdown-toggle"
                                                        name="guests" placeholder="Guests" data-toggle="dropdown"
                                                        aria-haspopup="true" aria-expanded="true" v-model="guestsText">
                                                    <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
                                                        <li v-for="guest in guestsPicker">
                                                            <div class="row">
                                                                <div class="col-sm-8">
                                                                    <span class="item">
                                                                        {{ guest.amount }} {{ guest.name }} <span
                                                                            style="color:#888;font-weight:300;font-size:12px;">{{
                                                                            guest.description }}</span>
                                                                    </span>
                                                                    <br /><a href="#" class="text-info"
                                                                        v-show="guest.helpText">{{ guest.helpText }}</a>
                                                                </div>
                                                                <div class="pull-right">
                                                                    <div class="btn-group btn-group-sm">
                                                                        <button type="button" class="btn btn-guest"
                                                                            @click.prevent.stop="addGuestCount(guest)"><span
                                                                                class="glyphicon glyphicon-plus"></span></button>
                                                                        <button type="button" class="btn btn-guest"
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
                            <div class="col-lg-8 col-md-offset-1">
                                <div class="row form-horizontal">
                                    <div class="col-md-12">
                                        <div class="form-group">
                                            <label for="vehicles" class="required col-md-4">Number of Vehicles</label>
                                            <div class="dropdown guests col-md-8">
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
                                                                    v-show="park_entry.helpText">{{ park_entry.helpText
                                                                    }}</a>
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
                                <div class="row" v-for="v in parkEntryVehicles">
                                    <div class="col-md-6 col-md-offset-4">
                                        <div class="form-group">
                                            <label class="required">{{ v.description }}</label>
                                            <input type="text" class="form-control vehicleLookup" required="required"
                                                v-model="v.rego" @change="validateRego">
                                        </div>
                                    </div>
                                    <div class="col-md-2" v-if="park.entry_fee_required">
                                        <label>Entry Fee</label>
                                        <div class="form-check">
                                            <label class="form-check-label">
                                                <input class="form-check-input" type="checkbox" required="required"
                                                    v-model="v.entry_fee" @change="updatePrices">
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-8 col-md-offset-1">
                                <div class="row form-horizontal" v-if="initialised">
                                    <div class="col-md-12">
                                        <div class="form-group">
                                            <label class="col-md-4" for="Total Price">Total Price <span
                                                    class="text-muted">(GST inclusive.)</span></label>
                                            <div class="col-md-8">
                                                <div class="input-group">
                                                    <span class="input-group-addon">AUD <i class="fa fa-usd"></i></span>
                                                    <input type="text" class="form-control"
                                                        :placeholder="$filters.formatMoney(0, 2)"
                                                        :value="$filters.formatMoney(booking_price, 2)" readonly="true">
                                                </div>
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <label class="col-md-4" for="Old Total Price">Old Total Price <span
                                                    class="text-muted">(GST inclusive.)</span></label>
                                            <div class="col-md-8">
                                                <div class="input-group">
                                                    <span class="input-group-addon">AUD <i class="fa fa-usd"></i></span>
                                                    <input type="text" class="form-control"
                                                        :placeholder="$filters.formatMoney(0, 2)"
                                                        :value="$filters.formatMoney(booking.cost_total, 2)"
                                                        readonly="true">
                                                </div>
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <label class="col-md-4" for="Amount Paid">Amount Paid</label>
                                            <div class="col-md-8">
                                                <div class="input-group">
                                                    <span class="input-group-addon">AUD <i class="fa fa-usd"></i></span>
                                                    <input type="text" class="form-control"
                                                        :placeholder="$filters.formatMoney(0, 2)"
                                                        :value="$filters.formatMoney(booking.amount_paid, 2)"
                                                        readonly="true">
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                        </div>
                        <div class="row" style="margin-top:20px;">
                            <div class="col-md-12">
                                <button type="button" :disabled="campsites.length == 0"
                                    class="btn btn-primary btn-lg pull-right" style="margin-top:15px;"
                                    @click="updateNow()">Save Changes</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
        <loader :isLoading="isLoading">{{ loading.join(' , ') }}...</loader>
    </div>

</template>

<script setup>
import booking_helpers from './booking_helpers'
import {
    $,
    getDateTimePicker, dateUtils, DateTime,
    Moment,
    api_endpoints,
    formValidate,
    helpers
} from "../../hooks.js";
import loader from '../utils/loader.vue';
import {
    mapGetters
} from 'vuex'
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from "../../apps/store.js";

const store = useStore()

const router = useRouter()
const bookingForm = ref(null)
const selected_campsite = ref("")
const selected_arrival = ref("")
const selected_departure = ref("")
const priceHistory = ref(null)
const booking = ref({
    parkEntry: {
        vehicles: 0
    },
})
const campsites = ref([])
const loading = ref([])
const guestsText = ref("")
const campground = ref(null)
const guestsPicker = [{
    id: "adults",
    name: "Adults (no concession)",
    amount: 0,
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
    id: "children",
    name: "Children",
    amount: 0,
    description: "Ages 6-16"
},
{
    id: "infants",
    name: "Infants",
    amount: 0,
    description: "Ages 0-5"
},
]
const parkEntryPicker = [{
    id: "vehicle",
    name: "Vehicle",
    amount: 0,
    price: 0,
    description: "Vehicle Registration",
    rego: "",
    entry_fee: false
},
{
    id: "concession",
    name: "Concession",
    amount: 0,
    price: 0,
    description: "Concession Vehicle Registration",
    helpText: "accepted concession cards",
    rego: "",
    entry_fee: false
},
{
    id: "motorbike",
    name: "Motorbike",
    amount: 0,
    price: 0,
    description: "Motorbike Registration",
    rego: "",
    entry_fee: false
}
]
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
const campsite_classes = ref([])
const selected_campsites = ref([])
const booking_type = ref("campsite")
const initialised = ref(false)
const fetchingSites = ref(false)
const booking_price = ref(0)


const isLoading = computed(() => {
    return loading.value.length > 0;
})
const maxEntryVehicles = computed(() => {
    var entries = (booking.value.parkEntry.vehicles <= 10) ? booking.value.parkEntry.vehicles : 10;
    booking.value.parkEntry.vehicles = entries;
    return entries;
})
const onlineCampgrounds = computed(() => {
    return campgrounds.value.filter(c => c.campground_type === 0);
})
const campgrounds = computed(() => store.getters.campgrounds)

watch(() => selected_campsite.value, function () {
    updatePrices();
})
watch(() => selected_arrival.value, function () {
    if (booking.value.arrival) {
        $.each(stayHistory.value, function (i, his) {
            const interval = {
                start: dateUtils.parseDate(his.range_start, "dd/MM/yyyy", new Date()),
                end: dateUtils.parseDate(his.range_end, "dd/MM/yyyy", new Date())
            };
            const arrivalDate = dateUtils.parseDate(booking.value.arrival, 'yyyy-MM-dd', new Date());
            if (dateUtils.isWithinInterval(arrivalDate, interval)) {
                departurePicker.value.updateOptions({
                    restrictions: {
                        maxDate: dateUtils.addDays(arrivalDate, his.max_days)
                    }
                })
                departurePicker.value.clear()
            }
        });
    }
    if (initialised.value) {
    }
    fetchSites();
    initSelectTwo();
    addEventListeners();
    updatePrices();
})
watch(() => selected_departure.value, function () {
    if (initialised.value) {
    }
    fetchSites();
    initSelectTwo();
    updatePrices();
})
watch(() => booking_type.value, function () {
    //vm.fetchSites();
})

const validateRego = function (e) {
    formValidate.isNotEmpty(e.target);
}
const updateCampground = function () {
    campground.value = booking.value.campground ? campgrounds.value.find(c => parseInt(c.id) === parseInt(booking.value.campground)) : null;
    fetchSites();
}
const initSelectTwo = function () {
    setTimeout(function () {
        $('#multi-campsites').select2({
            theme: 'bootstrap',
            allowClear: true,
            placeholder: "Select Campsites",
            tags: false,
        }).
            on("select2:select", function (e) {
                selected_campsites.value = $(e.currentTarget).val();
            }).
            on("select2:unselect", function (e) {
                selected_campsites.value = $(e.currentTarget).val();
            });
    }, 100)
}
const updatePrices = function () {
    var campsite_ids = selected_campsites.value;
    booking.value.price = 0;
    if (selected_campsite.value) {
        if (booking.value.arrival && booking.value.departure) {
            var arrival = Moment(selected_arrival.value, "DD/MM/YYYY");
            var departure = Moment(selected_departure.value, "DD/MM/YYYY");
            var nights = departure.diff(arrival, 'days');
            loading.value.push('updating prices');
            fetch(api_endpoints.campsites_current_price(),
                {
                    method: "POST",
                    body: {
                        campsites: campsite_ids,
                        arrival: arrival.format("YYYY-MM-DD"),
                        departure: departure.format("YYYY-MM-DD")
                    },
                    headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') }
                },
            ).then((response) => response.json()).then((data) => {
                priceHistory.value = null;
                priceHistory.value = data;
                generateBookingPrice();
                loading.value.splice('updating prices', 1);
            }, (error) => {
                console.log(error);
                loading.value.splice('updating prices', 1);
            });
        }
    }
}
const generateBookingPrice = function () {
    booking.value.price = 0;
    if (park.value.entry_fee_required) {
        fetchParkPrices(function () {
            $.each(priceHistory.value, function (i, price) {
                for (var guest in booking.value.guests) {
                    switch (guest) {
                        case 'adults':
                            booking.value.price += booking.value.guests[guest] * parseFloat(price.rate['adult']);
                            break;
                        case 'concession':
                            booking.value.price += booking.value.guests[guest] * parseFloat(price.rate['concession']);
                            break;
                        case 'children':
                            booking.value.price += booking.value.guests[guest] * parseFloat(price.rate['child']);
                            break;
                        case 'infants':
                            booking.value.price += booking.value.guests[guest] * parseFloat(price.rate['infant']);
                            break;
                    }
                }
            });
            updateParkEntryPrices()
            booking.value.price = booking.value.price + booking.value.entryFees.entry_fee;
            booking_price.value = booking.value.price;
        });
    } else {
        $.each(priceHistory.value, function (i, price) {
            for (var guest in booking.value.guests) {
                switch (guest) {
                    case 'adults':
                        booking.value.price += booking.value.guests[guest] * parseFloat(price.rate['adult']);
                        break;
                    case 'concession':
                        booking.value.price += booking.value.guests[guest] * parseFloat(price.rate['concession']);
                        break;
                    case 'children':
                        booking.value.price += booking.value.guests[guest] * parseFloat(price.rate['child']);
                        break;
                    case 'infants':
                        booking.value.price += booking.value.guests[guest] * parseFloat(price.rate['infant']);
                        break;
                }
            }
        });
        booking.value.price = booking.value.price + booking.value.entryFees.entry_fee;
        booking_price.value = booking.value.price;
    }
}
const fetchSites = function () {
    if (!fetchingSites.value) {
        if (selected_arrival.value && selected_departure.value) {
            fetchingSites.value = true;
            loading.value.push('fetching campsites');
            fetch(api_endpoints.available_campsites_booking(booking.value.campground, booking.value.arrival, booking.value.departure, booking.value.id)).then((response) => response.json()).then((data) => {
                fetchingSites.value = false;
                campsites.value = data;
                if (campsites.value.length > 0) {
                    let c_lookup = campsites.value.find(c => parseInt(c.id) === parseInt(selected_campsite.value));
                    if (c_lookup == null || c_lookup == undefined) {
                        selected_campsite.value = campsites.value[0].id;
                    }
                }
                loading.value.splice('fetching campsites', 1);
            }).catch((response) => {
                console.log(response);
                loading.value.splice('fetching campsites', 1);
                fetchingSites.value = false;
            });
        }
    }
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
        loading.value.splice('fetching park details', 1);
    }).catch((error) => {
        console.log(error);
        loading.value.splice('fetching park details', 1);
    });
}
const addEventListeners = function () {
    const today = new DateTime().startOf("date")

    const arrivalPickerElement = $(bookingForm.value.arrival).closest('.date');
    const departurePickerElement = $(bookingForm.value.departure).closest('.date');
    arrivalPicker.value = getDateTimePicker(arrivalPickerElement, {
        restrictions: {
            minDate: today,
        }
    });
    departurePicker.value = getDateTimePicker(departurePickerElement, {
        minDate: dateUtils.addDays(today, 1),
        useCurrent: false,
    });
    arrivalPickerElement.on('change.td', function (e) {
        const date = arrivalPicker.value.dates.lastPicked;
        if (!date) return
        booking.value.arrival = date ? dateUtils.formatDate(date, 'yyyy-MM-dd') : null;
        selected_arrival.value = booking.value.arrival;
        // selected_departure.value = "";
        // booking.value.departure = "";
        var selected_date = new Date(date);
        var minDate = dateUtils.addDays(selected_date, 1);
        departureDate.value = departurePicker.value.dates.lastPicked
        if (departureDate && selected_date > date) {
            departurePicker.value.updateOptions({
                restrictions: {
                    minDate: dateUtils.addDays(date, 1),
                    maxDate: dateUtils.addDays(minDate, 180)
                }
            })
            departurePicker.value.clear()
        }
    });
    departurePickerElement.on('change.td', function (e) {
        date.value = departurePicker.value.dates.lastPicked;
        booking.value.departure = date ? dateUtils.formatDate(date, 'yyyy-MM-dd') : null;
        selected_departure.value = date ? booking.value.departure : null;
    });
    // Set the initial minimum departure date for the booking

    console.log('addEventListeners');
    departurePicker.value.trigger('change');
    arrivalPicker.value.trigger('change');
}
const addGuestCount = function (guest) {
    guest.amount += 1;
    switch (guest.id) {
        case 'adults':
            booking.value.guests.adults = guest.amount;
            break;
        case 'concession':
            booking.value.guests.concession = guest.amount;
            break;
        case 'children':
            booking.value.guests.children = guest.amount;
            break;
        case 'infants':
            booking.value.guests.infants = guest.amount;
            break;
        default:

    }
    generateGuestCountText();
}
const removeGuestCount = function (guest) {
    guest.amount = (guest.amount > 0) ? guest.amount - 1 : 0;
    switch (guest.id) {
        case 'adults':
            booking.value.guests.adults = guest.amount;
            break;
        case 'concession':
            booking.value.guests.concession = guest.amount;
            break;
        case 'children':
            booking.value.guests.children = guest.amount;
            break;
        case 'infants':
            booking.value.guests.infants = guest.amount;
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
    if (initialised.value) {
        generateBookingPrice();
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
                            //booking.value.entryFees.vehicle++;
                            break;
                        case 'motorbike':
                            booking.value.entryFees.entry_fee += parseInt(parkPrices.value.motorbike);
                            //booking.value.entryFees.motorbike++;
                            break;
                        case 'concession':
                            booking.value.entryFees.entry_fee += parseInt(parkPrices.value.concession);
                            //booking.value.entryFees.concession++;
                            break;
                        default:
                            break;
                    }
                }
            });
        }
    }
}
const fetchParkPrices = function (calcprices) {
    if (booking.value.arrival) {
        var arrival = Moment(booking.value.arrival, "DD/MM/YYYY").format("YYYY-MM-DD");
        fetch(api_endpoints.park_current_price(park.value.id, arrival)).then((response) => response.json()).then((data) => {
            if (Array.isArray(data)) {
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
const updateNow = function () {
    let booking = {};
    // Deal with booking vehicles
    if (isFormValid()) {
        loading.value.push('updating booking');
        booking.entryFees = {
            vehicle: 0,
            motorbike: 0,
            concession: 0,
            regos: []
        };
        $.each(parkEntryVehicles.value, function (i, entry) {
            entry = JSON.parse(JSON.stringify(entry));
            if (entry.rego != null || entry.rego != "null") {
                booking.entryFees.regos.push({
                    type: entry.id,
                    rego: entry.rego,
                    entry_fee: entry.entry_fee
                });
            }
            switch (entry.id) {
                case 'vehicle':
                    booking.entryFees.vehicle++;
                    break;
                case 'motorbike':
                    booking.entryFees.motorbike++;
                    break;
                case 'concession':
                    booking.entryFees.concession++;
                    break;

            }
        });
        // Deal with the rest of the booking
        booking.arrival = booking.value.arrival;
        booking.departure = booking.value.departure;
        booking.guests = booking.value.guests;
        campsites.value = selected_campsites.value;
        booking.campground = booking.value.campground
        // Hide the alert
        store.dispatch("updateAlert", {
            visible: false,
            type: "danger",
            message: ""
        });
        fetch(api_endpoints.booking(booking.value.id), {
            body: booking,
            method: "PUT",
            headers: {
                'X-CSRFToken': helpers.getCookie('csrftoken')
            },
        }).then((response) => response.json()).then((data) => {
            loading.value.splice('updating booking', 1);
            finishBooking();
        }, (error) => {
            let error_str = helpers.apiVueResourceError(error);
            store.dispatch("updateAlert", {
                visible: true,
                type: "danger",
                message: error_str
            });
            loading.value.splice('updating booking', 1);
        });
    }
}
const finishBooking = function () {
    router.push({
        name: "booking-dashboard"
    });
}
const isFormValid = function () {
    return (validateParkEntry() && $(bookingForm.value).valid());
}
const validateParkEntry = function () {
    var isValid = true;
    let filled = 0;
    $('.vehicleLookup').each((i, d) => {
        $(d).val() != '' ? filled++ : '';
    });
    if (booking.value.parkEntry.vehicles > 0) {
        if (booking.value.parkEntry.vehicles > filled) {
            isValid = false;
        }
    }
    return isValid;
}
const addFormValidations = function () {
    $(bookingForm.value).validate({
        rules: {
            arrival: "required",
            departure: "required",
            guests: "required",
            campsite: "required",
            price_level: "required"
        },
        messages: {},
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
const addVehicleCount = function (park_entry) {

    var count = booking.value.parkEntry.vehicles
    if (park_entry.amount < 10 && count < 10) {
        park_entry.amount = (park_entry.amount < 10) ? park_entry.amount += 1 : park_entry.amount;
        booking.value.parkEntry.vehicles++;
        parkEntryVehicles.value.push(JSON.parse(JSON.stringify(park_entry)));
    }
    booking.value.price = booking.value.price - booking.value.entryFees.entry_fee;
    updateParkEntryPrices();
    booking.value.price = booking.value.price + booking.value.entryFees.entry_fee;
    booking_price.value = booking.value.price;

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
    booking_price.value = booking.value.price;
}
const initBooking = function (data) {
    booking.value = data;
    booking.value.arrival = Moment(booking.value.arrival).format('DD/MM/YYYY');
    booking.value.departure = Moment(booking.value.departure).format('DD/MM/YYYY');
    // set the campsite
    selected_campsites.value = booking.value.campsites;
    // Update dates
    selected_arrival.value = booking.value.arrival;
    selected_departure.value = booking.value.departure;
    // set the campground
    campground.value = booking.value.campground ? campgrounds.value.find(c => parseInt(c.id) === parseInt(booking.value.campground)) : null;
    // fetch park details
    fetchPark();
    // fetch the sites
    fetchSites();
    // Update guests
    let guests = booking.value.guests;
    Object.keys(guests).forEach((key) => {
        guestsPicker.map((p) => {
            if (p.id == key) {
                p.amount = guests[key];
            }
            return p;
        })
    });
    generateGuestCountText();
    // Update Vehicles
    booking.value.parkEntry = { 'vehicles': 0 };
    booking.value.entryFees = {
        vehicle: 0,
        motorbike: 0,
        concession: 0,
        entry_fee: 0,
        regos: []
    };
    $.each(booking.value.regos, (i, v) => {
        parkEntryPicker.map((vp) => {
            if (vp.id == v.type) {
                vp.rego = v.rego;
                vp.entry_fee = v.entry_fee;
                addVehicleCount(vp)
            }
            vp.rego = '';
            vp.entry_fee = false;
            return vp;
        });
    })

    nextTick(() => {
        addEventListeners();
    });
    setTimeout(function () {
        generateBookingPrice();
        initialised.value = true;
    }, 2000);

}


onMounted(function () {
    bookingForm.value = document.bookingForm.value;
    initSelectTwo();
    //addEventListeners();
    //vm.addFormValidations();
})

const onBeforeRouteEnters = () => {
    store.commit('SET_LOADER_STATE', true);
    store.commit('SET_LOADER_TEXT', 'Loading Booking');
    let initialisers = [
        store.dispatch('fetchCampgrounds'),
        booking_helpers.fetchBooking(to.params.booking_id)
    ]
    Promise.all(initialisers).then((responses) => {
        store.commit('SET_LOADER_STATE', false);
        next(vm => {
            initBooking(responses[1]);
        });
    }).catch(err => {
        console.log(err);
    });
}

onBeforeRouteEnters()

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
