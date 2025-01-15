<template>
    <div id="groundsList">
        <pkCgClose ref='pkCgCloseRef' @isOpenCloseCG="handleCloseCampground" @refreshCGTable="onRefreshCGTable"></pkCgClose>
        <pkCgOpen ref='pkCgOpenRef' @isOpenOpenCG="handleOpenCampground" @refreshCGTable="onRefreshCGTable"></pkCgOpen>
        <div class="panel-group" id="returns-accordion" role="tablist" aria-multiselectable="true">
            <div class="panel panel-default border p-3" id="returns">
                <base-panel-heading :title="title">
                    <div class="form-group text-end">
                        <a class="btn btn-primary mt-4 me-2" @click="addCampground()">Add
                            Campground</a>
                        <a class="btn btn-primary mt-4" @click="showBulkClose = !showBulkClose">
                            Close Campgrounds</a>
                    </div>
                </base-panel-heading>
                <div id="returns-collapse" oldclass="panel-collapse collapse in" role="tabpanel"
                    aria-labelledby="returns-heading">
                    <div class="panel-body">
                        <div id="groundsList">
                            <div class="col-12">
                                <form class="form" id="campgrounds-filter-form">
                                    <div class="row">

                                        <div class="col-md-8">
                                            <div class="row">
                                                <div class="col-md-3">
                                                    <div class="form-group">
                                                        <label for="campgrounds-filter-status">Status: </label>
                                                        <select v-model="selected_status"
                                                            class="form-control form-select" name="status"
                                                            id="campgrounds-filter-status">
                                                            <option value="All">All</option>
                                                            <option value="Open">Open</option>
                                                            <option value="Temporarily Closed">Temporarily Closed
                                                            </option>
                                                        </select>
                                                    </div>
                                                </div>
                                                <div class="col-md-3">
                                                    <div class="form-group">
                                                        <label for="applications-filter-region">Region: </label>
                                                        <select class="form-control form-select"
                                                            v-model="selected_region">
                                                            <option value="All">All</option>
                                                            <option v-for="region in regions" :value="region.name">{{
                                                                region.name }}</option>
                                                        </select>
                                                    </div>
                                                </div>
                                                <div class="col-md-3">
                                                    <div class="form-group">
                                                        <label for="applications-filter-region">District: </label>
                                                        <select class="form-control form-select"
                                                            v-model="selected_district">
                                                            <option value="All">All</option>
                                                            <option v-for="district in districts"
                                                                :value="district.name">{{
                                                                    district.name }}</option>
                                                        </select>
                                                    </div>
                                                </div>
                                                <div class="col-md-3">
                                                    <div class="form-group">
                                                        <label for="applications-filter-region">Park: </label>
                                                        <select class="form-control form-select"
                                                            v-model="selected_park">
                                                            <option value="All">All</option>
                                                            <option v-for="park in parks" :value="park.name">{{
                                                                park.name }}</option>
                                                        </select>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                    </div>
                                </form>
                                </br>
                            </div>
                            <div class="col-12">
                                <datatable :dtHeaders="['Campground', 'Status', 'Region', 'District', 'Park', 'Action']"
                                    :dtOptions="dtoptions" ref="dtGrounds" id="campground-table"></datatable>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <bulk-close-component :show="showBulkClose" ref="bulkClose" @close="closeBulkClose()" />
    </div>
</template>

<script setup>
import {
    $,
    api_endpoints,
    bus
} from '../../hooks.js'
import datatable from '../utils/datatable.vue'
import pkCgClose from './closeCampground.vue'
import pkCgOpen from './openCampground.vue'
import basePanelHeading from "../../layouts/base-panel-heading.vue";
import bulkCloseComponent from '../utils/closureHistory/bulk-close.vue'
import { mapGetters } from 'vuex'
import { computed, ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router';
import { useStore } from "../../apps/store.js";

const router = useRouter()
const store = useStore()

const grounds = ref([])
const rows = ref([])
const title = ref('Campgrounds')
const selected_status = ref('All')
const selected_region = ref('All')
const selected_park = ref('All')
const selected_district = ref('All')
const pkCgCloseRef = ref(null)
const pkCgOpenRef = ref(null)
const dtGrounds = ref(null)
const bulkClose = ref(null)
const isOpenAddCampground = ref(false)
const showBulkClose = ref(false)
const dtoptions = ref({
    responsive: true,

    columnDefs: [
        { targets: [0, 3], responsivePriority: 1 },
        { "defaultContent": "-", "targets": "_all" }
    ],
    ajax: {
        "url": api_endpoints.campgrounds_datatable,
        "dataSrc": ''
    },
    columns: [{
        "data": "name"
    }, {
        "data": "active",
        "mRender": function (data, type, full) {
            var status = (data == true) ? "Open" : "Temporarily Closed";
            var column = "<td >__Status__</td>";
            column += data ? "" : "<br/><br/>" + full.current_closure;
            return column.replace('__Status__', status);
        }
    }, {
        "data": "region"
    }, {
        "data": "district"
    }, {
        "data": "park"
    }, {
        "mRender": function (data, type, full) {
            var id = full.id;
            var addBooking = "<br/><a href='#' class='addBooking' data-campground=\"__ID__\" >Add Booking</a>";
            var availability_admin = "<br/><a target='_blank' href='/availability_admin/?site_id=__ID__' >Availability</a>";
            var column = "";

            if (full.active) {
                var column = "<td ><a href='#' class='detailRoute' data-campground=\"__ID__\" >Edit </a><br/><a href='#' class='statusCG' data-status='close' data-campground=\"__ID__\" > Close </a>";
            } else {
                var column = "<td ><a href='#' class='detailRoute' data-campground=\"__ID__\" >Edit </a><br/><a href='#' class='statusCG' data-status='open' data-campground=\"__ID__\" data-current_closure=\"__Current_Closure__\" data-current_closure_id=\"__Current_Closure_ID__\">Open</a>";
            }

            // column += full.campground_type == '0' ? addBooking : "";
            // column += full.campground_type == '0' ? availability_admin:"";
            column += "</td>";
            column = column.replace(/__Current_Closure__/, full.current_closure);
            column = column.replace(/__Current_Closure_ID__/, full.current_closure_id);
            return column.replace(/__ID__/g, id);
        }
    },],
    processing: true
})

const regions = computed(() => store.getters.regions)
const districts = computed(() => store.getters.districts)
const parks = computed(() => store.getters.parks)

watch(() => showBulkClose.value, function (value) {
    bulkClose.value.isModalOpen = value;
    bulkClose.value.initSelectTwo();
})
watch(() => selected_region.value, function (value) {
    if (value != 'All') {
        dtGrounds.value.vmDataTable.columns(2).search(value).draw();
    } else {
        dtGrounds.value.vmDataTable.columns(2).search('').draw();
    }
})
watch(() => selected_status.value, function (value) {
    if (value != 'All') {
        dtGrounds.value.vmDataTable.columns(1).search(value).draw();
    } else {
        dtGrounds.value.vmDataTable.columns(1).search('').draw();
    }
})
watch(() => selected_district.value, function (value) {
    if (value != 'All') {
        dtGrounds.value.vmDataTable.columns(3).search(value).draw();
    } else {
        dtGrounds.value.vmDataTable.columns(3).search('').draw();
    }
})
watch(() => selected_park.value, function (value) {
    if (value != 'All') {
        dtGrounds.value.vmDataTable.columns(4).search(value).draw();
    } else {
        dtGrounds.value.vmDataTable.columns(4).search('').draw();
    }
})

const flagFormat = function (flag) {
    return flag ? 'Yes' : 'No'
}

const closeBulkClose = function () {
    showBulkClose.value = false;
    dtGrounds.value.vmDataTable.ajax.reload();
}
const handleOpenCampground = function (value) {
    pkCgOpenRef.value.isOpen = value
}
const handleCloseCampground = function (value) {
    pkCgCloseRef.value.isOpen = value
}

const showOpenCloseCG = function () {
    pkCgCloseRef.value.isOpen = true
}
const showOpenOpenCG = function () {
    pkCgOpenRef.value.isOpen = true
}

const onRefreshCGTable =  function () {
    dtGrounds.value.vmDataTable.ajax.reload();
}

const openDetail = function (cg_id) {
    router.push({
        name: 'cg_detail',
        params: {
            id: cg_id
        }
    });
}
const addCampground = function (cg_id) {
    router.push({
        name: 'cg_add',
    });
}
const fetchRegions = function () {
    if (regions.value.length == 0) {
        store.dispatch("fetchRegions");
    }
}
const fetchParks = function () {
    if (parks.value.length == 0) {
        store.dispatch("fetchParks");
    }
}
const fetchDistricts = function () {
    if (districts.value.length == 0) {
        store.dispatch("fetchDistricts");
    }
}

onMounted(function () {
    dtGrounds.value.vmDataTable.on('click', '.detailRoute', function (e) {
        e.preventDefault();
        var id = $(this).attr('data-campground');
        openDetail(id);
    });
    dtGrounds.value.vmDataTable.on('click', '.statusCG', function (e) {
        e.preventDefault();
        var id = $(this).attr('data-campground');
        var status = $(this).attr('data-status');
        var current_closure = $(this).attr('data-current_closure') ? $(this).attr('data-current_closure') : '';
        var current_closure_id = $(this).attr('data-current_closure_id') ? $(this).attr('data-current_closure_id') : '';
        if (status === 'open') {
            var data = {
                'id': current_closure_id,
                'closure': current_closure
            };
            bus.emit('openCG', data);
            showOpenOpenCG();
        } else if (status === 'close') {
            var data = {
                'id': id,
            };
            bus.emit('closeCG', data);
            showOpenCloseCG();
        }
    });
    dtGrounds.value.vmDataTable.on('click', '.addBooking', function (e) {
        e.preventDefault();
        var id = $(this).attr('data-campground');
        router.push({
            name: 'add-booking',
            params: {
                "cg": id
            }
        });
    });
    fetchRegions();
    fetchParks();
    fetchDistricts();
})
</script>
