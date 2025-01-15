<template lang="html">
    <div id="campsite-type-dash">
        <div class="card p-3" id="applications">
            <base-panel-heading title="Campsite Types">
                <router-link :to="{ name: 'add-campsite-type' }" style="margin-top: 20px;"
                    class="btn btn-primary table_btn">Add Campsite Type</router-link>
            </base-panel-heading>
            <div id="applications-collapse" class="" role="tabpanel" aria-labelledby="applications-heading">
                <div class="panel-body">
                    <div id="groundsList">
                        <form class="form" id="campgrounds-filter-form">
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="campgrounds-filter-status">Status: </label>
                                            <select v-model="selected_status" class="form-control">
                                                <option value="All">All</option>
                                                <option value="Active">Active</option>
                                                <option value="Deleted">Deleted</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </form>
                        <datatable :dtOptions="dt_options" :dtHeaders="dt_headers" ref="campsite_type_table"
                            id="campsite-type-table"></datatable>
                    </div>
                </div>
            </div>
        </div>
        <confirmbox id="deleteCampsiteType" :options="deleteCampsiteTypePrompt"></confirmbox>
    </div>
</template>

<script setup>
import {
    $,
    api_endpoints,
    helpers,
    bus
}
    from '../../hooks.js';
import datatable from '../utils/datatable.vue'
import confirmbox from '../utils/confirmbox.vue'
import basePanelHeading from "../../layouts/base-panel-heading.vue";
import { onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter()

const selected_status = ref('All')
const campsite_type_table = ref(null)
const deleteCampsiteType = ref(null)
const deleteCampsiteTypePrompt = ref({
    icon: "<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
    message: "Are you sure you want to Delete this campsite type",
    buttons: [{
        text: "Delete",
        event: "delete",
        bsColor: "btn-danger",
        handler: function () {
            deleteCampsiteTypeRecord(deleteCampsiteType.value);
            deleteCampsiteType.value = null;
        },
        autoclose: true,
    }],
    id: 'deleteCampsiteType'
})
const dt_headers = ["Name", "Status", "Action"]
const dt_options = ref({
    language: {
        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
    },
    responsive: true,
    processing: true,
    columnDefs: [
        // { targets: [0,1,2], responsivePriority:1 },
        { "defaultContent": "-", "targets": "_all" },
        {
            responsivePriority: 1,
            targets: 0,
        },
        {
            responsivePriority: 2,
            targets: 1
        },
        {
            responsivePriority: 3,
            targets: 2
        }
    ],
    ajax: {
        "url": api_endpoints.campsite_classes,
        "dataSrc": ''
    },
    columns: [
        {
            "data": "name",
            mRender: function (data, type, full) {
                const max_length = 120;
                const popover_class = (data.length > max_length) ? "class='name_popover'" : "";
                const name = (data.length > max_length) ? data.substring(0, max_length - 1) + '...' : data;
                const column = '<td> <div ' + popover_class + 'tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__" >' + name + '</div></td>';
                return column.replace('__NAME__', data);
            }
        },
        {
            "data": "deleted",
            "mRender": function (data, type, full) {
                const status = (!data) ? "Active" : "Deleted";
                const column = "<td >__Status__</td>";
                return column.replace('__Status__', status);
            }
        },
        {
            "mRender": function (data, type, full) {
                var id = full.id;
                if (!full.deleted) {
                    var column = "<td ><a href='#' class=\"detailRoute\" data-campsite-type='__ID__'> Edit</a> </br> ";
                    column += "<a href='#' class=\"deleteCT\" data-campsite-type='__ID__'> Delete</a> </td>";
                    return column.replace(/__ID__/g, full.id);
                }
                return '';
            }
        }
    ]
})

watch(() => selected_status.value, (value) => {
    if (value) {
        campsite_type_table.value.vmDataTable.ajax.reload();
    }
})

const deleteCampsiteTypeRecord = function (id) {
    var url = api_endpoints.campsite_class(id);
    $.ajax({
        method: "DELETE",
        url: url,
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') }
    }).done(function (msg) {
        campsite_type_table.value.vmDataTable.ajax.reload();
    });
}
const goBack = function () {
    router.go(-1);
}
const attachTableEventListeners = function () {
    campsite_type_table.value.vmDataTable.on('click', '.detailRoute', function (e) {
        e.preventDefault();
        var id = $(this).data('campsite-type');
        router.push({
            name: 'campsite-type-detail',
            params: {
                campsite_type_id: id
            }
        });
    });
    campsite_type_table.value.vmDataTable.on('click', '.deleteCT', function (e) {
        e.preventDefault();
        var id = $(this).data('campsite-type');
        deleteCampsiteType.value = id;
        bus.emit('showAlert', 'deleteCampsiteType');
    });
}
onMounted(() => {
    helpers.namePopover($, campsite_type_table.value.vmDataTable);
    attachTableEventListeners();
})

</script>

<style lang="css">
.name_popover {
    padding: 10px;
    cursor: pointer;
}
</style>
