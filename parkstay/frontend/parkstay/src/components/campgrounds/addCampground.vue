<template lang="html" id="pkCGADD">
    <div class="panel-group" id="applications-accordion" role="tablist" aria-multiselectable="true">
        <div class="card p-3" id="applications">
            <div class="panel-heading" role="tab" id="applications-heading">
                <div class="panel-title">
                    <h3>New Campground</h3>
                </div>
            </div>
            <hr>
            <div id="applications-collapse" class="" role="tabpanel" aria-labelledby="applications-heading">
                <div class="panel-body">
                    <div class="col-lg-12">
                        <div class="row">
                            <div class="col-sm-12">
                            </div>
                            <campgroundAttr v-model:campground="campground" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<script setup>
import campgroundAttr from './campground-attr.vue'
import { ref } from 'vue'

const campground = ref({
    address: {},
    images: []
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
