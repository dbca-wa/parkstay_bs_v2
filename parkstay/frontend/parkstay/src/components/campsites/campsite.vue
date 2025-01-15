<template lang="html">
    <div id="campsite">
        <pkCsClose ref="closeCampsite" @closeCampsite="showCloseCS()"></pkCsClose>
        <div class="col-lg-12 card p-3">
            <div class="row">
                <form name="campsiteForm" ref="campsiteForm">
                    <div class="panel panel-primary">
                        <div class="panel-heading">
                            <h3 class="panel-title">Campsite Details</h3>
                        </div>
                        <div class="panel-body" v-show="!isLoading">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label class="control-label">Campsite Type</label>
                                        <select class="form-control form-select" v-show="!campsite_classes.length > 0">
                                            <option>Loading...</option>
                                        </select>
                                        <select v-if="campsite_classes.length > 0" @change="onCampsiteClassChange"
                                            name="campsite_class" class="form-control form-select"
                                            v-model="campsite.campsite_class">
                                            <option value=""></option>
                                            <option v-for="campsite_class in campsite_classes"
                                                :value="campsite_class.id">{{ campsite_class.name }}</option>
                                        </select>
                                    </div>
                                </div>
                                <div v-show="showName" class="col-md-6">
                                    <div class="form-group">
                                        <label class="control-label">Campsite Name</label>
                                        <input type="text" name="name" class="form-control" v-model="campsite.name"
                                            required />
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label class="control-label">Minimum Number of People</label>
                                        <input type="number" name="name" class="form-control"
                                            v-model="campsite.min_people" required
                                            :disabled="selected_campsite_class_url() != ''" />
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label class="control-label">Maximum Number of People</label>
                                        <input type="number" name="name" class="form-control"
                                            v-model="campsite.max_people" required
                                            :disabled="selected_campsite_class_url() != ''" />
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <div class="checkbox">
                                            <label><input type="checkbox" v-model="campsite.tent"
                                                    :disabled="selected_campsite_class_url() != ''" />Tent</label>
                                        </div>
                                        <div class="checkbox">
                                            <label><input type="checkbox" v-model="campsite.campervan"
                                                    :disabled="selected_campsite_class_url() != ''" />Campervan</label>
                                        </div>
                                        <div class="checkbox">
                                            <label><input type="checkbox" v-model="campsite.caravan"
                                                    :disabled="selected_campsite_class_url() != ''" />Caravan</label>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-group" v-if="campground.site_type == 0">
                                        <label class="control-label">Maximum Number of Vehicles</label>
                                        <input type="number" name="max_vehicles" class="form-control"
                                            v-model="campsite.max_vehicles" required
                                            :disabled="selected_campsite_class_url() != ''" />
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6">

                                </div>
                                <div class="col-sm-6">
                                    <div class="row">
                                        <div class="form-group">
                                            <div class="col-sm-6 col-xs-8">
                                                <button @click.prevent="addCampsite" type="button"
                                                    v-show="createCampsite"
                                                    class="btn btn-primary btn-create">Create</button>
                                            </div>
                                            <div class="col-sm-2 col-xs-4  pull-right">
                                                <input type="number" v-show="createCampsite" class="form-control"
                                                    name="number" v-model="campsite.number" value="">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row" style="margin-top:10px;">
                                        <div class="col-sm-6 pull-right">
                                            <div class="pull-right">
                                                <button type="button" v-show="!createCampsite" style="margin-right:5px"
                                                    @click="updateCampsite" class="btn btn-primary">Update</button>
                                                <button type="button" class="btn btn-default pull-right"
                                                    @click="goBack">Back</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>
                <loader :isLoading="isLoading">Saving Campsite Data...</loader>
            </div>
            <div style="margin-top:50px;">
                <!--stayHistory v-if="!createCampsite" ref="stay_dt" :object_id="myID" :datatableURL="stayHistoryURL"></stayHistory-->
                <priceHistory v-if="!createCampsite" level="campsite" ref="price_dt" :object_id="myID"
                    :dt_options="ph_options" :showAddBtn="canAddRate"></priceHistory>
                <closureHistory v-if="!createCampsite" ref="cg_closure_dt" :closeCampground=false :object_id="myID"
                    :datatableURL="closureHistoryURL"></closureHistory>
            </div>

        </div>
    </div>
</template>

<script setup>
import {
    $,
    api_endpoints,
    helpers,
    Moment
} from '../../hooks.js';
import pkCsClose from './closureHistory/closeCampsite.vue'
import loader from '../utils/loader.vue'
import closureHistory from '../utils/closureHistory.vue'
import priceHistory from '../utils/priceHistory/priceHistory.vue'
import { computed, onMounted, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter()
const route = useRoute()

const price_dt = ref(null)
const cg_closure_dt = ref(null)
const closeCampsite = ref(null)
const campsiteForm = ref(null)
const campsite_id = ref(null)
const isLoading = ref(false)
const createCampsite = ref(true)
const temp_campsite = ref({})
const campground = ref({})
const campsite = ref({
    number: 1,
    campsite_class: '',
    tent: false,
    description: '',
    campervan: false,
    caravan: false,
    min_people: '',
    max_people: '',
    max_vehicles: ''
})
const campsite_classes = ref([])
const ph_options = ref({
    responsive: true,
    processing: true,
    deferRender: true,
    ajax: {
        url: api_endpoints.campsites_price_history(route.params.id),
        dataSrc: ''
    },
    columnDefs: [
        { "defaultContent": "-", "targets": "_all" },
    ],
    columns: [{
        data: 'date_start',
        mRender: function (data, type, full) {
            return Moment(data).format('DD/MM/YYYY');
        }

    }, {
        data: 'date_end',
        mRender: function (data, type, full) {
            if (data) {
                return Moment(data).add(1, 'day').format('DD/MM/YYYY');
            }
            else {
                return '';
            }
        }

    }, {
        data: 'adult'
    }, {
        data: 'concession'
    }, {
        data: 'child'
    }, {
        data: 'details',
        mRender: function (data, type, full) {
            if (data) {
                return data;
            }
            return '';
        }
    }, {
        data: 'editable',
        mRender: function (data, type, full) {
            if (data && full.update_level == 2) {
                var id = full.id;
                var column = "<td ><a href='#' class='editPrice' data-rate=\"__ID__\" data-bookingpolicyid=\"__BOOKINGPOLICYID__\">Edit</a><br/>"
                if (full.deletable) {
                    column += "<a href='#' class='deletePrice' data-rate=\"__ID__\">Delete</a></td>";
                }
                column = column.replace(/__ID__/g, full.id);
                column = column.replace(/__BOOKINGPOLICYID__/g, full.booking_policy);
                return column
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
const closureHistoryURL = computed(function () {
    return api_endpoints.campsite_status_history(campsite_id.value);
})
const stayHistoryURL = computed(function () {
    return api_endpoints.campsites_stay_history;
})
const myID = computed(function () {
    return parseInt(campsite_id.value);
})
const canAddRate = computed(function () {
    return !!campsite.value.can_add_rate;
})
const showName = computed(function () {
    return (createCampsite.value && campsite.value.number == 1) || !createCampsite.value;
})

const selected_campsite_class_url = function () {
    return (campsite.value.campsite_class != null) ? campsite.value.campsite_class : '';
}
const onCampsiteClassChange = function () {
    if (campsite_classes.value.length > 0) {
        if (selected_campsite_class_url()) {
            var sel_class = campsite_classes.value.find(function (el) {
                return el.url == campsite.value.campsite_class;
            });

            if (sel_class) {
                campsite.value.tent = sel_class.tent;
                campsite.value.caravan = sel_class.caravan;
                campsite.value.campervan = sel_class.campervan;
                campsite.value.max_people = sel_class.max_people;
                campsite.value.min_people = sel_class.min_people;
                campsite.value.description = sel_class.description;
                campsite.value.max_vehicles = sel_class.max_vehicles;
                // $refs.descriptionEditor.updateContent(campsite.value.description);
            }

        } else {
        }

        /*

        if(selected_campsite_class_url()){
            $.ajax({
                url:selected_campsite_class_url(),
                dataType: 'json',
                success:function (sel_class) {
                    campsite.value.tent = sel_class.tent;
                    campsite.value.caravan= sel_class.caravan;
                    campsite.value.campervan= sel_class.campervan;
                    campsite.value.max_people = sel_class.max_people;
                    campsite.value.min_people= sel_class.min_people;
                    campsite.value.description = sel_class.description;
                    $refs.value.descriptionEditor.updateContent(campsite.value.description);
                }

            });
        }else{
            if (!createCampsite.value){
                campsite.value.tent = temp_campsite.value.tent;
                campsite.value.carvan= temp_campsite.value.caravan;
                campsite.value.campervan= temp_campsite.value.campervan;
                campsite.value.max_people = temp_campsite.value.max_people;
                campsite.value.min_people= temp_campsite.value.min_people;
                campsite.value.description = temp_campsite.value.description;
            }
        }*/
    }
}
const showCloseCS = function () {
    const id = campsite.value.id;
    // Update close modal attributes
    closeCampsite.value.id = id;
    closeCampsite.value.isOpen = true;
}
const fetchCampsite = function () {
    $.ajax({
        url: api_endpoints.campsite(campsite_id.value),
        method: 'GET',
        xhrFields: {
            withCredentials: true
        },
        dataType: 'json',
        success: function (data, stat, xhr) {
            var interval = setInterval(function () {
                if (campsite_classes.value.length > 0) {
                    temp_campsite.value = data;
                    campsite.value = JSON.parse(JSON.stringify(data));
                    if (data.campsite_class) {
                        onCampsiteClassChange();
                    }
                    clearInterval(interval);
                }
            }, 100);

        },
        error: function (resp) {
            if (resp.status == 404) {
                router.push({
                    name: '404'
                });
            }
        }
    });
}
const fetchCampground = function () {
    $.get(api_endpoints.campground(campsite_id.value), function (data) {
        campground.value = data;
        campsite.value.campground = data.id;
    })
}
const fetchCampsiteClasses = function () {
    $.get(api_endpoints.campsite_classes_active, function (data) {
        campsite_classes.value = data;
    })
}
const goBack = function () {
    router.go(-1);
}
const addCampsite = function () {
    sendData.value(api_endpoints.campsites, 'POST')
}
const updateCampsite = function () {
    sendData.value(api_endpoints.campsite(campsite_id.value), 'PUT')
}
const sendData = function (url, method) {
    isLoading.value = true;
    var data = campsite.value;
    $.ajax({
        beforeSend: function (xhrObj) {
            xhrObj.setRequestHeader("Content-Type", "application/json");
            xhrObj.setRequestHeader("Accept", "application/json");
        },
        xhrFields: {
            withCredentials: true
        },
        url: url,
        method: method,
        data: JSON.stringify(data),
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        success: function (data) {
            if (Array.isArray(data)) {
                data = data[data.length - 1];
            }
            temp_campsite.value = data;
            campsite.value = JSON.parse(JSON.stringify(data));
            if (data.campsite_class) {
                onCampsiteClassChange();
            }
            setTimeout(function () {
                isLoading.value = false;
            }, 500);
        },
        error: function (error) {
            isLoading.value = false

        }
    });


}

onMounted(function () {
    campsiteForm.value = document.forms.campsiteForm;
    campsite_id.value = route.params.id
    fetchCampsiteClasses();
    fetchCampground();
    if (campsite_id.value) {
        createCampsite.value = false;
        fetchCampsite();
    }
})

</script>

<style lang="css">
.table_btn {
    margin-top: 25px;
    margin-right: -14px;
}

@media(max-width: 768px) {
    .btn-create {
        position: absolute;
        left: 13px;
    }
}

@media(min-width: 768px) {
    .btn-create {
        position: absolute;
        left: 220px;
    }
}

@media(min-width: 992px) {
    .btn-create {
        position: absolute;
        left: 300px;
    }
}

@media(min-width: 1200px) {
    .btn-create {
        position: absolute;
        left: 390px;
    }
}
</style>
