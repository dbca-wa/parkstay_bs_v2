<template lang="html">
    <div class="row" id="reasons">
        <div class="form-group">
            <div v-bind:class="{'col-md-4':large,'col-md-2':!large}">
                <label>Reason: </label>
            </div>
            <div v-bind:class="{'col-md-8':large,'col-md-4':!large}">
                <select v-if="!reasons.length > 0" class="form-control form-select" >
                    <option value="">Loading...</option>
                </select>
                <select v-else name="open_reason" :value="value" @change="$emit('input', $event.target.value)" class="form-control form-select">
                    <option value=""></option>
                    <option v-for="reason in reasons" :value="reason.id">{{reason.text}}</option>
                </select>
            </div>
        </div>
    </div>
</template>

<script>
import {
    $,
    api_endpoints,
    bus
}from '../../hooks.js'
export default {
    name:'reasons',
    data:function () {
        let vm =this;
        return {
            reasons:[]
        }
    },
    props:{
        type:{
            required:true
        },
        value:{

        },
        large:{
            default:function () {
                return false;
            }
        }
    },
    methods:{
        fetchClosureReasons:function () {
            let vm = this;
            $.get(api_endpoints.closureReasons(),function (data) {
                vm.reasons = data;
            });
        },
        fetchMaxStayReasons:function () {
            let vm = this;
            $.get(api_endpoints.maxStayReasons(),function (data) {
                vm.reasons = data;
            });
        },
        fetchPriceReasons:function () {
            let vm = this;
            $.get(api_endpoints.priceReasons(),function (data) {
                vm.reasons = data;
            });
        },
        fetchDiscountReasons:function (){
            let vm = this;
            $.get(api_endpoints.discountReasons(),function (data){
                vm.reasons = data;
            });

        }
    },
    mounted:function(){
        let vm =this;
        if (vm.type) {
            switch (vm.type.toLowerCase()) {
                case 'close':
                    vm.fetchClosureReasons();
                    break;
                case 'stay':
                    vm.fetchMaxStayReasons();
                    break;
                case 'price':
                    vm.fetchPriceReasons();
                    break;
                case 'discount':
                    vm.fetchDiscountReasons();
            }
        }
    }
}
</script>

<style lang="css">
</style>
