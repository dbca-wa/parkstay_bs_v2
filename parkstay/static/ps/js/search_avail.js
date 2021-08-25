var search_avail = {
    var: { 'location_url' : '/api/campground_map/?format=json',
	   'search_location_url' : '/api/search_suggest',
           'places_url' : '/api/places/',
           'locations' : [],
           'places': [],
	   'search_locations': []
    },
    get_search_locations: function() {
                $.ajax({
                    url: search_avail.var.search_location_url,
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    data: "{}",
                    success: function(response) {
                            search_avail.var.search_locations = response;
                    },
                    error: function (error) {
                        alert('Error loading search locations');
                    },
                });
    },	   
    get_locations: function() {
                $.ajax({
                    url: search_avail.var.location_url,
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    data: "{}",
                    success: function(response) {
                            search_avail.var.locations = response;
                            // console.log(response);

                    },
                    error: function (error) {
                        alert('Error loading locations');
                    },
                });
    },
    get_places: function() {
                $.ajax({
                    url: search_avail.var.places_url,
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    // data: "{}",
                    success: function (response) {
                            search_avail.var.places = response;
                            // console.log(response);
                    },
                    error: function (error) {
                        alert('Error loading places');
                    },
                });
    },
    select_dates: function(start, end) {
        $('#when-date-range #when-dates').html("<b>Arrive:</b> "+start.format('D MMM YYYY') + ' <b>Depart:</b> ' + end.format('D MMM YYYY'));

        $('#checkin').val(start.format('YYYY/MM/DD'));
        $('#checkout').val(end.format('YYYY/MM/DD'));

        var whennights = search_avail.calculate_nights(start,end);
        $('#when-nights').html(whennights);
	$('#map-reload').click();
    },
    calculate_nights: function(start,end) {
           oneDay = 24 * 60 * 60 * 1000; 
           diffDays = Math.round(Math.abs((start - end) / oneDay));
           diffDays = diffDays - 1; 
           return diffDays;
    },
    select_remove: function() {
	    $('#search-filters').hide();
            $('#search-selections').hide();

            $('#region-park-selection-outer').hide();
            $('#region-park-selection-inner').html('');
            $('#region-park').val('');
            $('#region-park').show();
    },
    select_region: function(value_id, value_name, coord_1, coord_2, zoom_level) {
	      $('#coord_1').val(coord_1);
	      $('#coord_2').val(coord_2);
	      $('#zoom_level').val(zoom_level);
              $('#search-filters').show();
 	      $('#search-selections').show();
	      // need to open the map first before the campground cards will show
	      search_avail.select_filter_tab('map');
	      search_avail.select_filter_tab('campgrounds');

              $('#region-park-selection-outer').show();
              $('#region-park-selection-inner').html(value_name);
              $('#ps_search_dropdown').remove();
              $('#region-park').hide();
	     
    },
    select_filter_tab: function(tab) {
             $('#card-preview').hide();
	     $('#map-preview').hide();
             $('#card-preview-tab').removeClass('active');
	     $('#map-preview-tab').removeClass('active');

             if (tab == 'campgrounds') {
                  $('#card-preview').show();
		  $('#card-preview-tab').addClass('active');
	     }

	     if (tab == 'map') {
		  $('#map-preview').show();
		  $('#map-reload').click();
		  $('#map-preview-tab').addClass('active');
	     }

    },
    filter_options: function(status) { 
            if (status == 'open') { 
                $('#filter-options').slideDown();
		$('#more-filters').hide();
		$('#hide-filters').show();
            } else {
		$('#filter-options').slideUp();
		$('#hide-filters').hide();
		$('#more-filters').show();
            }

    },
    distance_between_gps: function(lat1, lon1, lat2, lon2, unit) {
	if ((lat1 == lat2) && (lon1 == lon2)) {
		return 0;
	}
	else {
		var radlat1 = Math.PI * lat1/180;
		var radlat2 = Math.PI * lat2/180;
		var theta = lon1-lon2;
		var radtheta = Math.PI * theta/180;
		var dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
		if (dist > 1) {
			dist = 1;
		}
		dist = Math.acos(dist);
		dist = dist * 180/Math.PI;
		dist = dist * 60 * 1.1515;
		if (unit=="K") { dist = dist * 1.609344 }
		if (unit=="N") { dist = dist * 0.8684 }
		return dist;
	}
    },
    init_dateselection: function() { 
        var start = moment().add(1, 'days');
        var end = moment().add(8,'days');

        $('#when-date-range').daterangepicker({
            minDate: new Date(),
            startDate: start,
            endDate: end,
            //ranges: {
            //   'Today': [moment(), moment()],
            //   'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            //   'Last 7 Days': [moment().subtract(6, 'days'), moment()],
            //   'Last 30 Days': [moment().subtract(29, 'days'), moment()],
            //   'This Month': [moment().startOf('month'), moment().endOf('month')],
            //   'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            //}
        }, search_avail.select_dates);
        search_avail.select_dates(start,end); 
    }, 
    search_pl: function(e, element_id, element_value) {
            if (element_value.length < 2) {
                $('#ps_search_dropdown').remove();
            } else {

            console.log(this);
            var search_results = [];
            for (let i = 0; i < search_avail.var.locations.features.length; i++) {
                    if (search_avail.var.locations.features[i].properties.name.toLocaleLowerCase().indexOf(element_value.toLocaleLowerCase())!=-1) {
                          console.log('found');
                          // search_results.push({'id': search_avail.var.locations.features[i].properties.id , 'name': search_avail.var.locations.features[i].properties.name, 'type' :'locations','coord_1' : search_avail.var.locations.features[i].geometry.coordinates[0], 'coord_2': search_avail.var.locations.features[i].geometry.coordinates[1]});
                    }
                   // console.log(search_avail.var.locations.features[i].properties.name);
            }

            for (let i = 0; i < search_avail.var.search_locations.features.length; i++) {
                    if (search_avail.var.search_locations.features[i].properties.name.toLocaleLowerCase().indexOf(element_value.toLocaleLowerCase())!=-1) {
                          console.log('search found');
                          search_results.push({'id': search_avail.var.search_locations.features[i].properties.id , 'name': search_avail.var.search_locations.features[i].properties.name, 'type' :'locations','coord_1' : search_avail.var.search_locations.features[i].coordinates[0], 'coord_2': search_avail.var.search_locations.features[i].coordinates[1], 'zoom_level':search_avail.var.search_locations.features[i].properties.zoom_level});
                    }
                   // console.log(search_avail.var.locations.features[i].properties.name);
            }
            

            for (let i = 0; i < search_avail.var.places.length; i++) {
                     if (search_avail.var.places[i].name.toLocaleLowerCase().indexOf(element_value.toLocaleLowerCase()) != -1) {
                           search_results.push({'id': search_avail.var.places[i].id ,'name': search_avail.var.places[i].name, 'type': 'places', 'coord_1': search_avail.var.places[i].gps[0], 'coord_2': search_avail.var.places[i].gps[1], 'zoom_level': search_avail.var.places[i].zoom_level});
                     }
                      //console.log(search_avail.var.places[i].name);
            }


            if (e.keyCode === 13) {
                if (search_results.length > 0) {
                        search_avail.select_region(search_results[0]['id'],search_results[0]['name'], search_results[0]['coord_1'], search_results[0]['coord_2'], search_avail.var.places[i].zoom_level);
                        // $('#region-park-selection').html(search_results[0]['name']);
                }


            } else {
                // Create list for dropdown
                var search_results_html = "";
                var rowcount =0;

                for (let i = 0; i < search_results.length; i++) {
                        // console.log(search_results[i]['name']+"test");
                        var search_pattern = RegExp(element_value, 'gi');
                        var sr = search_results[i]['name'].match(search_pattern);
                        for (let s = 0; s < sr.length; s++) {
                               var completed = {};
                               var sp = RegExp(sr[s], 'g');

                               search_results[i]['name'] = search_results[i]['name'].replace(sp, "<span>"+sr[s]+"</span>");
                        }
                        // search_results[i]['name']
                        if (rowcount < 15) {
                            // var search_pattern = RegExp(element_value, 'gi');
                            // search_results[i]['name'] = search_results[i]['name'].replace(search_pattern, "<span>"+element_value+"</span>");
                        search_results_html += "<div id='search_dropdown_item_"+rowcount+"' onclick='search_avail.select_region("+search_results[i]['id']+","+'"'+search_results[i]['name']+'"'+","+'"'+search_results[i]['coord_1']+'"'+","+'"'+search_results[i]['coord_2']+'"'+","+'"'+search_results[i]['zoom_level']+'"'+");'  class='search_dropdown_item_outer'><div class='search_dropdown_item_inner'>"+search_results[i]['name']+"</div></div>";
                            rowcount = rowcount + 1;
                        }
                }

                $('#ps_search_dropdown').remove();
                $('#'+element_id).after("<div id='ps_search_dropdown' class='search_dropdown'><div class='col-sm-12'>"+search_results_html+"</div></div>");
                }
            }
    },
    search_availabilty_locations: function() {




    }

}
