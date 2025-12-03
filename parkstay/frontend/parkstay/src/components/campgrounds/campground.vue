<template lang="html">
    <div class="panel-group" id="applications-accordion" role="tablist" aria-multiselectable="true">
        <pkCsClose ref="closeCampsiteRef" @closeCampsite="closeCampsite"></pkCsClose>
        <pkCsOpen ref="openCampsiteRef" @openCampsite="openCampsite()"></pkCsOpen>
        <div class="card p-3" id="applications">
            <div class="panel-heading" role="tab" id="applications-heading">
                <h4 class="panel-title">
                    {{ title }}
                </h4>
            </div>
            <div id="applications-collapse" class="" role="tabpanel" aria-labelledby="applications-heading">
                <div class="panel-body">
                    <div class="col-lg-12">
                        <div class="row">
                            <campgroundAttr :createCampground=false :campground="campground">
                            </campgroundAttr>
                        </div>
                        <hr style="margin: 30px 0px;" />
                        <stay-history :object_id="ID" :datatableURL="stayHistoryURL"
                            ></stay-history>
                        <priceHistory ref="price_dt" level="campground" :dt_options="ph_options"
                            :historyDeleteURL="priceHistoryDeleteURL" :showAddBtn="hasCampsites"
                            v-show="campground.price_level == 0" :object_id="ID"></priceHistory>
                        <closureHistory ref="cg_closure_dt" :object_id="ID" :datatableURL="closureHistoryURL">
                        </closureHistory>
                    </div>
                </div>
            </div>
        </div>
        <div class="card p-3" id="applications" style="margin-top:50px;">
            <div class="panel-heading" role="tab" id="applications-heading">
                <h4 class="panel-title">
                    Campsites
                </h4>
            </div>
            <div class="" role="tabpanel" aria-labelledby="applications-heading" id="campsites">
                <div class="panel-body">
                    <div class="col-lg-12">
                        <div class="row">
                            <div class="well">
                                <div class="col-sm-offset-8 col-sm-4">
                                    <button @click="openBulkCloseCG()"
                                        class="btn btn-outline-primary table_btn me-2">Close Campsites</button>
                                    <router-link :to="{ name: 'add_campsite', params: { id: campground_id } }"
                                        class="btn btn-primary table_btn" style="margin-right: 1em;">Add
                                        Campsite</router-link>
                                </div>
                                <datatable ref="cg_campsites_dt" :dtHeaders="cs_headers" :dtOptions="cs_options"
                                    id="cs_table"></datatable>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <confirmbox id="deleteRange" :options="deletePrompt"></confirmbox>
        <bulk-close-campsites v-on:bulkCloseCampsites="onBulkCloseCampsites"
            @cancel="closeBulkCloseCG" ref="bulkCloseCampsitesRef" v-bind:campsites="campsites" />
    </div>

</template>

<script setup>
import datatable from '../utils/datatable.vue'
import closureHistory from '../utils/closureHistory.vue'
import priceHistory from '../utils/priceHistory/priceHistory.vue'
import campgroundAttr from './campground-attr.vue'
import confirmbox from '../utils/confirmbox.vue'
import bulkCloseCampsites from '../campsites/closureHistory/bulkClose.vue'
import pkCsClose from '../campsites/closureHistory/closeCampsite.vue'
import pkCsOpen from '../campsites/closureHistory/openCampsite.vue'
import stayHistory from '../utils/stayHistory/stayHistory.vue'
import {
    bus
}
    from '../utils/eventBus.js'
import {
    $,
    Moment,
    api_endpoints,
    helpers
}
from '../../hooks.js'
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router';

const router = useRouter()
const route = useRoute()

const closeCampsiteRef = ref(null)
const openCampsiteRef = ref(null)
const price_dt = ref(null)
const cg_closure_dt = ref(null)
const cg_campsites_dt = ref(null)
const bulkCloseCampsitesRef = ref(null)

const stayHistoryURL = api_endpoints.campgroundStayHistory(route.params.id)
const campground = ref({
    address: {},
    images: []
})
const campsites = ref([])
const isOpenOpenCS = ref(false)
const isOpenCloseCS = ref(false)
const showBulkCloseCampsites = ref(false)
const deleteRange = ref(null)
const ph_options = ref({
    responsive: true,
    processing: true,
    deferRender: true,
    order: [],
    columnDefs: [
        { "defaultContent": "-", "targets": "_all" },
    ],
    ajax: {
        url: api_endpoints.campground_price_history(route.params.id),
        dataSrc: ''
    },
    columns: [{
        data: 'date_start',
        mRender: function (data, type, full) {
            return Moment(data).format('DD/MM/YYYY');
        }

    }, {
        data: 'date_end',
        mRender: function (data, type, full) {
            if (data) {

                return Moment(data).format('DD/MM/YYYY');

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
                var column = "<td ><a href='#' class='editPrice' data-date_start=\"__START__\"  data-date_end=\"__END__\"  data-rate=\"__RATE__\" data-reason=\"__REASON__\" data-details=\"__DETAILS__\"  data-bookingpolicyid=\"__BOOKINGPOLICYID__\" >Edit</a><br/>"
                if (full.deletable) {
                    column += "<a href='#' class='deletePrice' data-date_start=\"__START__\"  data-date_end=\"__END__\"  data-rate=\"__RATE__\" data-reason=\"__REASON__\" data-details=\"__DETAILS__\">Delete</a></td>";
                }
                column = column.replace(/__START__/g, full.date_start)
                column = column.replace(/__END__/g, full.date_end)
                column = column.replace(/__RATE__/g, full.rate_id)
                column = column.replace(/__REASON__/g, full.reason)
                column = column.replace(/__DETAILS__/g, full.details)
                column = column.replace(/__BOOKINGPOLICYID__/g, full.booking_policy_id)
                return column
            }
            else {
                return "";
            }
        }
    }],
})
const cs_options = ref({
    responsive: true,
    processing: true,
    deferRender: true,
    ajax: {
        url: api_endpoints.campgroundCampsites(route.params.id),
        dataSrc: ''
    },
    columnDefs: [
        { "defaultContent": "-", "targets": "_all" },
        {
            responsivePriority: 1,
            targets: 0
        }, {
            responsivePriority: 2,
            targets: 3
        }, {
            responsivePriority: 3,
            targets: 1
        }, {
            responsivePriority: 4,
            targets: 2
        }],
    columns: [{
        data: 'name'
    }, {
        data: 'type',
        mRender: function (data, type, full) {
            if (data) {
                var max_length = 25;
                var name = (data.length > max_length) ? data.substring(0, max_length - 1) + '...' : data;
                var column = '<td> <div class="name_popover" tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__" >' + name + '</div></td>';
                return column.replace('__NAME__', data);
            }
            return '';
        }
    }, {
        data: 'active',
        mRender: function (data, type, full) {
            return data ? 'Open' : 'Closed'
        }
    }, {
        data: 'price'
    }, {
        "mRender": function (data, type, full) {
            var id = full.id;
            if (full.active) {
                var column = "<td ><a href='#' class='detailRoute' data-campsite=\"__ID__\" >Edit</a><br/>";
                if (full.campground_open) {
                    column += "<a href='#' class='statusCS' data-status='close' data-campsite=\"__ID__\" >Close</a></td>";
                }
            }
            else {
                var column = "<td ><a href='#' class='detailRoute' data-campsite=\"__ID__\" >Edit</a><br/>";
                if (full.campground_open) {
                    column += "<a href='#' class='statusCS' data-status='open' data-campsite=\"__ID__\" data-current_closure='" + full.current_closure + "' data-current_closure_id='" + full.current_closure_id + "'>Open</a></td>";
                }
            }

            return column.replace(/__ID__/g, id);
        }
    }],
})
const title = 'Campground'
const cs_headers = ['Name', 'Type', 'Status', 'Price', 'Action']
const deletePrompt = ref({
    icon: "<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
    message: "Are you sure you want to Delete ?",
    buttons: [{
        text: "Delete",
        event: "deleteRange",
        bsColor: "btn-danger",
        handler: function () {
            deleteBookingRange(deleteRange.value);
            deleteRange.value = null;
        },
        autoclose: true
    }],
    id: 'deleteRange'
})
const closureHistoryURL = computed(function () {
    return api_endpoints.campground_status_history(route.params.id);
})
const priceHistoryURL = computed(function () {
    return api_endpoints.campground_price_history(route.params.id);
})
const ID = computed(function () {
    return parseInt(route.params.id);
})
const hasCampsites = computed(function () {
    return campsites.value.length > 0;
})
const campground_id = computed(function () {
    return campground.value.id ? campground.value.id : 0;
})
const priceHistoryDeleteURL = computed(function () {
    return api_endpoints.delete_campground_price(ID);
})


const deleteBookingRange = function (id) {
    var url = api_endpoints.campground_booking_ranges_detail(id);
    $.ajax({
        method: "DELETE",
        url: url,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') }
    }).done(function (msg) {
        cg_closure_dt.value.vmDataTable.ajax.reload();
    });
}
const showCloseCS = function () {
    closeCampsiteRef.value.isOpen = true;
}
const openBulkCloseCG = () => {
    bulkCloseCampsitesRef.value.isOpen = true
}
const closeBulkCloseCG = () => {
    bulkCloseCampsitesRef.value.isOpen = false
}

const openCampsite = function () {
    var data = openCampsiteRef.value.formdata;
    $.ajax({
        url: api_endpoints.campsite_booking_ranges_detail(openCampsiteRef.value.id),
        method: 'PATCH',
        xhrFields: { withCredentials: true },
        data: data,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        dataType: 'json',
        success: function (data, stat, xhr) {
            openCampsiteRef.value.close();
            refreshCampsiteClosures();
        },
        error: function (data) {
            openCampsiteRef.value.errors = true;
            openCampsiteRef.value.errorString = helpers.apiError(data);
        }
    });

}
const closeCampsite = function () {
    const data = closeCampsiteRef.value.formdata;
    $.ajax({
        url: api_endpoints.campsite_booking_ranges(),
        method: 'POST',
        xhrFields: { withCredentials: true },
        data: data,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        dataType: 'json',
        success: function (data, stat, xhr) {
            closeCampsiteRef.value.close();
            refreshCampsiteClosures();
        },
        error: function (resp) {
            closeCampsiteRef.value.errors = true;
            closeCampsiteRef.value.errorString = helpers.apiError(resp);
        }
    });
}
const onBulkCloseCampsites = function () {
    // var data = bulkCloseCampsitesRef.value.formdata;
    var formData = {}
    $.each($('#bulkCloseCGForm').serializeArray(), function(_, field) {
        if (field.name == 'campsites') {

        } else {
            formData[field.name] = field.value;
        }

    });

    formData['campsites'] = $('#bcs-campsites').val();
    formData['range_start'] = $('#closure_start').val();
    formData['range_end'] = $('#closure_end').val();
    formData['status'] = 1

    $.ajax({
        url: api_endpoints.bulk_close_campsites(),
        method: 'POST',
        xhrFields: { withCredentials: true },
        data: formData,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        dataType: 'json',
        success: function (formData, stat, xhr) {
            
            // bulkCloseCampsitesRef.value.hide();       
            closeBulkCloseCG()     
            refreshCampsiteClosures();
        },
        error: function (resp) {
            bulkCloseCampsitesRef.value.errors = true;
            bulkCloseCampsitesRef.value.errorString = helpers.apiError(resp);
        }
    });
}
const refreshCampsiteClosures = function (dt) {
    cg_campsites_dt.value.vmDataTable.ajax.reload();
}
const showOpenOpenCS = function () {
    openCampsiteRef.value.isOpen = true;
}
const fetchCampsites = function () {
    $.get(api_endpoints.campgroundCampsites(route.params.id), function (data) {
        campsites.value = data;
    });
}
const fetchCampground = function () {
    $.ajax({
        url: api_endpoints.campground(route.params.id),
        dataType: 'json',
        success: function (data, stat, xhr) {
            campground.value = data;
            fetchCampsites();
            bus.emit('campgroundFetched');
        }
    });
}

onMounted(function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    cg_campsites_dt.value.vmDataTable.on('click', '.detailRoute', function (e) {
        e.preventDefault();
        var id = $(this).attr('data-campsite');
        router.push({
            name: 'view_campsite',
            params: {
                id: campground.value.id,
                campsite_id: id
            }
        });
    });
    cg_campsites_dt.value.vmDataTable.on('click', '.statusCS', function (e) {
        e.preventDefault();
        var id = $(this).attr('data-campsite');
        var status = $(this).attr('data-status');
        var current_closure = $(this).attr('data-current_closure') ? $(this).attr('data-current_closure') : '';
        var current_closure_id = $(this).attr('data-current_closure_id') ? $(this).attr('data-current_closure_id') : '';

        if (status === 'open') {
            showOpenOpenCS();
            // Update open modal attributes
            openCampsiteRef.value.id = current_closure_id;
            openCampsiteRef.value.current_closure = current_closure;
        } else if (status === 'close') {
            showCloseCS();
            // Update close modal attributes
            closeCampsiteRef.value.formdata.campsite = id;
        }
    });
    helpers.namePopover($, cg_campsites_dt.value.vmDataTable);
    fetchCampground();
})

</script>

<style lang="css">
.well {
    background-color: #fff;
}

.btn {
    margin-bottom: 10px;
}
</style>
