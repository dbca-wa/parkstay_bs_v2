<template html>
    <div v-cloak class="f6inject">
        <div class="row">
            <div class="small-12 medium-3 large-6 columns search-params">
                <button id='map-reload' type="button" class="button formButton" v-on:click="reloadMap"
                    style='display:none'>MAP RELOAD</button>
            </div>
        </div>



        <div id='card-preview' style='display:none'>

            <div v-if="camping_distance_array && camping_distance_array.length > 0">
                <SearchCarousel :camping_distance_array="camping_distance_array" :parkstayUrl="parkstayUrl"
                    :booking_arrival_days="booking_arrival_days"
                    :permission_to_make_advanced_booking="permission_to_make_advanced_booking"
                    :campgroundSiteTotal="campgroundSiteTotal" :campgroundAvailablity="campgroundAvailablity"
                    :bookingParam="bookingParam" />


            </div>
        </div>



        <div id='map-preview' style='display:none'>
            <div class="loading-map" style='display:none'>
                <div
                    class="spinner-border text-primary"
                    style="width: 6rem; height: 6rem"
                    role="status"
                >
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
            <div class="row map-container">
                <div class="small-12 medium-12 large-12 columns search-params" style='display:none'>
                    <div class="row">
                        <div class="small-12 columns">
                            <label>Search <input class="input-group-field" id="searchInput" type="text"
                                    placeholder="Search for campgrounds, parks, addresses..." /></label>
                        </div>
                    </div>

                    <div class="row">
                        <div class="small-12 medium-12 large-4 columns">
                            <label>Arrival <input id="dateArrival" name="arrival" type="text" placeholder="dd/mm/yyyy"
                                    vonchange="updateDates" /></label>
                        </div>
                        <div class="small-12 medium-12 large-4 columns">
                            <label>Departure <input id="dateDeparture" name="departure" type="text"
                                    placeholder="dd/mm/yyyy" vonchange="updateDates" /></label>
                        </div>
                        <div class="small-12 medium-12 large-4 columns">
                            <label>
                                Guests <input type="button" class="button formButton" v-bind:value="numPeople"
                                    data-toggle="guests-dropdown" />
                            </label>
                            <div class="dropdown-pane" id="guests-dropdown" data-dropdown data-auto-focus="true">
                                <div class="row">
                                    <div class="small-6 columns">
                                        <label for="num_adults" class="text-right">Adults (non-concessions)</label>
                                    </div>
                                    <div class="small-6 columns">
                                        <label> <input type="number" id="numAdults" name="num_adults"
                                                v-model.number="numAdults" min="0" max="16" /></label>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="small-6 columns">
                                        <!-- <a class="button" v-bind:href="f.info_url" target="_self">More info</a> -->
                                        <label for="num_concessions" class="text-right"><span class="has-tip" title="Holders of one of the following Australian-issued cards:
- Seniors Card
- Age Pension
- Disability Support
- Carer Payment
- Carer Allowance
- Companion Card
- Department of Veterans' Affairs">Concessions</span></label>
                                    </div>
                                    <div class="small-6 columns">
                                        <label> <input type="number" id="numConcessions" name="num_concessions"
                                                v-model.number="numConcessions" min="0" max="16" /></label>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="small-6 columns">
                                        <label for="num_children" class="text-right">Children (ages 6-15)</label>
                                    </div>
                                    <div class="small-6 columns">
                                        <label> <input type="number" id="numChildren" name="num_children"
                                                v-model.number="numChildren" min="0" max="16" /></label>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="small-6 columns">
                                        <label for="num_infants" class="text-right">Infants (ages 0-5)</label>
                                    </div>
                                    <div class="small-6 columns">
                                        <label> <input type="number" id="numInfants" name="num_infants"
                                                v-model.number="numInfants" min="0" max="16" /></label>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="small-12 medium-12 large-12 columns">
                            <label><input type="checkbox" v-model="bookableOnly" /> Show bookable campsites only</label>
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-12 columns">
                            <hr />
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-12 medium-12 large-12 columns">
                            <label>Select equipment</label>
                        </div>
                        <div class="small-12 medium-12 large-4 columns">
                            <label><input type="radio" name="gear_type" value="all" v-model="gearType"
                                    class="show-for-sr" v-on:change="reload()" /><i class="symb RC3"></i> All
                                types</label>
                        </div>
                        <div class="small-12 medium-12 large-4 columns">
                            <label><input type="radio" name="gear_type" value="tent" v-model="gearType"
                                    class="show-for-sr" v-on:change="reload()" /><i class="symb RC2"></i> Tent</label>
                        </div>
                        <div class="small-12 medium-12 large-4 columns">
                            <label><input type="radio" name="gear_type" value="campervan" v-model="gearType"
                                    class="show-for-sr" v-on:change="reload()" /><i class="symb RV10"></i>
                                Campervan</label>
                        </div>
                        <div class="small-12 medium-12 large-5 columns">
                            <label><input type="radio" name="gear_type" value="caravan" v-model="gearType"
                                    class="show-for-sr" v-on:change="reload()" /><i class="symb RC4"></i> Caravan /
                                Camper trailer</label>
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-12 columns">
                            <hr class="search" />
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-12 medium-12 large-12 columns">
                            <label>Select features</label>
                        </div>
                        <template v-for="filt in filterList">
                            <div class="small-12 medium-12 large-4 columns">
                                <label><input type="checkbox" class="show-for-sr" :value="'filt_' + filt.key"
                                        v-model="filterParams[filt.key]" v-on:change="updateFilter()" /> <i class="symb"
                                        :class="filt.symb"></i> {{ filt.name }}</label>
                            </div>
                        </template>
                        <template v-for="filt in extraFilterList">
                            <div class="small-12 medium-12 large-4 columns"
                                v-bind:class="{ 'filter-hide': hideExtraFilters }">
                                <label><input type="checkbox" class="show-for-sr" :value="'filt_' + filt.key"
                                        v-model="filterParams[filt.key]" v-on:change="updateFilter()" /> <i class="symb"
                                        :class="filt.symb"></i> {{ filt.name }}</label>
                            </div>
                        </template>
                    </div>
                    <div class="row">
                        <div class="small-12 medium-12 large-4 columns"
                            v-bind:class="{ 'filter-hide': hideExtraFilters }">
                            <label><input type="checkbox" v-model="sitesOnline" v-on:change="updateFilter()" /><img
                                    v-bind:src="sitesOnlineIcon" width="24" height="24" /> Online bookings</label>
                        </div>
                        <div class="small-12 medium-12 large-4 columns"
                            v-bind:class="{ 'filter-hide': hideExtraFilters }">
                            <label><input type="checkbox" v-model="sitesInPerson" v-on:change="updateFilter()" /><img
                                    v-bind:src="sitesInPersonIcon" width="24" height="24" /> No online bookings</label>
                        </div>
                        <div class="small-12 medium-12 large-4 columns"
                            v-bind:class="{ 'filter-hide': hideExtraFilters }">
                            <label><input type="checkbox" v-model="sitesAlt" v-on:change="updateFilter()" /><img
                                    v-bind:src="sitesAltIcon" width="24" height="24" /> Third-party site</label>
                        </div>
                        <div class="small-12 medium-12 large-12 columns filter-button">
                            <button class="button expanded" v-on:click="toggleShowFilters"><span
                                    v-if="hideExtraFilters">Show
                                    more filters ▼</span><span v-else>Hide filters ▲</span></button>
                        </div>
                    </div>
                </div>
                <div class="small-12 medium-12 large-12 columns">
                    <div id="map"></div>
                    <div id="mapPopup" class="mapPopup" v-cloak>
                        <a href="#" id="mapPopupClose" class="mapPopupClose"></a>
                        <div id="mapPopupContent">
                            <h4 style="margin: 0"><b id="mapPopupName"></b></h4>
                            <p><i id="mapPopupPrice"></i></p>
                            <img class="thumbnail" id="mapPopupImage" />
                            <div id="mapPopupDescription" style="font-size: .9rem;" />
                            <a id="mapPopupButton" class="button" style="margin-bottom: 0; margin-top: 1em;"
                                target="_self">See availability</a>
                        </div>
                    </div>
                </div>
            </div>

        </div>

        <!-- End of hide-->
    </div>
</template>



<script>
import 'foundation-sites/dist/js/foundation.min';
// import 'foundation-datepicker/js/foundation-datepicker';
import debounce from 'debounce';
import moment from 'moment';
import SearchCarousel from './searchCarousel/SearchCarousel.vue';
import sitesOnlineIcon from '@assets/pin.svg';
import sitesOnlineNotAvailIcon from '@assets/pin_red.svg';
import sitesNoMatchIcon from '@assets/pin_grey.svg';
import sitesInPersonIcon from '@assets/pin_offline.svg';
import sitesAltIcon from '@assets/pin_alt.svg';
import locationIcon from '@assets/location.svg';
import map_init_mount from '../utils/map_init_mount';
var today = moment.utc().add(8, 'hours');
today = moment.utc({ year: today.year(), month: today.month(), day: today.date(), hour: 0, minute: 0, millisecond: 0 })

export default {
    name: 'parkfinder',
    components: { SearchCarousel },
    
    data: function () {
        return {
            parkstayUrl: (import.meta.env.VITE_PARKSTAY_URL  || (typeof global != 'undefined'? global : {})?.parkstayUrl) || "",
            defaultCenter: [13775786.985667605, -2871569.067879858], // [123.75, -24.966],
            defaultLayers: [
                ['dpaw:mapbox_outdoors', {}],
                ['cddp:dpaw_tenure', {}],
            ],
            filterList: [
                { name: '2WD accessible', symb: 'RV2', key: 'twowheel', 'remoteKey': ['2WD/SUV ACCESS'] },
                { name: 'Campfires allowed', symb: 'RF10', key: 'campfire', 'remoteKey': ['FIREPIT'] },
                { name: 'Dogs allowed', symb: 'RG2', key: 'dogs', 'remoteKey': ['DOGS'] }
            ],
            extraFilterList: [
                { name: 'BBQ', symb: 'RF8G', key: 'bbq', 'remoteKey': ['BBQ'] },
                { name: 'Dish washing', symb: 'RF17', key: 'dishwashing', 'remoteKey': ['DISHWASHING'] },
                { name: 'Dump station', symb: 'RF19', key: 'sullage', 'remoteKey': ['DUMP STATION'] },
                { name: 'Generators allowed', symb: 'RG15', key: 'generators', 'remoteKey': ['GENERATORS PERMITTED'] },
                { name: 'Mains water', symb: 'RF13', key: 'water', 'remoteKey': ['MAINS WATER'] },
                { name: 'Picnic tables', symb: 'RF6', key: 'picnic', 'remoteKey': ['PICNIC TABLE'] },
                //{name: 'Sheltered picnic tables', symb: 'RF7', key: 'picnicsheltered', 'remoteKey': ['TABLE - SHELTERED']},
                { name: 'Showers', symb: 'RF15', key: 'showers', 'remoteKey': ['SHOWER'] },
                { name: 'Toilets', symb: 'RF1', key: 'toilets', 'remoteKey': ['TOILETS'] },
                //{name: 'Walk trail', symb: 'RW3', key: 'walktrail', 'remoteKey': ['WALK TRAIL']},
                { name: 'Powered sites', symb: 'MAINS', key: 'walktrail', 'remoteKey': ['POWERED SITES'] },
            ],
            hideExtraFilters: true,
            suggestions: {},
            extentFeatures: [],
            //Added to store values of api date
            currentDate: null,
            arrivalDate: null,
            departureDate: null,
            numAdults: 2,
            numConcessions: 0,
            numChildren: 0,
            numInfants: 0,
            gearType: 'all',
            features: [],
            featuresCs: [],
            camping_distance_array: [],
            campground_data: [],
            filterParams: {
            },
            campgroundAvailablity: {},
            campgroundSiteTotal: {},
            dateSetFirstTime: true,
            sitesOnline: true,
            sitesInPerson: true,
            sitesAlt: true,
            sitesOnlineIcon: sitesOnlineIcon,
            sitesNoMatchIcon: sitesNoMatchIcon,
            sitesOnlineNotAvailIcon: sitesOnlineNotAvailIcon,
            sitesInPersonIcon: sitesInPersonIcon,
            sitesAltIcon: sitesAltIcon,
            locationIcon: locationIcon,
            selectedFeature: null,
            booking_arrival_days: 0,
            screen_width: 0,
            permission_to_make_advanced_booking: false,
            groundsFilter: [],
            _updateViewport: undefined
        }
    },
    computed: {
        bookableOnly: {
            cache: false,
            get: function () {
                return this.sitesOnline && (!this.sitesInPerson) && (!this.sitesAlt);
            },
            set: function (val) {
                this.sitesOnline = true;
                this.sitesInPerson = !val;
                this.sitesAlt = !val;
                this.reload();
            }
        },
        extent: {
            cache: false,
            get: function () {
                return this.olmap.getView().calculateExtent(this.olmap.getSize());
            }
        },
        center: {
            cache: false,
            get: function () {
                return this.olmap.getView().getCenter();
            }
        },

        numPeople: {
            cache: false,
            get: function () {
                // annoying wrapper to deal with vue.js' weak number casting
                var count = (this.numAdults ? this.numAdults : 0) +
                    (this.numConcessions ? this.numConcessions : 0) +
                    (this.numChildren ? this.numChildren : 0) +
                    (this.numInfants ? this.numInfants : 0);
                if (count === 1) {
                    return `${count} person ▼`;
                } else {
                    return `${count} people ▼`;
                }
            }
        },
        bookingParam: {
            cache: false,
            get: function () {
                var params = {
                    'num_adult': this.numAdults,
                    'num_concession': this.numConcessions,
                    'num_children': this.numChildren,
                    'num_infants': this.numInfants,
                    'gear_type': this.gearType,
                    'arrival': this.arrivalDate ?? "",
                    'departure': this.departureDate ?? ""
                };
                return $.param(params);
            }
        },
    },
    methods: {
        toggleShowFilters: function () {
            this.hideExtraFilters = !this.hideExtraFilters;
        },
        search: function (place) {
            if (!place) {
                return;
            }
            var vm = this;
            // search through the autocomplete list first
            var target = this.suggestions['features'].find(function (el) {
                return el['properties']['name'] == place;
            });
            if (target) {                
                var view = this.olmap.getView();
                // zoom slightly closer in for campgrounds
                var resolution = vm.resolutions[10];
                if (target['properties']['type'] == 'Campground') {
                    resolution = vm.resolutions[12];
                }
                // pan to the spot, zoom slightly closer in for campgrounds
                view.animate({
                    center: vm.ol.proj.fromLonLat(target['coordinates']),
                    resolution: resolution,
                    duration: 1000
                });

                return;
            }

            // no match, forward on to mapbox geocode query
            var center = vm.ol.proj.toLonLat(vm.center);
            $.ajax({
                url: 'https://mapbox.dpaw.wa.gov.au/geocoding/v5/mapbox.places/' + encodeURIComponent(place) + '.json?' + $.param({
                    country: 'au',
                    proximity: '' + center[0] + ',' + center[1],
                    bbox: '112.920934,-35.191991,129.0019283,-11.9662455',
                    types: 'region,postcode,place,locality,neighborhood,address'
                }),
                dataType: 'json',
                success: function (data, status, xhr) {
                    if (data.features && data.features.length > 0) {
                        var view = vm.olmap.getView();
                        view.animate({
                            center: vm.ol.proj.fromLonLat(data.features[0].geometry.coordinates),
                            resolution: vm.resolutions[12],
                            duration: 1000
                        });

                    }
                }
            })

        },
        refreshPopup: function () {
            let vm = this;
            let feature = vm.selectedFeature;
            if (feature != null) {
                vm.popup.setPosition(feature.getGeometry().getCoordinates());
                // really want to make vue.js render this, except reactivity dies
                // when you pass control of the popup element to OpenLayers :(
                $("#mapPopupName")[0].innerHTML = feature.get('name');
                if (feature.get('images')) {
                    $("#mapPopupImage").attr('src', vm.parkstayUrl + '/campground-image/146/248/?mediafile=' + feature.get('images')[0].image);
                    $("#mapPopupImage").show();
                } else {
                    $("#mapPopupImage").hide();
                }
                if (feature.get('price_hint') && Number(feature.get('price_hint'))) {
                    $("#mapPopupPrice")[0].innerHTML = '<small>From $' + feature.get('price_hint') + ' per night</small>';
                } else {
                    $("#mapPopupPrice")[0].innerHTML = '';
                }
                $("#mapPopupDescription")[0].innerHTML = feature.get('description');

                // Need to change this portion for the new button
                // if/else used to diffrentiate campground type(if covers type 0 and 1), differentiated by API
                if (feature.get('campground_type') == 0) {
                    $("#mapPopupBook").show();
                    $("#mapPopupInfo").hide();
                    $("#mapPopupBook").attr('href', vm.parkstayUrl + '/search-availability/campground/site_id=' + feature.getId() + '&' + vm.bookingParam);
                } else if (feature.get('campground_type') == 1) {
                    $("#mapPopupBook").hide();
                    $("#mapPopupInfo").show();
                    $("#mapPopupInfo").attr('href', feature.get('info_url'));
                } else {
                    $("#mapPopupBook").hide();
                    $("#mapPopupInfo").show();
                    $("#mapPopupInfo").attr('href', feature.get('info_url'));
                    $("#mapPopupInfo").attr('href', vm.parkstayUrl + '/search-availability/campground/site_id=' + feature.getId());
                }
            }
        },
        groundFilter: function (feature) {
            return true;
        },
        removeCampsiteFromAvailable: function (campground_id, campsite_id) {
            var vm = this;
            if (vm.campgroundSiteTotal[campground_id]['sites'].indexOf(campsite_id) >= 0) {
                var cst = vm.campgroundSiteTotal[campground_id]['sites'].indexOf(campsite_id);
                if (cst >= 0) {
                    vm.campgroundSiteTotal[campground_id]['sites'].splice(cst, 1);
                }
            }

        },
        reloadMap: function () {
            console.log('RELOAD MAP');
            this.booking_arrival_days = window.search_avail.var.arrival_days;
            this.arrivalDate = $('#checkin').val();
            this.departureDate = $('#checkout').val();
            this.permission_to_make_advanced_booking = window.search_avail.var.permission_to_make_advanced_booking;

            var vm = this;
            this.updateDates();
            this.olmap.updateSize();
            var coord_1 = $('#coord_1').val();
            var coord_2 = $('#coord_2').val();
            var zoom_level = $('#zoom_level').val();
            var coord = [];
            coord[0] = parseFloat(coord_1);
            coord[1] = parseFloat(coord_2);
            let fromLonLat = vm.ol.proj.fromLonLat(coord);
            var view = this.olmap.getView();
            // zoom slightly closer in for campgrounds
            var resolution = vm.resolutions[10];
            if (zoom_level > 0) {
                var resolution = vm.resolutions[zoom_level];
            }

            // pan to the spot, zoom slightly closer in for campgrounds
            if (vm.selectedFeature) {
                fromLonLat = vm.selectedFeature.getGeometry().getCoordinates()
            }
            
            // search_avail.focus_map()
            view.animate({
                center: fromLonLat,
                resolution: resolution,
                duration: 1000
            });
        },
        buildDistanceArray: function () {
            console.log("running buildDistanceArray");
            var vm = this;
            var coord_1 = $('#coord_1').val();
            var coord_2 = $('#coord_2').val();
            vm.camping_distance_array = [];

            var tents = $('#filter-checkbox-tent').is(':checked');
            var campervan = $('#filter-checkbox-campervan').is(':checked');
            var campertrailer = $('#filter-checkbox-campertrailer').is(':checked');

            var legit = new Set();
            var featurescs = new Set();
            $("#search-filters").find("input").each(function () {
                if (this.id.substring(0, 15) == 'filter-feature-') {
                    var filter_element_id = this.id;
                    var feature_id = this.id.substring(15);
                    var is_checked = $("#" + filter_element_id).is(':checked');
                    if (is_checked == true) {
                        legit.add(parseInt(feature_id));
                    }
                }
            });


            vm.featuresCs = [];
            $("#search-filters").find("input").each(function () {
                if (this.id.substring(0, 17) == 'filter-featurecs-') {
                    var filter_element_id = this.id;
                    var feature_id = this.id.substring(17);
                    var is_checked = $("#" + filter_element_id).is(':checked');
                    if (is_checked == true) {
                        vm.featuresCs.push(feature_id);
                        featurescs.add(parseInt(feature_id));
                    }
                }
            });
            this.campground_data.forEach(function (el) {
                var skip_cg = false;
                var geo = el.geometry.coordinates;
                var campground_id = el.id;
                var campground_name = el.properties.name;
                var campground_type = el.properties.campground_type;
                var max_advance_booking = el.properties.max_advance_booking;
                var campsite_features = el.properties.features;
                var description = el.properties.description;
                var images = el.properties.images;
                var price_hint = el.properties.price_hint;
                var campsites = el.properties.campsites;
                var campsites_total = el.properties.campsites.length;
                var info_url = el.properties.info_url;
                var park_name = '';
                if (el.properties.park) {
                    park_name = el.properties.park.name
                }
                vm.campgroundSiteTotal[campground_id] = { 'sites': {}, 'total_available': 0 }
                vm.campgroundSiteTotal[campground_id]['sites'] = JSON.parse(JSON.stringify(vm.campgroundAvailablity[campground_id]['sites']));

                // Tier 1 Filter Start
                var cs_tent = false;
                var cs_campervan = false;
                var cs_caravan = false;
                var cs_features = false;

                if (campsites.length > 0) {
                } else {
                    cs_features = true;
                }

                var hascsfeatcount = 0;
                for (var cs of campsites) {
                    // Start Complete campground site filter
                    var remove_campsite = false;
                    if (cs.tent == true) {
                        // because there is more than one site,  if more more than one site supports tents then set true.
                        cs_tent = true;
                    }

                    if (cs.campervan == true) {
                        cs_campervan = true;
                    }

                    if (cs.caravan == true) {
                        cs_caravan = true;
                    }

                    // End completed campground site filter
                    if (tents == true) {
                        if (cs.tent == true) {
                        } else {
                            remove_campsite = true;
                        }
                    }
                    if (campervan == true) {
                        if (cs.campervan == true) {
                        } else {
                            remove_campsite = true;
                        }
                    }

                    if (campertrailer == true) {
                        if (cs.caravan == true) {
                        } else {
                            remove_campsite = true;
                        }
                    }

                    var hascsfeat = 0;
                    var feats = new Set(cs['features'].map(function (x) {
                        return x.id;
                    }));
                    for (var x of featurescs) {
                        if (feats.has(x)) {
                            hascsfeat = hascsfeat + 1;
                        }
                    }

                    if (hascsfeat == featurescs.size) {
                        hascsfeatcount = hascsfeatcount + 1;
                    } else {
                        remove_campsite = true;
                    }
                    if (remove_campsite == true) {
                        vm.removeCampsiteFromAvailable(campground_id, cs.id);
                    }
                }

                // START Remove CG
                if (hascsfeatcount == 0) {
                    cs_features = true;
                }
                if (featurescs.size > 0) {
                    if (cs_features == true) {
                        skip_cg = true;
                    }
                }
                // END Remove CG

                if (tents == true && cs_tent == false) {
                    skip_cg = true;
                }

                if (campervan == true && cs_campervan == false) {
                    skip_cg = true;
                }

                if (campertrailer == true && cs_caravan == false) {
                    skip_cg = true;
                }

                // Tier 1 Filter End
                var feats = new Set(campsite_features.map(function (x) {
                    return x.id;
                }));

                for (var x of legit) {
                    if (!feats.has(x)) {
                        // console.log("Skipping Campsite");
                        skip_cg = true;
                    }
                }

                var row = { 'id': null, 'campground_name': '', 'distance': null, 'description': null, 'price_hint': '', 'images': [], 'campground_type': null, 'available_campsites': 0, 'info_url': null, 'park_name': park_name };

                row['description'] = description;
                row['images'] = images;
                row['price_hint'] = price_hint;
                row['campground_type'] = campground_type;
                row['max_advance_booking'] = max_advance_booking;
                row['id'] = campground_id;
                var distance_km = vm.distance_between_gps(coord_1, coord_2, geo[0], geo[1], "K");

                row['distance'] = distance_km.toFixed(2);
                row['distance_short'] = distance_km.toFixed(0);

                row['available_campsites'] = campsites_total;
                row['info_url'] = info_url;
                row['park_name'] = park_name;

                row['campground_name'] = campground_name;
                row['filters_match'] = skip_cg === false;
                if (campground_name) {
                    vm.camping_distance_array.push(row);
                }

                vm.campgroundSiteTotal[campground_id]['total_available'] = vm.campgroundSiteTotal[campground_id]['sites'].length;
                var row = { 'campground_name': 'test', 'distance': null };
            });
            vm.camping_distance_array.sort(function (a, b) {
                return a.distance - b.distance;
            });
        },
        distance_between_gps: function (lon1, lat1, lon2, lat2, unit) {
            if ((lat1 == lat2) && (lon1 == lon2)) {
                return 0;
            }
            else {
                var radlat1 = Math.PI * lat1 / 180;
                var radlat2 = Math.PI * lat2 / 180;
                var theta = lon1 - lon2;
                var radtheta = Math.PI * theta / 180;
                var dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
                if (dist > 1) {
                    dist = 1;
                }
                dist = Math.acos(dist);
                dist = dist * 180 / Math.PI;
                dist = dist * 60 * 1.1515;
                if (unit == "K") { dist = dist * 1.609344 }
                if (unit == "N") { dist = dist * 0.8684 }
                return dist;
            }
        },
        updateViewport: function (runNow) {
            var vm = this;
            var updateViewportFunc = function () {
                // this object is going to be hammered by vue.js introspection, strip openlayers stuff
                vm.extentFeatures = vm.groundsSource.getFeaturesInExtent(vm.extent).filter(vm.groundFilter).map(function (el) {
                    var props = el.getProperties();
                    props.style = undefined;
                    props.geometry = props.geometry.getCoordinates();
                    props.distance = Math.sqrt(Math.pow(props.geometry[0] - vm.center[0], 2) + Math.pow(props.geometry[1] - vm.center[1], 2));
                    props.id = el.getId();
                    return props;
                }).sort(function (a, b) {
                    /* distance from map center sort */
                    if (a.distance < b.distance) {
                        return -1;
                    }
                    if (a.distance > b.distance) {
                        return 1;
                    }
                    return 0;

                    /* alphabet sort
                    var nameA = a.name.toUpperCase();
                    var nameB = b.name.toUpperCase();
                    if (nameA < nameB) {
                        return -1;
                    }
                    if (nameA > nameB) {
                        return 1;
                    }
                    return 0; */
                });

            };
            if (runNow) {
                updateViewportFunc();
            } else {
                if (!vm._updateViewport) {
                    vm._updateViewport = debounce(function () {
                        updateViewportFunc();
                    }, 100);
                }
                vm._updateViewport();
            }
            // console.log('Activating Glider');
            // Glider(document.querySelector('.glider')).refresh();
            //new Glider(document.querySelector('.glider'), {  slidesToShow: 5,
            //  slidesToScroll: 5,
            //  draggable: true,
            //  dots: '.dots',
            //  arrows: {
            //    prev: '.glider-prev',
            //    next: '.glider-next'
            //  }
            //});

        },
        updateDates: function (ev) {
            // for the first time someone changes the dates, enable the
            // "Show bookable campsites only" flag
            if (this.dateSetFirstTime) {
                this.dateSetFirstTime = false;
                this.bookableOnly = true;
            }
            this.reload();
        },
        reload: debounce(function () {
            this.groundsSource.loadSource();
            this.refreshPopup();
        }, 250),

        // TODO Added these methods to use server date extracted from an api call
        // Needs to be implemented in the system, have to use server date to restrict arrival date instead of today
        // Currently this function is not used
        setDate: function (datestring) {
            let vm = this;
            var tempDate = new Date(datestring)
            vm.currentDate = moment({ year: tempDate.getFullYear(), month: tempDate.getMonth(), day: tempDate.getDate(), hour: 0, minute: 0, second: 0, millisecond: 0 });
        },

        fetchServerDate: function () {
            let vm = this;
            vm.$http.get(vm.parkstayUrl + '/api/server-date').then(function (response) {
                this.setDate(response.body)
            })
        },

        // End of change
        updateFilter: function () {
            console.log("Running updateFilter");
            var vm = this;
            // make a lookup table of campground features to filter on
            var legit = new Set();
            var featurescs = new Set();

            var filterCb = function (el) {
                //legit.add(el);
                if (vm.filterParams[el.key] === true) {
                    el.remoteKey.forEach(function (fl) {
                        // legit.add(fl);
                    });
                }
            };
            // this.filterList.forEach(filterCb);
            // this.extraFilterList.forEach(filterCb);
            vm.features = [];
            $("#search-filters").find("input").each(function () {
                if (this.id.substring(0, 15) == 'filter-feature-') {
                    var filter_element_id = this.id;
                    var feature_id = this.id.substring(15);
                    var is_checked = $("#" + filter_element_id).is(':checked');
                    if (is_checked == true) {
                        vm.features.push(feature_id);
                        legit.add(parseInt(feature_id));
                    }
                }
            });

            vm.featuresCs = [];
            $("#search-filters").find("input").each(function () {
                if (this.id.substring(0, 17) == 'filter-featurecs-') {
                    var filter_element_id = this.id;
                    var feature_id = this.id.substring(17);
                    var is_checked = $("#" + filter_element_id).is(':checked');
                    if (is_checked == true) {
                        vm.featuresCs.push(feature_id);
                        featurescs.add(parseInt(feature_id));
                    }
                }
            });

            this.groundsFilter.clear();
            this.groundsData.forEach(function (el) {
                var campgroundType = el.get('campground_type');
                var campground_id = el.getId();

                const tents = $('#filter-checkbox-tent').is(':checked');
                const campervan = $('#filter-checkbox-campervan').is(':checked');
                const campertrailer = $('#filter-checkbox-campertrailer').is(':checked');
                const filtersOn = tents || campervan || campertrailer || featurescs.size > 0 || legit.size > 0
               
                el.set('match', true)
                let campsites = el.get('campsites');
                let cs_tent = false;
                let cs_campervan = false;
                let cs_caravan = false;
                let cs_features = false;

                for (let cs of campsites) {
                    // because there is more than one site,  if more more than one site supports tents then set true.
                    if (cs.tent == true) cs_tent = true;
                    if (cs.campervan == true) cs_campervan = true;
                    if (cs.caravan == true) cs_caravan = true;
                    if (cs['features'].length > 0) {
                        for (var x of featurescs) {
                            for (var c of cs['features']) {
                                if (c.id == x) {
                                    cs_features = true;
                                }
                            }
                        }
                    }
                }

                if ((!cs_features && featurescs.size > 0) ||
                    (tents == true && !cs_tent) ||
                    (campervan == true && !cs_campervan) ||
                    (campertrailer == true && !cs_caravan)) {
                    if (filtersOn) el.set('match', false)
                }

                el.set('available', vm.groundsIds.has(el.getId()))
                if (legit.size) { // if we have a feature filter list
                    // check that all parameters are present
                    var feats = new Set(el.get('features').map(function (x) {
                        return x.id;
                    }));
                    for (var x of legit) {
                        if (!feats.has(x)) {
                            if (filtersOn) el.set('match', false)
                        }
                    }
                } 
               
                // always insert cg in results.
                vm.groundsFilter.push(el);
            });
        },
        load_site_queue: function () {
            console.log("load_site_queue");
            var vm = this;
            if (window.sitequeuemanager) {
                console.log("Site Queue Loaded");
                // jQuery is loaded
            } else {
                var waiting_queue_enabled = $('#waiting_queue_enabled').val();
                if (waiting_queue_enabled == 'True') {
                    var scriptTag = document.createElement('script');
                    scriptTag.src = vm.parkstayUrl + '/static/js/django_queue_manager/site-queue-manager.js';
                    document.head.appendChild(scriptTag);
                    setTimeout(function () { if (window.sitequeuemanager) { sitequeuemanager.init(); } vm.load_site_queue(); }, 200);
                    console.log("Deploying Waiting Queue");
                }
            }
        },
        init_mounted: function () {
            map_init_mount(this)
        },
    },
    mounted: function () {
        console.log("LOAD MOUNTED START");
        this.init_mounted();
        console.log("LOAD MOUNTED END");
        this.screen_width = $(window).width();
    }
};
</script>
<style lang="scss">
[v-cloak] {
    display: none;
}

@font-face {
    font-family: "DPaWSymbols";
    src: url("@assets/campicon.woff") format("woff");
}

.symb {
    font-family: "DPaWSymbols";
    font-style: normal;
    font-size: 1.5rem;
}

.symb.RC2:before {
    content: "a";
}

.symb.RC4:before {
    content: "b";
}

.symb.RV10:before {
    content: "c";
}

.symb.RG2:before {
    content: "d";
}

.symb.RG15:before {
    content: "e";
}

.symb.RV2:before {
    content: "f";
}

.symb.RF10:before {
    content: "g";
}

.symb.RF13:before {
    content: "h";
}

.symb.RF15:before {
    content: "i";
}

.symb.RF17:before {
    content: "j";
}

.symb.RF1:before {
    content: "k";
}

.symb.RF6:before {
    content: "l";
}

.symb.RF7:before {
    content: "m";
}

.symb.RF19:before {
    content: "n";
}

.symb.RF8G:before {
    content: "o";
}

.symb.RC1:before {
    content: "p";
}

.symb.RC3:before {
    content: "q";
}

.symb.LOC:before {
    content: "r";
}

.symb.RW3:before {
    content: "s";
}

.symb.MAINS:before {
    content: "t";
}

.f6inject {

    .search-params hr {
        margin: 0;
    }

    .search-params label {
        cursor: pointer;
        font-size: 0.8em;
    }

    /* filter hiding on small screens */
    @media print,
    screen and (max-width: 63.9375em) {
        .filter-hide {
            display: none;
        }
    }

    @media print,
    screen and (min-width: 64em) {
        .filter-button {
            display: none;
        }
    }

    #map {
        height: 75vh;

        .ol-control {
            background-color: rgba(255, 255, 255, 0.4);
            padding: 2px;

            button.ol-zoom-in,
            button.ol-zoom-out {
                border-radius: 2px 2px 0 0;
                height: 2em !important;
                width: 2em !important;
            }
        }

        .ol-control button {
            display: block;
            margin: 1px;
            padding: 0;
            color: white;
            font-size: 1.14em;
            font-weight: bold;
            text-decoration: none;
            text-align: center;
            line-height: .4em;
            background-color: rgba(0, 60, 136, 0.5);
            border: none;
            border-radius: 2px;
        }

        .ol-scale-line {
            background: rgba(0, 60, 136, 0.3);
            border-radius: 4px;
            bottom: 8px;
            left: 8px;
            padding: 2px;
            position: absolute;
        }

        .ol-scale-line-inner {
            border: 1px solid #eee;
            color: #eee;
            border-top: none;
            font-size: 10px;
            text-align: center;
            margin: 1px;
            will-change: contents, width;
        }
    }

    /* set on the #map element when mousing over a feature */
    .click {
        cursor: pointer;
    }

    input+.symb {
        color: #000000;
        transition: color 0.25s ease-out;
    }

    input:checked+.symb {
        color: #2199e8;
    }

    .tooltip {
        position: relative;
        border-radius: 4px;
        background-color: #ffcc33;
        color: black;
        padding: 4px 8px;
        opacity: 0.7;
        white-space: nowrap;
    }

    .tooltip:before {
        border-top: 6px solid rgba(0, 0, 0, 0.5);
        border-right: 6px solid transparent;
        border-left: 6px solid transparent;
        content: "";
        position: absolute;
        bottom: -6px;
        margin-left: -7px;
        left: 50%;
    }

    .mapPopup {
        position: absolute;
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #cccccc;
        bottom: 32px;
        left: -140px;
        width: 280px;
    }

    .mapPopup:after,
    .mapPopup:before {
        top: 100%;
        border: solid transparent;
        content: " ";
        height: 0;
        width: 0;
        position: absolute;
        pointer-events: none;
    }

    .mapPopup:after {
        border-top-color: white;
        border-width: 10px;
        left: 138px;
        margin-left: -10px;
    }

    .mapPopup:before {
        border-top-color: #cccccc;
        border-width: 11px;
        left: 138px;
        margin-left: -11px;
    }

    .mapPopupClose {
        text-decoration: none;
        position: absolute;
        top: 2px;
        right: 8px;
    }

    .mapPopupClose:after {
        content: "✖";
    }
    #mapPopupDescription.popup-notavailable {
        font-size: 12px;
        color: red;
    }

    .searchTitle {
        font-size: 150%;
        font-weight: bold;
    }

    .resultList {
        padding: 0;
    }
}

/* hacks to make awesomeplete play nice with F6 */
div.awesomplete {
    display: block;
}

div.awesomplete>input {
    display: table-cell;
}

#map-preview {
    position: relative;
}
.loading-map {
    font-size: 48px;
    position: absolute;
    z-index: 1;
    right: 44%;
    top: 33%;
}
</style>