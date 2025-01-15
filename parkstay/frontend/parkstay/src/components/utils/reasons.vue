<template lang="html">
    <div class="row" id="reasons">
        <div class="form-group">
            <div v-bind:class="{ 'col-md-4': large, 'col-md-2': !large }">
                <label>Reason: </label>
            </div>
            <div v-bind:class="{ 'col-md-8': large, 'col-md-4': !large }">
                <select v-if="!reasons.length > 0" class="form-control form-select">
                    <option value="">Loading...</option>
                </select>
                <select v-else name="open_reason" v-model="model"
                    class="form-control form-select">
                    <option value=""></option>
                    <option v-for="reason in reasons" :value="reason.id">{{ reason.text }}</option>
                </select>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import {
    $, api_endpoints
} from '../../hooks.js'

const props = defineProps({
    type: {
        required: true
    },
    large: {
        default: false
    }
})

const model = defineModel()

const reasons = ref([])

const fetchClosureReasons = function () {
    $.get(api_endpoints.closureReasons(), function (data) {
        reasons.value = data;
    });
}
const fetchMaxStayReasons = function () {
    $.get(api_endpoints.maxStayReasons(), function (data) {
        reasons.value = data;
    });
}
const fetchPriceReasons = function () {
    $.get(api_endpoints.priceReasons(), function (data) {
        reasons.value = data;
    });
}
const fetchDiscountReasons = function () {
    $.get(api_endpoints.discountReasons(), function (data) {
        reasons.value = data;
    });

}

onMounted(function () {
    if (props.type) {
        switch (props.type.toLowerCase()) {
            case 'close':
                fetchClosureReasons();
                break;
            case 'stay':
                fetchMaxStayReasons();
                break;
            case 'price':
                fetchPriceReasons();
                break;
            case 'discount':
                fetchDiscountReasons();
        }
    }
})
</script>

<style lang="css"></style>
