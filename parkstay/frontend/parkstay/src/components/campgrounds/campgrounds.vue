<template>
    <div id="groundsList">
        <pkCgClose></pkCgClose>
        <pkCgOpen></pkCgOpen>
        <div class="panel-group" id="returns-accordion" role="tablist" aria-multiselectable="true">
            <div class="panel panel-default border p-3" id="returns">
                <base-panel-heading :title="title">
                    <div class="form-group text-end">
                        <a style="margin-top: 20px;" class="btn btn-primary" @click="addCampground()">Add
                            Campground</a>
                        <a style="margin-top: 20px;" class="btn btn-primary" @click="showBulkClose = !showBulkClose">
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
        <bulk-close :show="showBulkClose" ref="bulkClose" />
    </div>
</template>

<script>
import {
    $,
    api_endpoints
} from '../../hooks'
import datatable from '../utils/datatable.vue'
import pkCgClose from './closeCampground.vue'
import pkCgOpen from './openCampground.vue'
import bulkClose from '../utils/closureHistory/bulk-close.vue'
import { bus } from '../utils/eventBus.js'
import { mapGetters } from 'vuex'
module.exports = {
    name: 'campgrounds',
    data: function () {
        let vm = this;
        return {
            grounds: [],
            rows: [],
            title: 'Campgrounds',
            selected_status: 'All',
            selected_region: 'All',
            selected_park: 'All',
            selected_district: 'All',
            isOpenAddCampground: false,
            isOpenOpenCG: false,
            isOpenCloseCG: false,
            showBulkClose: false,
            dtoptions: {

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
            }
        }
    },
    components: {
        pkCgClose,
        pkCgOpen,
        datatable,
        "bulk-close": bulkClose,
    },
    computed: {
        ...mapGetters([
            'regions',
            'districts',
            'parks'
        ]),
    },
    watch: {
        showBulkClose: function () {
            let vm = this
            this.$refs.bulkClose.isModalOpen = vm.showBulkClose;
            this.$refs.bulkClose.initSelectTwo();
        },
        selected_region: function () {
            let vm = this;
            if (vm.selected_region != 'All') {
                vm.$refs.dtGrounds.vmDataTable.columns(2).search(vm.selected_region).draw();
            } else {
                vm.$refs.dtGrounds.vmDataTable.columns(2).search('').draw();
            }
        },
        selected_status: function () {
            let vm = this;
            if (vm.selected_status != 'All') {
                vm.$refs.dtGrounds.vmDataTable.columns(1).search(vm.selected_status).draw();
            } else {
                vm.$refs.dtGrounds.vmDataTable.columns(1).search('').draw();
            }
        },
        selected_district: function () {
            let vm = this;
            if (vm.selected_district != 'All') {
                vm.$refs.dtGrounds.vmDataTable.columns(3).search(vm.selected_district).draw();
            } else {
                vm.$refs.dtGrounds.vmDataTable.columns(3).search('').draw();
            }
        },
        selected_park: function () {
            let vm = this;
            if (vm.selected_park != 'All') {
                vm.$refs.dtGrounds.vmDataTable.columns(4).search(vm.selected_park).draw();
            } else {
                vm.$refs.dtGrounds.vmDataTable.columns(4).search('').draw();
            }
        }
    },
    methods: {
        flagFormat: function (flag) {
            return flag ? 'Yes' : 'No'
        },
        update: function () {
            var vm = this;
            var url = api_endpoints.regions;
            $.ajax({
                url: url,
                dataType: 'json',
                success: function (data, stat, xhr) {
                    vm.regions = data;
                }
            });
        },
        updateTable: function () {
            var vm = this;
            vm.$refs.dtGrounds.vmDataTable.draw();
        },
        showOpenCloseCG: function () {
            this.isOpenCloseCG = true;
        },
        showOpenOpenCG: function () {
            this.isOpenOpenCG = true;
        },
        openDetail: function (cg_id) {
            this.$router.push({
                name: 'cg_detail',
                params: {
                    id: cg_id
                }
            });
        },
        addCampground: function (cg_id) {
            this.$router.push({
                name: 'cg_add',
            });
        },
        fetchRegions: function () {
            let vm = this;
            if (vm.regions.length == 0) {
                vm.$store.dispatch("fetchRegions");
            }
        },
        fetchParks: function () {
            let vm = this;
            if (vm.parks.length == 0) {
                vm.$store.dispatch("fetchParks");
            }
        },
        fetchDistricts: function () {
            let vm = this;
            if (vm.districts.length == 0) {
                vm.$store.dispatch("fetchDistricts");
            }
        }
    },
    mounted: function () {
        var vm = this;
        vm.$refs.dtGrounds.vmDataTable.on('click', '.detailRoute', function (e) {
            e.preventDefault();
            var id = $(this).attr('data-campground');
            vm.openDetail(id);
        });
        vm.$refs.dtGrounds.vmDataTable.on('click', '.statusCG', function (e) {
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
                bus.$emit('openCG', data);
                vm.showOpenOpenCG();
            } else if (status === 'close') {
                var data = {
                    'id': id,
                };
                bus.$emit('closeCG', data);
                vm.showOpenCloseCG();
            }
        });
        vm.$refs.dtGrounds.vmDataTable.on('click', '.addBooking', function (e) {
            e.preventDefault();
            var id = $(this).attr('data-campground');
            vm.$router.push({
                name: 'add-booking',
                params: {
                    "cg": id
                }
            });
        });
        bus.$on('refreshCGTable', function () {
            vm.$refs.dtGrounds.vmDataTable.ajax.reload();
        });
        vm.fetchRegions();
        vm.fetchParks();
        vm.fetchDistricts();
    }
};
</script>
