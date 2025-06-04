import Awesomplete from 'awesomplete';
import { get as getProjection, fromLonLat as fromLonLat } from 'ol/proj.js';
import { getTopLeft, getWidth } from 'ol/extent.js';
import WMTS from 'ol/tilegrid/WMTS';
import layertitle from 'ol/layer/Tile';
import layervector from 'ol/layer/Vector';
import sourcevector from 'ol/source/Vector';
import sourcewmts from 'ol/source/WMTS';
import styleicon from 'ol/style/Icon';
import stylestyle from 'ol/style/Style';
import overlay from 'ol/Overlay';
import feature from 'ol/Feature';
import map from 'ol/Map';
import view from 'ol/View';
import controlzoom from 'ol/control/Zoom';
import controlscaleline from 'ol/control/ScaleLine';
import { defaults as defaults } from 'ol/interaction';
import geolocation from 'ol/Geolocation';
import point from 'ol/geom/Point';
import formatgeojson from 'ol/format/GeoJSON';
import collection from 'ol/Collection';

export default function (vm) {
    $('#map').html('');
    //vm.booking_arrival_days = search_avail.var.arrival_days;

    var features = $('#feature_json').val() ?? '"[]"';
    vm.filterList = JSON.parse(features);
    // {name: 'BBQ', symb: 'RF8G', key: 'bbq', 'remoteKey': ['BBQ']},
    console.log('Load init_mounted');

    // $(document).foundation();
    let ol = {
        proj: { getProjection: getProjection, fromLonLat },
        extent: {
            getTopLeft: getTopLeft,
            getWidth: getWidth,
        },
        tilegrid: { WMTS: WMTS },
        layer: { Tile: layertitle, Vector: layervector },
        source: { WMTS: sourcewmts, Vector: sourcevector },
        style: { Icon: styleicon, Style: stylestyle },
        Overlay: overlay,
        Feature: feature,
        Map: map,
        View: view,
        control: { Zoom: controlzoom, ScaleLine: controlscaleline },
        interaction: {
            defaults: defaults,
        },
        Geolocation: geolocation,
        geom: { Point: point },
        format: { GeoJSON: formatgeojson },
        Collection: collection,
    };
    vm.ol = ol;
    console.log('Loading map...');
    // vm.load_site_queue();

    var nowTemp = new Date();
    var now = moment
        .utc({
            year: nowTemp.getFullYear(),
            month: nowTemp.getMonth(),
            day: nowTemp.getDate(),
            hour: 0,
            minute: 0,
            second: 0,
        })
        .toDate();

    // Added this portion from availability to solve datepicker utc - issue

    var today = moment.utc().add(8, 'hours');
    today = moment.utc({
        year: today.year(),
        month: today.month(),
        day: today.date(),
    });

    var later = moment(today).add(-1, 'days');

    var search = document.getElementById('searchInput');
    var autocomplete = new Awesomplete(search);
    autocomplete.autoFirst = true;

    $.ajax({
        url: vm.parkstayUrl + '/api/search_suggest',
        dataType: 'json',
        success: function (response, stat, xhr) {
            vm.suggestions = response;
            $(search).on('awesomplete-selectcomplete', function (ev) {
                this.blur();
                //vm.search(ev.target.value);
            });

            autocomplete.list = response['features'].map(function (el) {
                return el['properties']['name'];
            });
        },
    });

    // wire up search box
    $(search)
        .on('blur', function (ev) {
            vm.search(ev.target.value);
        })
        .on('keypress', function (ev) {
            if (!ev) {
                ev = window.event;
            }
            // intercept enter keys
            var keyCode = ev.keyCode || ev.which;
            if (keyCode == '13') {
                this.blur();
                return false;
            }
        });

    $('.filter-features').on('click', function () {
        console.log('UPDATE FILTERS');
        vm.updateFilter();
        vm.groundsSource.loadSource();
        vm.buildDistanceArray();
    });

    $('.filter-featurescs').on('click', function () {
        console.log('UPDATE FILTERS');
        vm.updateFilter();
        vm.groundsSource.loadSource();
        vm.buildDistanceArray();
    });

    // generate WMTS tile grid
    vm.projection = ol.proj.getProjection('EPSG:3857');
    vm.projectionExtent = vm.projection.getExtent();
    var size = ol.extent.getWidth(vm.projectionExtent) / 256;
    vm.matrixSet = 'mercator';
    vm.resolutions = new Array(21);
    vm.matrixIds = new Array(21);
    for (var z = 0; z < 21; ++z) {
        // generate resolutions and matrixIds arrays for this WMTS
        vm.resolutions[z] = size / Math.pow(2, z);
        vm.matrixIds[z] = vm.matrixSet + ':' + z;
    }
    var tileGrid = new ol.tilegrid.WMTS({
        origin: ol.extent.getTopLeft(vm.projectionExtent),
        resolutions: vm.resolutions,
        matrixIds: vm.matrixIds,
    });

    vm.streets = new ol.layer.Tile({
        source: new ol.source.WMTS({
            url: 'https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts',
            format: 'image/png',
            layer: 'public:mapbox-streets',
            matrixSet: vm.matrixSet,
            projection: vm.projection,
            tileGrid: tileGrid,
        }),
    });

    vm.tenure = new ol.layer.Tile({
        opacity: 0.6,
        source: new ol.source.WMTS({
            url: 'https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts',
            format: 'image/png',
            layer: 'public:dbca_legislated_lands_and_waters',
            matrixSet: vm.matrixSet,
            projection: vm.projection,
            tileGrid: tileGrid,
        }),
    });

    vm.geojson = new ol.format.GeoJSON({
        featureProjection: 'EPSG:3857',
    });

    vm.groundsData = new ol.Collection();
    vm.groundsIds = new Set();
    vm.groundsFilter = new ol.Collection();
    $.ajax({
        url: vm.parkstayUrl + '/api/campground_map/?format=json',
        dataType: 'json',
        success: function (response, stat, xhr) {
            var features = vm.geojson.readFeatures(response);
            vm.campground_data = response.features;
            vm.groundsData.clear();
            vm.groundsData.extend(features);
            vm.groundsSource.loadSource();
        },
        error: function (error) {
            console.log(error);
        },
    });

    vm.groundsSource = new ol.source.Vector({
        features: vm.groundsFilter,
    });

    vm.groundsSource.loadSource = function (onSuccess) {
        // var urlBase = vm.parkstayUrl+'/api/campground_map_filter/?';
        var urlBase = vm.parkstayUrl + '/api/campground_availabilty_view/?';
        var params = { format: 'json' };
        var isCustom = false;
        var checkin = $('#checkin');
        var checkout = $('#checkout');

        if (checkin && checkout) {
            isCustom = true;
            var arrival = vm.arrivalDateString;

            if (arrival) {
                params.arrival = arrival;
            }

            var departure = vm.departureDateString;
            if (departure) {
                params.departure = vm.departureDateString;
            }

            // params.num_adult = vm.numAdults;
            // params.num_concessions = vm.numConcessions;
            // params.num_children = vm.numChildren;
            // params.num_infants = vm.numInfants;

            params.gear_type = vm.gearType;
            params.features = JSON.stringify(vm.features);
            params.featurescs = JSON.stringify(vm.featuresCs);
        }

        $.ajax({
            url: urlBase + $.param(params),
            success: function (response, stat, xhr) {
                vm.groundsIds.clear();
                if (response.hasOwnProperty('available_cg') == true) {
                    response['available_cg'].forEach(function (el) {
                        vm.groundsIds.add(el.id);
                    });
                }
                if (response.hasOwnProperty('campground_available') == true) {
                    vm.campgroundAvailablity = response['campground_available'];
                }
                vm.updateFilter();
                vm.buildDistanceArray();
                search_avail.focus_map()
            },
            dataType: 'json',
        });
    };

    function getOLIcon(vm, campgroundId, campgroundType, is_match) {
        let icon = is_match ? vm.sitesInPersonIcon : vm.sitesNoMatchIcon;
        switch (campgroundType) {
            case 0:
                const hasBookings =
                    vm.campgroundAvailablity[campgroundId].total_bookable > 0;
                icon = is_match
                    ? hasBookings
                        ? vm.sitesOnlineIcon
                        : vm.sitesOnlineNotAvailIcon
                    : vm.sitesNoMatchIcon;
                break;
            case 2:
                icon = is_match ? vm.sitesAltIcon : vm.sitesNoMatchIcon;
                break;
            default:
                break;
        }
        return new ol.style.Icon({
            src: icon,
            imgSize: [32, 32],
            snapToPixel: true,
            anchor: [0.5, 1.0],
            anchorXUnits: 'fraction',
            anchorYUnits: 'fraction',
        });
    }

    vm.grounds = new ol.layer.Vector({
        source: vm.groundsSource,
        style: function (feature) {
            var style = feature.get('style');
            const is_match = feature.get('match') ?? true;
            const campgroundType = feature.get('campground_type');
            const campgroundId = feature.getId();
            if (!style) {
                style = new ol.style.Style({
                    image: getOLIcon(
                        vm,
                        campgroundId,
                        campgroundType,
                        is_match
                    ),
                    zIndex: -feature.getGeometry().getCoordinates()[1],
                });
                feature.set('style', style);
            } else {
                style.setImage(
                    getOLIcon(vm, campgroundId, campgroundType, is_match)
                );
            }
            return style;
        },
    });

    $('#mapPopupClose').on('click', function (ev) {
        vm.popup.setPosition(undefined);
        vm.selectedFeature = null;
        return false;
    });
    vm.popupContent = document.getElementById('mapPopupContent');
    vm.popup = new ol.Overlay({
        element: document.getElementById('mapPopup'),
        offset: [0, 0],
        positioning: 'center-center',
        autoPan: {
            margin: 8,
            animation: {
                duration: 1000,
            },
        },
    });

    vm.posFeature = new ol.Feature();
    vm.posFeature.setStyle(
        new ol.style.Style({
            image: new ol.style.Icon({
                src: vm.locationIcon,
                snapToPixel: true,
                anchor: [0.5, 0.5],
                anchorXUnits: 'fraction',
                anchorYUnits: 'fraction',
            }),
        })
    );

    vm.posLayer = new ol.layer.Vector({
        source: new ol.source.Vector({
            features: [vm.posFeature],
        }),
    });

    // create OpenLayers map object, prefill with all the stuff we made
    vm.olmap = new ol.Map({
        logo: false,
        renderer: 'canvas',
        target: 'map',
        view: new ol.View({
            projection: 'EPSG:3857',
            center: vm.defaultCenter,
            zoom: 5,
            maxZoom: 21,
            minZoom: 5,
        }),
        controls: [new ol.control.Zoom(), new ol.control.ScaleLine()],
        interactions: ol.interaction.defaults({
            altShiftDragRotate: false,
            pinchRotate: false,
        }),
        layers: [vm.streets, vm.grounds, vm.posLayer],
        overlays: [vm.popup],
    });

    // spawn geolocation tracker
    vm.geolocation = new ol.Geolocation({
        tracking: true,
        projection: vm.olmap.getView().getProjection(),
    });
    vm.geolocation.on('change:position', function () {
        var coords = vm.geolocation.getPosition();
        vm.posFeature.setGeometry(coords ? new ol.geom.Point(coords) : null);
    });

    // sad loop to change the pointer when mousing over a vector layer
    vm.olmap.on('pointermove', function (ev) {
        if (ev.dragging) {
            return;
        }
        var result =
            ev.map.forEachFeatureAtPixel(
                ev.pixel,
                function (feature, layer) {
                    $('#map').attr('title', feature.get('name'));
                    return true;
                },
                {
                    layerFilter: function (layer) {
                        return layer === vm.grounds;
                    },
                }
            ) === true;
        if (!result) {
            $('#map').removeAttr('title');
        }
        $('#map').toggleClass('click', result);
    });

    // another loop to spawn the popup on click
    vm.olmap.on('singleclick', function (ev) {
        var result = ev.map.forEachFeatureAtPixel(
            ev.pixel,
            async function (feature, layer) {
                vm.popup.setPosition(undefined); // resets popup
                vm.selectedFeature = feature;
                var zoom_level = $('#zoom_level').val();

                const coord = feature.getGeometry().getCoordinates();
                const view = vm.olmap.getView();
                let resolution = vm.resolutions[10];
                if (zoom_level > 0) {
                    resolution = vm.resolutions[zoom_level];
                }
                // really want to make vue.js render this, except reactivity dies
                // when you pass control of the popup element to OpenLayers :(
                $('#mapPopupName')[0].innerHTML = feature.get('name');
                if (feature.get('images')) {
                    var popup_image = '/static/ps/img/no_image.jpg';
                    var fimages = feature.get('images');
                    if (fimages) {
                        if (fimages.length > 0) {
                            if (fimages[0].image != null) {
                                popup_image = fimages[0].image;
                            }
                        }
                    }
                    $('#mapPopupImage').attr(
                        'src',
                        vm.parkstayUrl +
                            '/campground-image/146/248/?mediafile=' +
                            popup_image
                    );
                    $('#mapPopupImage').show();
                } else {
                    $('#mapPopupImage').hide();
                }
                if (
                    feature.get('price_hint') &&
                    Number(feature.get('price_hint'))
                ) {
                    $('#mapPopupPrice')[0].innerHTML =
                        '<small>From $' +
                        feature.get('price_hint') +
                        ' per night</small>';
                } else {
                    $('#mapPopupPrice')[0].innerHTML = '';
                }
                $('#mapPopupDescription')[0].innerHTML =
                    feature.get('description');

                // This portion needs to be modified to accomodate the new button
                // Online/Offline sites is determined by the backend api
                const isMatch = feature.get('match') === true;
                if (isMatch) {
                    $('#mapPopupButton')[0].className = 'button';
                } else {
                    $('#mapPopupButton').html('More information');
                    $('#mapPopupButton')[0].className = 'button formButton5';
                }

                if (feature.get('campground_type') == 0) {
                    $('#mapPopupButton').attr(
                        'href',
                        vm.parkstayUrl +
                            '/search-availability/campground/?site_id=' +
                            feature.getId() +
                            '&' +
                            vm.bookingParam
                    );
                    if (isMatch) {
                        $('#mapPopupButton').html('See availability');
                        if (feature.get('available')) {
                            $('#mapPopupButton')[0].className =
                                'button formButton1';
                        } else {
                            $('#mapPopupButton')[0].className =
                                'button formButton4';
                        }
                    }
                } else if (feature.get('campground_type') == 1) {
                    $('#mapPopupButton').attr(
                        'href',
                        vm.parkstayUrl +
                            '/search-availability/campground/?site_id=' +
                            feature.getId()
                    );
                    if (isMatch) {
                        $('#mapPopupButton').html('More information');
                        $('#mapPopupButton')[0].className = 'button formButton';
                    }
                } else {
                    // Now,this section is used for the partner accommodation
                    if (isMatch) {
                        $('#mapPopupButton').html(
                            'More Information<i class="bi bi-box-arrow-up-right ms-2">'
                        );
                        $('#mapPopupButton')[0].className =
                            'button formButton2';
                    }
                    $('#mapPopupButton').attr(
                        'href',
                        vm.parkstayUrl +
                            '/search-availability/campground/?site_id=' +
                            feature.getId()
                    );
                }
                setTimeout(() => {
                    view.animate(
                        {
                            center: coord,
                            resolution: resolution,
                            duration: 1000,
                        }
                    );
                    return true;
                }, 300);
                setTimeout(() => {
                    vm.popup.setPosition(coord);
                    return true;
                }, 1300);
            },
            {
                layerFilter: function (layer) {
                    return layer === vm.grounds;
                },
            }
        );
        // if just single-clicking the map, hide the popup
        if (!result) {
            vm.popup.setPosition(undefined);
        }
    });

    // hook to update the visible feature list on viewport change
    vm.olmap.getView().on('propertychange', function (ev) {
        vm.updateViewport();
    });
    vm.olmap.on('loadstart', function (ev) {
        if(!search_avail.var.map_loaded_first) {
            $('#map-preview').find('.loading-map').show();
        }
    });
    vm.olmap.on('loadend', function (ev) {
        if (!search_avail.var.map_loaded_first) {
            search_avail.var.map_loaded_first = true
            $('#map-preview').find('.loading-map').hide();
        }
    });

    $(window).resize(function () {
        var screen_width = $(window).width();
        if (vm.screen_width !== screen_width) {
            vm.reloadMap();
            vm.screen_width = screen_width;
        }
    });

    //new Glider(document.querySelector('.glider'), {  slidesToShow: 5,
    //  slidesToScroll: 5,
    //  draggable: true,
    //  dots: '.dots',
    //  arrows: {
    //    prev: '.glider-prev',
    //    next: '.glider-next'
    //  }
    //});

    vm.reload();
}
