<template>
    <div>
        <Carousel ref="carousel" v-bind="carouselSettings" :breakpoints="breakpoints" @slide-start="handleSlideStart">
            <Slide v-for="(slide, index) in slides" :key="index">
                <div>
                    <div class='row' v-for="campground in slide" :key="campground.id">
                        <div class='carousel-slide-card'>
                            <div class='row'>
                                <div class='col-xs-12 col-sm-6'>
                                    <div v-if="campground.images && campground.images[0] && campground.images[0].image">
                                        <img class="slider-card-thumbnail"
                                            v-bind:src="parkstayUrl + '/campground-image-cropped-square/250/400/?mediafile=' + campground.images[0].image" />
                                    </div>
                                </div>
                                <div class='col-xs-12 col-sm-6'>
                                    <div>
                                        <div class="carousel-slide-card-title" :title="campground.campground_name"
                                            :alt="campground.campground_name">
                                            {{ campground.campground_name }}
                                        </div>
                                        <div class="carousel-slide-card-distance"
                                            title="Distance from selected location"
                                            alt="Distance from selected location">
                                            {{ campground.distance_short }}km&nbsp;
                                            <i class="bi bi-info-circle-fill distance-info-icon"
                                                data-bs-toggle="tooltip" data-bs-placement="right"
                                                data-bs-title="Straight-line distance from searched place."></i>
                                        </div>
                                    </div>

                                    <div>

                                        <div v-if="campground.park_name" v-html="campground.park_name.slice(0, 55)"
                                            class='carousel-slide-description'>
                                        </div>
                                        <div class='carousel-slide-card-notavailabile'
                                            v-if="!!!campground.filters_match">
                                            Does not match filters
                                        </div>
                                        <div v-else-if="campground.campground_type == 0">
                                            <div v-if="booking_arrival_days > campground.max_advance_booking && permission_to_make_advanced_booking == false"
                                                class='carousel-slide-card-notavailabile'>
                                                Book up to {{ campground.max_advance_booking }} days
                                            </div>
                                            <div v-else>
                                                <div v-if="campgroundAvailablity[campground.id].total_bookable > 0"
                                                    class='carousel-slide-card-availabile'>&nbsp;
                                                </div>
                                                <div v-else class='carousel-slide-card-notavailabile'>
                                                    No/limited availability!
                                                </div>
                                            </div>
                                        </div>
                                        <div class='carousel-slide-card-notavailabile'
                                            v-else-if="campground.campground_type == 1">
                                            No bookings
                                        </div>
                                        <div class='carousel-slide-card-notavailabile'
                                            v-else-if="campground.campground_type == 2">
                                            Partner-operated facility
                                        </div>

                                        <div class='carousel-slide-card-notavailabile'
                                            v-else-if="campground.campground_type == 4">
                                            Booking by application
                                        </div>
                                        
                                        
                                        <div v-else>
                                            <div>&nbsp;</div>
                                        </div>
                                        <p v-if="campground.price_hint && Number(campground.price_hint)"><i><small>From
                                                    ${{
                                                        campground.price_hint
                                                    }} per night</small></i></p>

                                        <a v-if="campground.campground_type == 0 && (booking_arrival_days <= campground.max_advance_booking || permission_to_make_advanced_booking == true)"
                                            :class="{
                                                'button': true,
                                                'formButton1': campgroundAvailablity[campground.id].total_bookable > 0,
                                                'formButton4': campgroundAvailablity[campground.id].total_bookable == 0,
                                                'formButton5': !!!campground.filters_match
                                            }"
                                            style="width:100%;"
                                            v-bind:href="parkstayUrl + '/search-availability/campground/?site_id=' + campground.id + '&' + bookingParam"
                                            target="_self">{{!!!campground.filters_match ? 'More information' : 'See availability' }}</a>
                                        <a v-else-if="campground.campground_type == 1 || campground.campground_type == 4"
                                            :class="{'button':true, 'formButton': !!campground.filters_match,'formButton5': !!!campground.filters_match}" style="width:100%;"
                                            v-bind:href="parkstayUrl + '/search-availability/campground/?site_id=' + campground.id + '&' + bookingParam"
                                            target="_self">More information</a>
                                        <a v-else :class="{'button':true, 'formButton2': !!campground.filters_match,'formButton5': !!!campground.filters_match}"
                                            v-bind:href="parkstayUrl + '/search-availability/campground/?site_id=' + campground.id + '&' + bookingParam"
                                            style="width:100%;" target="_self">More information<i
                                                class="bi bi-box-arrow-up-right ms-2"></i> </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </Slide>

            <template #addons="{ slidesCount }">
                <navigation>
                    <template #next>
                        <img src="@assets/chevron-right.svg" alt="Next" />
                    </template>
                    <template #prev>
                        <img src="@assets/chevron-left.svg" alt="Prev" />

                    </template>
                </navigation>
            </template>
        </Carousel>
    </div>
</template>

<script>
import { Carousel, Navigation, Slide } from 'vue3-carousel'
import 'vue3-carousel/dist/carousel.css'

const CAMPGROUND_REUSULT_LIMIT = 21;

export default {
    name: 'SearchCarousel',
    components: {
        Carousel,
        Slide,
        Navigation
    },
    data() {
        return {
            carouselSettings: {
                itemsToShow: 1,
                snapAlign: 'center',
                wrapAround: false,
                transition: 500
            },
            slideNumRows: 3,
            breakpoints: {
                // 1150 and up
                1150: {
                    itemsToShow: 2,
                    snapAlign: 'start',
                },
                // 800px and up
                800: {
                    itemsToShow: 1,
                    snapAlign: 'center',
                },
                480: {
                    itemsToShow: 1,
                    snapAlign: 'center',
                },

            },
        };
    },
    props: {
        camping_distance_array: {
            type: Array,
            default: []
        },
        parkstayUrl: {
            type: String,
            default: ''
        },
        booking_arrival_days: {
            type: Number,
            default: 0
        },
        permission_to_make_advanced_booking: {
            type: Boolean,
            default: false
        },
        campgroundSiteTotal: {
            type: Object,
            default: {}
        },
        campgroundAvailablity: {
            type: Object,
            default: {}
        },
        bookingParam: {
            type: String,
            default: ''
        }
    },
    computed: {
        slides() {
            const result = [];
            const campgrounds = this.camping_distance_array.slice(0, CAMPGROUND_REUSULT_LIMIT);
            for (let i = 0; i < campgrounds.length; i += this.slideNumRows) {
                result.push(campgrounds.slice(i, i + this.slideNumRows));
            }
            return result;
        }
    },
    watch: {
        slides() {
            if (this.$refs.carousel) {
                this.$refs.carousel.slideTo(0)
                this.$refs.carousel.updateSlideWidth()
            }
            this.$nextTick(() => {

                const tooltipTriggerList = document.querySelectorAll('.carousel-slide-card [data-bs-toggle="tooltip"]')
                const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => bootstrap.Tooltip.getOrCreateInstance(tooltipTriggerEl))
            })
        }
    },
    methods: {
        adjustCarouselRows() {
            let windowWidth = window.innerWidth;
            let shouldResetCarousel = false;
            if (windowWidth < 800) {
                shouldResetCarousel = this.slideNumRows !== 1;
                this.slideNumRows = 1;
            } else {
                shouldResetCarousel = this.slideNumRows !== 3;
                this.slideNumRows = 3;
            }
            if (shouldResetCarousel && this.$refs.carousel) {
                this.$refs.carousel.slideTo(0)
            }
            this.$refs.carousel.updateSlidesData()
        },
        handleSlideStart() {
            // hack to fix faulty behaviour.
            if (this.$refs.carousel) {
                this.$refs.carousel.updateSlideWidth()
            }
        }
    }
    ,
    mounted: function () {
        this.adjustCarouselRows();
        window.addEventListener('resize', this.adjustCarouselRows);
    }

    ,
    unmounted: function () {
        document.removeEventListener('resize', () => { });
    }
};
</script>

<style lang="scss">
.carousel-slide-card {
    max-width: 490px;
    min-height: 220px;
    background-color: #FFFFFF;
    margin-right: 20px;
    padding: 10px;
    padding-right: 22px;
    border: 1px solid #eaeaea;
    border-radius: 5px;
    margin-bottom: 10px;
    margin: auto;
    text-align: left;
}

.carousel-slide-card-title {
    font-size: 15px;
    font-weight: bold;
    height: 25px;
    text-wrap: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
}

.carousel-slide-card-distance {
    font-size: 11px;
    height: 22px;
}

.carousel-slide-description {
    height: 94px;
    font-size: 12px;
}

.carousel-slide-card-availabile {
    font-size: 11px;
    height: 22px;
}

.carousel-slide-card-notavailabile {
    font-size: 10.5px;
    height: 22px;
    color: red;
}

.carousel-slide-noavailable-sites {
    color: red;
}

.slider-card-thumbnail {
    width: 100%;
}

.carousel {

    .carousel__slide {
        align-items: start;
    }

    .carousel__prev.carousel__prev--disabled,
    .carousel__next.carousel__next--disabled,
    .carousel__prev.carousel__prev--disabled:hover,
    .carousel__next.carousel__next--disabled:hover {
        opacity: 0.30;
    }

    .carousel__prev,
    .carousel__next {
        opacity: 0.75;
        background: black;
        height: 52px;
        border-radius: 30px !important;
        width: 52px;

    }

    .carousel__prev:hover,
    .carousel__next:hover {
        opacity: 0.85;
    }

    .carousel__prev {
        z-index: 1000;
        left: 10px;
        color: #012531;
        padding: 7px;
        padding-left: 0px;
    }

    .carousel__next {
        z-index: 10;
        right: 10px;
        color: #012531;
        padding: 7px;
        padding-right: 0px;
    }

    .distance-info-icon {
        color: #0081df;
    }
}

[v-cloak] {
    display: none;
}

@font-face {
    font-family: "DPaWSymbols";
    src: url("../../assets/campicon.woff") format("woff");
}

.symb {
    font-family: "DPaWSymbols";
    font-style: normal;
    font-size: 1.5rem;
}

.symb.RC2:before {
    content: "a";
}

.symb.RC4:before {
    content: "b";
}

.symb.RV10:before {
    content: "c";
}

.symb.RG2:before {
    content: "d";
}

.symb.RG15:before {
    content: "e";
}

.symb.RV2:before {
    content: "f";
}

.symb.RF10:before {
    content: "g";
}

.symb.RF13:before {
    content: "h";
}

.symb.RF15:before {
    content: "i";
}

.symb.RF17:before {
    content: "j";
}

.symb.RF1:before {
    content: "k";
}

.symb.RF6:before {
    content: "l";
}

.symb.RF7:before {
    content: "m";
}

.symb.RF19:before {
    content: "n";
}

.symb.RF8G:before {
    content: "o";
}

.symb.RC1:before {
    content: "p";
}

.symb.RC3:before {
    content: "q";
}

.symb.LOC:before {
    content: "r";
}

.symb.RW3:before {
    content: "s";
}

.symb.MAINS:before {
    content: "t";
}

.f6inject {

    .search-params hr {
        margin: 0;
    }

    .search-params label {
        cursor: pointer;
        font-size: 0.8em;
    }

    /* filter hiding on small screens */
    @media print,
    screen and (max-width: 63.9375em) {
        .filter-hide {
            display: none;
        }
    }

    @media print,
    screen and (min-width: 64em) {
        .filter-button {
            display: none;
        }
    }

    #map {
        height: 75vh;
    }

    /* set on the #map element when mousing over a feature */
    .click {
        cursor: pointer;
    }

    input+.symb {
        color: #000000;
        transition: color 0.25s ease-out;
    }

    input:checked+.symb {
        color: #2199e8;
    }

    .button.formButton1,
    .button.formButton1:hover {
        background-color: green;
    }

    .button.formButton,
    .button.formButton1,
    .button.formButton2,
    .button.formButton5,
    .button.formButton4 {
        display: block;
        width: 100%;
    }

    .button.formButton2,
    .button.formButton2:hover {
        background-color: purple;
    }

    .button.formButton4,
    .button.formButton4:hover {
        background-color: #bb1010;
    }

    .button.formButton5,
    .button.formButton5:hover {
        background-color: #717070;
    }

    .button.selector {
        background-color: #fff;
        border: 1px solid #777;
        border-radius: 4px;
        color: #000;
    }

    .button.selector:hover {
        background-color: #d6eaff;
        border: 1px solid #729fcf;
    }

    .button.selector~input:checked {
        color: #fff;
        background-color: #0060c4;
        border: 1px solid #00366e;
    }

    .button.selector:hover~input:checked {
        color: #fff;
        background-color: #0e83ff;
        border: 1px solid #004d9f;
    }

    .pagination {
        padding: 0;
        text-align: center;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 1em;
    }

    .pagination .active {
        background: #2199e8;
        color: #fefefe;
        cursor: default;
    }

    .pagination li {
        display: inline-block;
        cursor: pointer;
    }

    .tooltip {
        position: relative;
        border-radius: 4px;
        background-color: #ffcc33;
        color: black;
        padding: 4px 8px;
        opacity: 0.7;
        white-space: nowrap;
    }

    .tooltip:before {
        border-top: 6px solid rgba(0, 0, 0, 0.5);
        border-right: 6px solid transparent;
        border-left: 6px solid transparent;
        content: "";
        position: absolute;
        bottom: -6px;
        margin-left: -7px;
        left: 50%;
    }


    .searchTitle {
        font-size: 150%;
        font-weight: bold;
    }

    .resultList {
        padding: 0;
    }
}

/* hacks to make awesomeplete play nice with F6 */
div.awesomplete {
    display: block;
}

div.awesomplete>input {
    display: table-cell;
}
</style>