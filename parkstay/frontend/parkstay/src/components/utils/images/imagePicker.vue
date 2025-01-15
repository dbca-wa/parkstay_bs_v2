<template>
    <div class="row" imagePicker>
        <div class="form-group">
            <div class="col-sm-12">
                <span class="btn btn-primary btn-file btn-sm">
                    <i class="fa fa-fw fa-camera"></i><input multiple ref="imagePicker" type="file" name='img'  accept="image/*"
                        @change="readURL()" />
                    Add Image
                </span>
                <button class="btn btn-sm btn-danger" v-show="imagesLoaded" @click.prevent="clearImages">Clear
                    All</button>
            </div>
        </div>
        <div class="form-group">
            <loader :isLoading="addingImage">{{ imageLoaderText }}</loader>
            <div class="col-sm-12">
                <div v-show="!addingImage" class="col-sm-12">
                    <div class="upload">
                        <div v-for="(img, i) in images" class="panel panel-default">
                            <div class="overlay">
                                <button type="button" class="btn btn-danger btn-block" @click.prevent="removeImage(i)">
                                    Remove <i class="fa fa-w fa-trash-o"></i></button>
                            </div>
                            <div class="panel-body" :data-index='i'>
                                <img :src="img.image" class="img" alt="Responsive image" />
                                <div v-show="showCaption" class="panel-footer">
                                    <div class="row">
                                        <div class="col-lg-12">
                                            <div class="form-group">
                                                <input type="text" class="form-control" placeholder="Caption"
                                                    v-model="img.caption" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>

            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUpdated, onBeforeUnmount, computed } from 'vue';
import {
    $
}
    from '../../../hooks.js'
import {
    bus
}
    from '../eventBus.js'
import loader from '../loader.vue'

const props = defineProps({
    showCaption: {
        type: Boolean,
        default: false
    },
    images: {
        type: Array,
        required: true
    }
})
const imagePicker = ref(null)
const slide = ref(0)
const addingImage = ref(false)
const imageLoaderText = ref('')
const slickCaro = ref(null)
const slick_options = ref({
    dots: true,
    infinite: true,
    speed: 300,
    adaptiveHeight: true,
    slidesToShow: 4,
    slidesToScroll: 4,
    responsive: [{
        breakpoint: 1024,
        settings: {
            slidesToShow: 3,
            slidesToScroll: 3,
            infinite: false,
            dots: true
        }
    }, {
        breakpoint: 600,
        settings: {
            slidesToShow: 2,
            slidesToScroll: 2
        }
    }, {
        breakpoint: 480,
        settings: {
            slidesToShow: 1,
            slidesToScroll: 1
        }
    }]

})

onMounted(function () {
    slick_init();
    bus.on('campgroundFetched', function () {
        if (props.images) {
            $('.upload').slick('unslick');
            imageLoaderText.value = 'Loading Images...'
            addingImage.value = true;
            slick_refresh();
        }
    });
    slide.value = props.images.length;
})

const removeImage = function (i) {
    imageLoaderText.value = 'Loading Images...'
    addingImage.value = true;
    props.images.splice(i, 1);
    $('.upload').slick('unslick');
    slick_refresh();
}

const showRemove = function () {
    var el = $('div[data-index]');
    $(el).on('mouseover', function (e) {
        $(this).siblings('.overlay').addClass('show').on('mouseleave', function (el) {
            $(this).removeClass('show');
        });
    });
}
const clearImages = function () {

    imageLoaderText.value = 'Removing Images...'
    addingImage.value = true;
    props.images.splice(0, props.images.length);
    $('.upload').slick('unslick');
    slick_refresh();
}
const slick_init = function () {
    slickCaro.value = $('.upload').not('.slick-initialized').slick(slick_options.value);
}
const slick_refresh = function () {
    setTimeout(function () {
        slick_init();
    }, 100);
    setTimeout(function () {
        addingImage.value = false;
        $('.upload').slick('resize');
    }, 400);
}
const readURL = function () {
    $('.upload').slick('unslick');
    addingImage.value = true;
    var input = imagePicker.value;
    if (input.files && input.files[0]) {
        input.files.length > 1 ? imageLoaderText.value = 'Adding Images...' : imageLoaderText.value = 'Adding Image...';
        for (var i = 0; i < input.files.length; i++) {
            var reader = new FileReader();
            reader.onload = function (e) {
                slide.value++
                props.images.push({
                    image: e.target.result,
                    caption: ''
                });
            };
            reader.readAsDataURL(input.files[i]);
        }
        $(input).val("");
        slick_refresh();
    }
}

const imagesLoaded = computed(function () {
    return props.images && props.images.length > 1
})

onUpdated(function () {
    showRemove();
})

</script>

<style lang="css">
.upload .panel {
    box-shadow: 0 1px 6px 0 rgba(0, 0, 0, 0.12), 0 1px 6px 0 rgba(0, 0, 0, 0.12);
    border-radius: 2px;
    margin-right: 5px;
}

.upload img {
    height: 250px;
    width: 250px;
}

.btn-file {
    position: relative;
    width: 120px;
    overflow: hidden;
}

.btn-file-large {
    position: relative;
    overflow: hidden;
    width: 120px;
    height: 96px;
    /*font-size: 45px;*/
}

.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}

.slick-prev {
    left: 10px;
    color: #012531;
}

.slick-next {
    right: 10px;
    color: #012531;
}


/* Slider */
.slick-loading .slick-list {
    /* background: #fff url('./ajax-loader.gif') center center no-repeat; */
}

/* Arrows */
.slick-prev,
.slick-next {
    font-size: 0;
    line-height: 0;

    position: absolute;
    top: 50%;

    display: block;

    width: 20px;
    height: 20px;
    margin-top: -10px;
    padding: 0;

    cursor: pointer;

    color: transparent;
    border: none;
    outline: none;
    background: #337ab7;
}

.slick-prev:hover,
.slick-prev:focus,
.slick-next:hover,
.slick-next:focus {
    color: transparent;
    outline: none;
    background: #337ab7;
}

.slick-prev:hover:before,
.slick-prev:focus:before,
.slick-next:hover:before,
.slick-next:focus:before {
    opacity: 1;
}

.slick-prev.slick-disabled:before,
.slick-next.slick-disabled:before {
    opacity: .11;
}

.slick-prev:before,
.slick-next:before {
    font: normal normal normal 14px/1 FontAwesome;
    text-rendering: auto;
    font-size: 20px;
    line-height: 1;

    opacity: .75;
    color: white;

    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

[dir='rtl'] .slick-prev {
    right: -11px;
    left: auto;
}

.slick-prev:before {
    content: '\f0a8';
}

[dir='rtl'] .slick-prev:before {
    content: '\f0a8';
}

[dir='rtl'] .slick-next {
    right: auto;
    left: -11px;
}

.slick-next:before {
    content: '\f0a9';
}

[dir='rtl'] .slick-next:before {
    content: '\f0a9';
}

/* Dots */
.slick-slider {
    margin-bottom: 30px;
}

.slick-dots {
    position: absolute;
    bottom: -45px;

    display: block;

    width: 100%;
    padding: 0;

    list-style: none;

    text-align: center;
}

.slick-dots li {
    position: relative;

    display: inline-block;

    width: 20px;
    height: 20px;
    margin: 0 5px;
    padding: 0;

    cursor: pointer;
}

.slick-dots li button {
    font-size: 0;
    line-height: 0;

    display: block;

    width: 20px;
    height: 20px;
    padding: 5px;

    cursor: pointer;

    color: transparent;
    ;
    border: 0;
    outline: none;
    background: transparent;
}

.slick-dots li button:hover,
.slick-dots li button:focus {
    outline: none;
}

.slick-dots li button:hover:before,
.slick-dots li button:focus:before {
    opacity: 1;
}

.slick-dots li button:before {
    font: normal normal normal 14px/1 FontAwesome;
    font-size: 12px;
    line-height: 20px;

    position: absolute;
    top: 0;
    left: 0;

    width: 20px;
    height: 20px;

    content: '\f111';
    text-align: center;

    opacity: .25;
    color: #337ab7;

    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.slick-dots li.slick-active button:before {
    opacity: 1;
    color: #337ab7;
}

.panel-group .panel+.panel {
    margin-top: 0;
    z-index: 0;
    cursor: pointer;
}

.overlay {
    position: absolute;
    top: 0px;
    height: 100%;
    width: inherit;
    background-color: rgba(51, 122, 183, 0.4);
    z-index: 1;
    overflow: hidden;
    display: flex !important;
    flex-direction: row;
    justify-content: center;
    flex-wrap: nowrap;
    align-items: center;
    visibility: hidden;
    cursor: pointer;
}

.show {
    visibility: visible;
    transition: visibility 1000s linear 0s;
}
</style>
