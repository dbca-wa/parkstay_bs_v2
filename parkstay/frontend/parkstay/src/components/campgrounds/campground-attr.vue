<template lang="html">
    <div id="cg_attr">
        <div v-show="!isLoading">
            <form id="attForm">
                <div class="col-sm-12">
                    <alert v-model:show="showUpdate" type="success" :duration="7000">
                        <p>Campground successfully updated</p>
                    </alert>
                    <alert v-model:show="showError" type="danger" :dismissable="true">
                        <p>{{ errorString }}</p>
                    </alert>
                    <div class="row">
                        <div class="col-lg-12">
                            <div class="panel panel-primary">
                                <div class="panel-heading">
                                    <h5 class="panel-title">Info</h5>
                                </div>
                                <div id="main-panel" class="panel-body">
                                    <div class="row">
                                        <div class="col-md-10 col-lg-12">

                                            <div class="row">
                                                <div class="col-md-6 col-lg-6">
                                                    <div class="form-group">
                                                        <label class="control-label">Campground Name</label>
                                                        <input autofocus="true" type="text" name="name" id="name"
                                                            class="form-control" v-model="campground.name" required />
                                                    </div>
                                                </div>
                                                <div class="col-md-4 col-lg-3">
                                                    <div class="form-group">
                                                        <label class="control-label">Oracle Code</label>
                                                        <input type="text" name="oracle_code" id="oracle_code"
                                                            class="form-control" v-model="campground.oracle_code"
                                                            required />
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-md-10 col-lg-6">
                                                    <div class="form-group ">
                                                        <label class="control-label">Park</label>
                                                        <select name="park" v-show="!parks.length > 0"
                                                            class="form-control">
                                                            <option>Loading...</option>
                                                        </select>
                                                        <select name="park" v-if="parks.length > 0"
                                                            class="form-control form-select" v-model="campground.park">
                                                            <option v-for="park in parks" :value="park.id">{{ park.name
                                                                }}
                                                            </option>
                                                        </select>
                                                    </div>
                                                </div>
                                            </div>

                                            <div class="row">
                                                <div class="col-md-6 col-lg-3">
                                                    <div class="form-group ">
                                                        <label class="control-label">Type</label>
                                                        <select id="campground_type" name="campground_type"
                                                            class="form-control form-select"
                                                            v-model="campground.campground_type">
                                                            <option value="0">Bookable Online</option>
                                                            <option value="1">Not Bookable Online</option>
                                                            <option value="2">Other accomodation</option>
                                                            <option value="3">Unpublished</option>
                                                        </select>
                                                    </div>
                                                </div>
                                                <div class="col-md-4 col-lg-3">
                                                    <div class="form-group ">
                                                        <label class="control-label">Booking Configuration</label>
                                                        <select id="site_type" name="site_type"
                                                            class="form-control form-select"
                                                            v-model="campground.site_type">
                                                            <option value="0">Bookable per site</option>
                                                            <option value="1">Bookable per site type</option>
                                                            <option value="2">Bookable per site type (hide site number)
                                                            </option>
                                                        </select>
                                                    </div>
                                                </div>
                                                <div class="col-md-4 col-lg-3">
                                                    <label class="control-label">Price set at: </label>
                                                    <select id="price_level" name="price_level"
                                                        class="form-control form-select"
                                                        v-model="campground.price_level">
                                                        <option v-for="level in priceSet" :value="level.val">{{
                                                            level.name }}</option>
                                                    </select>

                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <h5 class="panel-title">Campground Images</h5>

                                        <div class="col-lg-12" style="padding-top: 20px;">
                                            <imagePicker :images="campground.images"></imagePicker>
                                        </div>
                                    </div>
                                    <hr />
                                    <div class="row">
                                        <div class="col-lg-12">
                                            <div class="panel panel-primary">
                                                <div class="panel-heading">
                                                    <h5 class="panel-title">Contact</h5>
                                                </div>
                                                <div class="panel-body">
                                                    <div class="row">
                                                        <div class="form-group">
                                                            <label class="col-md-4 control-label">Customer
                                                                Contact</label>
                                                            <div class="col-md-8">
                                                                <select class="form-control form-select" name="contact"
                                                                    v-model="campground.contact">
                                                                    <option value="undefined">Select Contact</option>
                                                                    <option v-for="c in contacts" :value="c.id">{{
                                                                        c.name }}</option>
                                                                </select>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div class="row">
                                                        <div class="col-md-3">
                                                            <label class="control-label">Phone Number</label>
                                                            <input type="text" disabled name="contact_number"
                                                                id="contact_number" class="form-control"
                                                                v-model="selected_contact_number" required />
                                                        </div>
                                                        <div class="col-md-5">
                                                            <label class="control-label">Email</label>
                                                            <input type="text" disabled name="contact_email"
                                                                id="contact_email" class="form-control"
                                                                v-model="selected_contact_email" required />
                                                        </div>

                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-6 col-lg-4 features">
                                            <div class="panel panel-primary">
                                                <div class="panel-heading">
                                                    <h5 class="panel-title">Features</h5>
                                                </div>
                                                <div class="panel-body"
                                                    v-bind:class="{ 'empty-features': allFeaturesSelected }">
                                                    <p v-show="allFeaturesSelected">
                                                        All features selected
                                                    </p>
                                                    <ul class="list-group">
                                                        <a href="" v-for="feature, key in features"
                                                            @click.prevent="addSelectedFeature(feature, key)"
                                                            class="list-group-item list-group-item-primary">{{
                                                                feature.name }}</a>
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-sm-6 col-lg-4 features">
                                            <div class="panel panel-primary">
                                                <div class="panel-heading">
                                                    <h5 class="panel-title">Selected</h5>
                                                </div>
                                                <div class="panel-body"
                                                    v-bind:class="{ 'empty-features': !hasSelectedFeatures }">
                                                    <p v-show="!hasSelectedFeatures">
                                                        No features selected
                                                    </p>
                                                    <ul class="list-group">
                                                        <a href="" v-for="feature, key in selected_features"
                                                            @click.prevent="removeSelectedFeature(feature, key)"
                                                            class="list-group-item ">{{ feature.name }}</a>
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <h4>Additional information</h4>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-12">
                                            <div class="form-group">
                                                <label class="control-label">Description</label>
                                                <div id="editor" class="form-control"></div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-12">
                                            <div class="form-group">
                                                <label class="control-label">Additional confirmation information</label>
                                                <textarea id="additional_info" class="form-control"
                                                    v-model="campground.additional_info" />
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <div class="form-group pull-right">
                                                <a href="#" v-if="createCampground" class="btn btn-primary me-2"
                                                    @click.prevent="create">Create Campground</a>
                                                <a href="#" v-else class="btn btn-primary"
                                                    @click.prevent="update">Update Campground</a>
                                                <a href="#" class="btn btn-default" @click.prevent="goBack">Cancel</a>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                            </div>
                        </div>
                    </div>
                </div>

            </form>
        </div>
        <loader v-model:isLoading="isLoading">Loading...</loader>
    </div>
</template>

<script setup>
import {
    $,
    api_endpoints,
    helpers
}
    from '../../hooks.js'
import {
    bus
}
    from '../utils/eventBus.js';
import imagePicker from '../utils/images/imagePicker.vue'
import "quill/dist/quill.snow.css";
import Editor from 'quill';
import loader from '../utils/loader.vue'
import alert from '../utils/alert.vue'
import { mapGetters } from 'vuex'
import { computed, onMounted, onUpdated, ref, toRefs, watch } from 'vue';
import { useStore } from "../../apps/store.js";
import { useRouter } from 'vue-router';

const router = useRouter()
const store = useStore()
const props = defineProps({
    createCampground: { type: Boolean, default: true },
    priceSet: {
        type: Array,
        default: () => [{
            'val': 0,
            name: 'Campground level'
        }, {
            'val': 1,
            name: 'Campsite Type level'
        }, {
            'val': 2,
            name: 'Campsite level'
        }]
    },
    campground: {
        type: Object,
        default: ()=> ({
            address: {},
            images: []
        })
    },

})

const { campground, createCampground, priceSet } = toRefs(props)

let editor = null
const editor_updated = ref(false)
const features = ref([])
const selected_features = ref([])
const form = ref(null)
const errors = ref(false)
const errorString = ref('')
const showUpdate = ref(false)
const isLoading = ref(false)
const contacts = ref([])

const showError = computed(function () {
    return errors.value;
})
const hasSelectedFeatures = computed(function () {
    return selected_features.value.length > 0;
})
const allFeaturesSelected = computed(function () {
    return features.value.length < 1;
})
const selected_contact_number = computed(function () {
    let id = campground.value.contact;
    if (id != null) {
        let contact = contacts.value.find(contact => contact.id === id);
        return contact ? contact.phone_number : '';
    }
    else {
        return '';
    }
})
const selected_contact_email = computed(function () {
    let id = campground.value.contact;
    if (id != null) {
        let contact = contacts.value.find(contact => contact.id === id);
        return contact ? contact.email : '';
    }
    else {
        return '';
    }
})
const parks = computed(() => store.getters.parks)

watch(() => campground.value, function () {
    loadSelectedFeatures();
}, { deep: true })

const goBack = function () {
    router.go(-1);
}
const validateForm = function () {
    var isValid = validateEditor($('#editor'));
    return form.value.valid() && isValid;
}
const create = function () {
    if (validateForm()) {
        sendData(api_endpoints.campgrounds, 'POST');
    }
}
const update = function () {
    if (validateForm()) {
        sendData(api_endpoints.campground(campground.value.id), 'PUT');
    }
}
const validateEditor = function (el) {

    if (el.parents('.form-group').hasClass('has-error')) {
        el.tooltip("destroy");
        el.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
    }
    if (editor.getText().trim().length == 0) {
        // add or update tooltips
        el.tooltip({
            trigger: "focus"
        })
            .attr("data-original-title", 'Description is required')
            .parents('.form-group').addClass('has-error');
        return false;
    }
    return true;
}
const sendData = function (url, method) {
    isLoading.value = true;
    var featuresURL = new Array();
    var temp_features = selected_features.value;
    if (createCampground.value) {
        campground.value.features = selected_features.value;
    }
    campground.value.features.forEach(function (f) {
        featuresURL.push(f.id);
    });
    campground.value.features = featuresURL;
    if (campground.value.contact == "undefined") {
        campground.value.contact = '';
    }
    $.ajax({
        beforeSend: function (xhrObj) {
            xhrObj.setRequestHeader("Content-Type", "application/json");
            xhrObj.setRequestHeader("Accept", "application/json");
        },
        url: url,
        method: method,
        xhrFields: {
            withCredentials: true
        },
        data: JSON.stringify(campground.value),
        headers: { 'X-CSRFToken': helpers.getCookie('csrftoken') },
        contentType: "application/x-www-form-urlencoded",
        dataType: 'json',
        success: function (data, stat, xhr) {
            if (method == 'POST') {
                router.push({
                    name: 'cg_detail',
                    params: {
                        id: data.id
                    }
                });
                isLoading.value = false;
            }
            else if (method == 'PUT') {
                campground.value.features = temp_features;
                showUpdate.value = true;
                isLoading.value = false
            }
            store.dispatch("updateAlert", {
                visible: false,
                type: "danger",
                message: ""
            });
        },
        error: function (resp) {
            isLoading.value = false
            errorString.value = helpers.apiError(resp)
            errors.value = true
        }
    });
}
const showAlert = function () {
    bus.emit('showAlert', 'alert1');
}
const loadParks = function () {
    if (parks.value.length == 0) {
        store.dispatch("fetchParks");
    }

}
const loadFeatures = function () {
    var url = api_endpoints.features;
    $.ajax({
        url: url,
        dataType: 'json',
        success: function (data, stat, xhr) {
            features.value = data;
        }
    });
}
const addSelectedFeature = function (feature, key) {
    selected_features.value.push(feature);
    features.value.splice(key, 1);
    selected_features.value.sort(function (a, b) {
        return parseInt(a.id) - parseInt(b.id)
    });
}
const removeSelectedFeature = function (feature, key) {
    features.value.push(feature);
    selected_features.value.splice(key, 1);
    features.value.sort(function (a, b) {
        return parseInt(a.id) - parseInt(b.id)
    });
}
const addFormValidations = function () {
    form.value.validate({
        ignore: 'div.ql-editor',
        rules: {
            name: "required",
            park: "required",
            campground_type: "required",
            site_type: "required",
            street: "required",
            email: {
                required: true,
                email: true
            },
            telephone: "required",
            postcode: "required",
            price_level: "required"
        },
        messages: {
            name: "Enter a campground name",
            park: "Select a park from the options",
            campground_type: "Select a campground type from the options",
            site_type: "Select a site type from the options",
            price_level: "Select a price level from the options"
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
const loadSelectedFeatures = function () {
    if (campground.value.features) {
        if (!createCampground.value) {
            selected_features.value = campground.value.features;
        }
        $.each(campground.value.features, function (i, cgfeature) {
            $.each(features.value, function (j, feat) {
                if (feat != null) {
                    if (cgfeature.id == feat.id) {
                        features.value.splice(j, 1);
                    }
                }
            })
        });
    }

}

onMounted(function () {
    loadParks();
    loadFeatures();
    editor = new Editor('#editor', {
        modules: {
            toolbar: true
        },
        theme: 'snow'
    });
    editor.clipboard.dangerouslyPasteHTML(0, campground.value.description, 'api');
    editor.on('text-change', function (delta, oldDelta, source) {
        var text = $('#editor >.ql-editor').html();
        campground.value.description = text;
        validateEditor($('#editor'));
    });

    form.value = $('#attForm');
    addFormValidations();
    fetch(api_endpoints.contacts).then((response) => response.json()).then(data => {
        contacts.value = data
    }).catch((error) => {
        console.log(error);
    })
})

onUpdated(function () {
    var changed = false;
    if (campground.value.description != null && editor_updated.value == false) {
        editor.clipboard.dangerouslyPasteHTML(0, campground.value.description, 'api');
        changed = true;
    }
    if (changed) {
        editor_updated.value = true;
    }
}
)

</script>

<style lang="css">
#main-panel.panel-body>.row {
    margin-top: 20px;
}

#editor {
    height: 200px;
}

.features>.panel>.panel-body {
    padding: 0;
    max-height: 300px;
    min-height: 300px;
    overflow: auto;
}

.features .list-group {
    margin-bottom: 0;
}

.features .list-group-item {
    border-radius: 0;
}

.list-group-item:last-child {
    border-bottom-left-radius: 5px;
    border-bottom-right-radius: 5px;
}

.empty-features {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 300px;
    color: #ccc;
    font-size: 2em;
}

.pagination {
    float: right !important;
}
</style>
