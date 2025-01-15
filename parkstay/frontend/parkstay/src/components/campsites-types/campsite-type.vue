<template lang="html">
    <div id="campsite-type">
        <div class="card p-3" id="applications">

            <div id="applications-collapse" class="" role="tabpanel" aria-labelledby="applications-heading">
                <div class="panel-body">
                    <div class="col-lg-12">
                        <div class="row">
                            <form v-show="!isLoading">
                                <div class="panel panel-primary">
                                    <div class="panel-heading">
                                        <h3 class="panel-title">{{ createCampsiteType ? 'New' : 'Edit' }} Campsite Type
                                        </h3>
                                    </div>
                                    <div class="panel-body">
                                        <div class="row">
                                            <div class="col-md-6">
                                                <div class="form-group">
                                                    <label class="control-label">Name</label>
                                                    <input type="text" name="name" class="form-control"
                                                        v-model="campsite_type.name" required />
                                                </div>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="form-group">
                                                    <label class="control-label">Maximum Number of Vehicles</label>
                                                    <input type="number" name="max_vehicles" class="form-control"
                                                        v-model="campsite_type.max_vehicles" required />
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6">
                                                <div class="form-group">
                                                    <label class="control-label">Minimum Number of People</label>
                                                    <input type="number" name="name" class="form-control"
                                                        v-model="campsite_type.min_people" required />
                                                </div>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="form-group">
                                                    <label class="control-label">Maximum Number of People</label>
                                                    <input type="number" name="name" class="form-control"
                                                        v-model="campsite_type.max_people" required />
                                                </div>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6">
                                                <div class="form-group">
                                                    <div class="checkbox">
                                                        <label class="checkbox-inline">
                                                            <input type="checkbox"
                                                                v-model="campsite_type.tent" />Tent</label>
                                                    </div>
                                                    <div class="checkbox">
                                                        <label class="checkbox-inline">
                                                            <input type="checkbox"
                                                                v-model="campsite_type.campervan" />Campervan</label>
                                                    </div>
                                                    <div class="checkbox">
                                                        <label class="checkbox-inline">
                                                            <input type="checkbox"
                                                                v-model="campsite_type.caravan" />Caravan</label>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <select-panel ref="select_features" :options="features"
                                            :selected="selected_features" id="select-features" @onChange="onChangeSelectedFeatures"></select-panel>
                                        <editor ref="descriptionEditor" v-model="campsite_type.description"></editor>
                                        <div class="row">
                                            <div class="col-sm-12">
                                                <div class="form-group pull-right">
                                                    <button type="button" v-show="createCampsiteType"
                                                        style="margin-right:5px" @click="addCampsiteType()"
                                                        class="btn btn-primary">Create</button>
                                                    <button type="button" v-show="!createCampsiteType"
                                                        style="margin-right:5px" @click="updateCampsiteType()"
                                                        class="btn btn-primary">Update</button>
                                                    <button type="button" class="btn btn-default pull-right"
                                                        @click="goBack">Cancel</button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </form>
                            <loader :isLoading="isLoading">Saving Campsite Type Data...</loader>
                        </div>
                    </div>
                    <div class="col-lg-12" v-if="!createCampsiteType">
                        <priceHistory level="campsite_class" :showAddBtn="canAddRate" ref="price_dt"
                            :object_id="campsiteTypeId" :dt_options="ph_options"
                            :historyDeleteURL="priceHistoryDeleteURL"></priceHistory>
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
    Moment
}
    from '../../hooks.js';
import editor from '../utils/editor.vue'
import selectPanel from '../utils/select-panel.vue'
import loader from '../utils/loader.vue'
import priceHistory from '../utils/priceHistory/priceHistory.vue'
import { computed, onMounted, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter()
const route = useRoute()
const isLoading = ref(false)
const campsite = ref(null)
const campsite_type = ref({})
const features = ref([])
const selected_features = ref([])
const createCampsiteType = ref(true)
const select_features = ref(null)
const campsite_type_id = ref(null)
const ph_options = ref({
    responsive: true,
    processing: true,
    deferRender: true,
    order: [
        [0, 'desc']
    ],
    ajax: {
        url: route.params.campsite_type_id ? api_endpoints.campsiteclass_price_history(route.params.campsite_type_id) : undefined,
        dataSrc: ''
    },
    columns: [{
        data: 'date_start',
        mRender: function (data, type, full) {
            return Moment(data).format('MMMM Do, YYYY');
        }

    }, {
        data: 'date_end',
        mRender: function (data, type, full) {
            if (data) {
                return Moment(data).add(1, 'day').format('MMMM Do, YYYY');
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
            if (data) {
                var id = full.id;
                var column = "<td ><a href='#' class='editPrice' data-date_start=\"__START__\"  data-date_end=\"__END__\"  data-rate=\"__RATE__\" data-reason=\"__REASON__\" data-details=\"__DETAILS__\">Edit</a><br/>"
                if (full.deletable) {
                    column += "<a href='#' class='deletePrice' data-date_start=\"__START__\"  data-date_end=\"__END__\"  data-rate=\"__RATE__\" data-reason=\"__REASON__\" data-details=\"__DETAILS__\">Delete</a></td>";
                }
                column = column.replace(/__START__/g, full.date_start)
                column = column.replace(/__END__/g, full.date_end)
                column = column.replace(/__RATE__/g, full.rate_id)
                column = column.replace(/__REASON__/g, full.reason)
                column = column.replace(/__DETAILS__/g, full.details)
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
const campsiteTypeId = computed(
    () => parseInt(campsite_type_id.value)
)
const canAddRate = computed(
    () => campsite_type.value.can_add_rate ? campsite_type.value.can_add_rate : false
)
const priceHistoryDeleteURL = computed(
    () => api_endpoints.deleteCampsiteClassPrice(campsiteTypeId.value)
)


const init = function () {
    loadFeatures();
    if (route.params.campsite_type_id) {
        createCampsiteType.value = false;
        fetchCampsiteType();
    }
}
const goBack = function () {
    router.go(-1);
}
const loadFeatures = function () {
    var url = api_endpoints.features;
    $.ajax({
        url: url,
        dataType: 'json',
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        success: function (data, stat, xhr) {
            features.value = data;
        }
    });
}
const addCampsiteType = function () {
    sendData(api_endpoints.campsite_classes, 'POST');
}
const updateCampsiteType = function () {
    sendData(api_endpoints.campsite_class(campsite_type.value.id), 'PUT');
}
const fetchCampsiteType = function () {
    $.ajax({
        url: api_endpoints.campsite_class(route.params.campsite_type_id),
        method: 'GET',
        xhrFields: {
            withCredentials: true
        },
        dataType: 'json',
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        success: function (data, stat, xhr) {
            campsite_type.value = data;
            select_features.value.loadSelectedFeatures(data.features);
            campsite_type.value.features = select_features.value.selectedRef.map(feature => feature.url)
            isLoading.value = false;
        },
        error: function (resp) {
            isLoading.value = false;
            if (resp.status == 404) {
                router.push({
                    name: '404'
                });
            }
        }
    });
}

const sendData = function (url, method) {
    isLoading.value = true;
    const data = campsite_type.value;
    $.ajax({
        beforeSend: function (xhrObj) {
            xhrObj.setRequestHeader("Content-Type", "application/json");
            xhrObj.setRequestHeader("Accept", "application/json");
        },
        xhrFields: {
            withCredentials: true
        },
        url: url,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        method: method,
        data: JSON.stringify(data),
        success: async function (data) {
            if (method == 'POST') {
                isLoading.value = false;
                await router.push({
                    name: 'campsite-type-detail',
                    params: {
                        campsite_type_id: data.id
                    }
                });
                router.go(0)
            }
            else {
                setTimeout(function () {
                    isLoading.value = false;
                }, 500);
            }
        },
        error: function(error) {
            window.alert('an error ocurred')
            isLoading.value = false;
        }
    })
}

onMounted(() => {
    campsite_type_id.value = route.params.campsite_type_id
    init();
})

const onChangeSelectedFeatures = (values) => {
    campsite_type.value.features = select_features.value.selectedRef.map(feature => feature.url)
}

</script>

<style lang="css">
.panel-body>div.row {
    margin-top: 10px;
}
</style>
