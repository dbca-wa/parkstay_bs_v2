var search_avail = {
  var: {
    csrf_token: "",
    selected_site: null,
    map_loaded_first: false,
    multiplesites: [],
    multiplesites_options: { min_people: 0, max_people: 0, max_vehicle: 0 },
    multiplesites_class_totals: {},
    change_booking_id: null,
    page: "",
    campground_id: null,
    camping_period: { checkin: null, checkout: null },
    location_url: "/api/campground_map/?format=json",
    search_location_url: "/api/search_suggest",
    get_booking_vehicle_info: "/api/get_booking_vehicle_info/",
    update_booking_vehicle_info: "/api/booking_vehicle_update/",
    places_url: "/api/places/",
    locations: [],
    places: [],
    search_locations: [],
    campers: {
      adult: 2,
      concession: 0,
      children: 0,
      infant: 0,
      total_people: 0,
    },
    vehicles: {
      vehicle: 0,
      campervan: 0,
      motorcycle: 0,
      trailer: 0,
      caravan: 0,
      total_vehicles: 0,
    },
    loaded: { locations: false, search_locations: false, places: false },
    selecttype: "single",
    mcs_enabled: false,
    selected_booking_id: null,
    site_type: null,
    availabity: null,
    max_advance_booking: 60,
    campground_release_date: null,
    campground_booking_open_date: null,
    today_date: null,
    arrival_days: 0,
    permission_to_make_advanced_booking: false,
    arrival: null,
    departure: null,
    date_override: false,
  },
  change_tabs: function (tabname) {
    $("#campsite-booking").hide();
    $("#campground-details").hide();
    $("#campsite-booking-tab").removeClass("active");
    $("#campground-details-tab").removeClass("active");
    $("#" + tabname + "-tab").addClass("active");
    $("#" + tabname).show();
  },
  change_camper_counters: function (group, direction) {
    if (group in search_avail.var.campers) {
      if (direction == "up") {
        search_avail.var.campers[group] = search_avail.var.campers[group] + 1;
      }
    }

    if (group in search_avail.var.campers) {
      if (direction == "down") {
        if (search_avail.var.campers[group] > 0) {
          search_avail.var.campers[group] = search_avail.var.campers[group] - 1;
        }
      }
    }

    // search_avail.var.campers['total_people']  = search_avail.var.campers['adult'] + search_avail.var.campers['concession'] + search_avail.var.campers['children'];
    //$('#camper-selection-inner-text').html(search_avail.var.campers['adult']+' adult, '+search_avail.var.campers['concession']+' concession, '+search_avail.var.campers['children']+' child, '+search_avail.var.campers['infant']+' Infant');
    search_avail.total_campers();
    if (
      search_avail.var.campers["adult"] > 0 ||
      search_avail.var.campers["concession"] > 0
    ) {
      $("#adult-message").html("");
    } else {
      $("#adult-message").html("Minimum 1 adult required");
      // search_avail.change_camper_counters('adult','up');
    }
    if (search_avail.var.page == "campsite-availablity") {
      ///   search_avail.load_campsite_availabilty();
    }
  },
  total_campers: function () {
    search_avail.var.campers["total_people"] =
      search_avail.var.campers["adult"] +
      search_avail.var.campers["concession"] +
      search_avail.var.campers["children"];
    $("#camper-selection-inner-text").html(
      search_avail.var.campers["adult"] +
        " adult, " +
        search_avail.var.campers["concession"] +
        " concession, " +
        search_avail.var.campers["children"] +
        " child, " +
        search_avail.var.campers["infant"] +
        " Infant"
    );
  },
  change_vehicle_counters: function (group, direction) {
    if (group in search_avail.var.vehicles) {
      if (direction == "up") {
        search_avail.var.vehicles[group] = search_avail.var.vehicles[group] + 1;
      }
    }

    if (group in search_avail.var.vehicles) {
      if (direction == "down") {
        if (search_avail.var.vehicles[group] > 0) {
          search_avail.var.vehicles[group] =
            search_avail.var.vehicles[group] - 1;
        }
      }
    }

    search_avail.total_vehicles();
    //$('#vehicle-selection-inner-text').html(search_avail.var.vehicles['vehicle']+' vehicle , '+search_avail.var.vehicles['campervan']+' campervans, '+search_avail.var.vehicles['motorcycle']+' motorcycles, '+search_avail.var.vehicles['trailer']+' trailers');

    if (search_avail.var.page == "campsite-availablity") {
      // search_avail.load_campsite_availabilty();
    }
  },
  total_vehicles: function () {
    search_avail.var.vehicles["total_vehicles"] =
      search_avail.var.vehicles["vehicle"] +
      search_avail.var.vehicles["campervan"] +
      search_avail.var.vehicles["motorcycle"] +
      search_avail.var.vehicles["trailer"] +
      search_avail.var.vehicles["caravan"];
    var total_vehicles_occupied_space = 0;
    total_vehicles_occupied_space =
      search_avail.var.vehicles["motorcycle"] / 2 +
      search_avail.var.vehicles["vehicle"] +
      search_avail.var.vehicles["campervan"] +
      search_avail.var.vehicles["trailer"] +
      search_avail.var.vehicles["caravan"];
    // var vehicle_addons = search_avail.var.vehicles['trailer'] + search_avail.var.vehicles['caravan'];
    // if (vehicle_addons <= search_avail.var.vehicles['vehicle']) {
    //      total_vehicles_occupied_space = total_vehicles_occupied_space - vehicle_addons;
    // }

    search_avail.var.vehicles["total_vehicles_occupied_space"] =
      total_vehicles_occupied_space;

    $("#vehicle-selection-inner-text").html(
      search_avail.var.vehicles["vehicle"] +
        " car/ute , " +
        search_avail.var.vehicles["campervan"] +
        " campervan, " +
        search_avail.var.vehicles["caravan"] +
        " caravan/camper trailer, " +
        search_avail.var.vehicles["motorcycle"] +
        " motorcycle, " +
        search_avail.var.vehicles["trailer"] +
        " other trailer"
    );
  },
  open_vehicle_updates: function (booking_id) {
    $("#vehicle-update-error").hide();
    $("#BookingVehicleUpdates").modal("show");
    search_avail.var.selected_booking_id = booking_id;
    search_avail.get_booking_vehicle_info(booking_id);
  },
  get_booking_vehicle_info: function (booking_id) {
    $("#datatables-BookingVehicleUpdates").html(
      '<tr><td colspan=3 align="center"><div class="spinner-border text-primary" role="status"> <span class="visually-hidden">Loading...</span></div></td></tr>'
    );
    var datahtml = "";
    var vehicle_map = {};
    vehicle_map["vehicle"] = "Car/Ute";
    vehicle_map["motorbike"] = "Motorcycle";
    vehicle_map["campervan"] = "Campervan";
    vehicle_map["trailer"] = "Trailer";
    vehicle_map["caravan"] = "Caravan/Camper trailer";

    $.ajax({
      url: search_avail.var.get_booking_vehicle_info + booking_id + "/",
      method: "GET",
      dataType: "json",
      contentType: "application/json",
      //data: "{}",
      success: function (response) {
        for (let i = 0; i < response.length; i++) {
          datahtml += "<tr>";
          datahtml += "<td>" + vehicle_map[response[i].type] + "</td>";
          datahtml +=
            "<td><input type='text' class='form-control' name='bvrego-" +
            response[i].id +
            "' value='" +
            response[i].rego +
            "'></td>";
          datahtml += "<td align='center'>";
          if (response[i].hire_car == true) {
            datahtml +=
              "<i class='bi bi-check-circle-fill' style='color:#2eb701;'>";
          } else {
            datahtml +=
              "<i class='bi bi-x-circle-fill' style='color:red'></i></i></td>";
          }
          datahtml += "</tr>";
        }
        $("#datatables-BookingVehicleUpdates").html(datahtml);
        setTimeout("$('#LoadingPopup').modal('hide');", 800);
      },
      error: function (error) {
        console.log("Error loading search locations");
      },
    });
  },
  update_booking_vehicle_info: function () {
    console.log("update_booking_vehicle_info");

    var data = { booking_id: search_avail.var.selected_booking_id };
    $("#datatables-BookingVehicleUpdates")
      .find("input")
      .each(function () {
        if (this.name.substring(0, 7) == "bvrego-") {
          data[this.name] = this.value;
        }
      });

    $("#BookingVehicleUpdates").modal("hide");
    $("#LoadingPopup").modal("show");
    $.ajax({
      url: search_avail.var.update_booking_vehicle_info,
      method: "POST",
      headers: { "X-CSRFToken": search_avail.var.csrf_token },
      data: JSON.stringify({ payload: data }),
      contentType: "application/json",
      success: function (data) {
        $("#group-flat-success").show();
        $("#group-flat-success").html("Successfull");
        setTimeout("$('#LoadingPopup').modal('hide');", 800);
        setTimeout("$('#group-flat-success').fadeOut(2000);", 7000);
      },
      error: function (error) {
        $("#vehicle-update-error").html(error.responseJSON.msg.error);
        $("#vehicle-update-error").show();

        $("#LoadingPopup").modal("hide");
        $("#BookingVehicleUpdates").modal("show");
        console.log("Error updating vehicle information");
      },
    });
  },
  get_search_locations: function () {
    $.ajax({
      url: search_avail.var.search_location_url,
      method: "GET",
      dataType: "json",
      contentType: "application/json",
      data: "{}",
      success: function (response) {
        search_avail.var.search_locations = response;
        search_avail.var.loaded.search_locations = true;
      },
      error: function (error) {
        console.log("Error loading search locations");
      },
    });
  },
  get_locations: function () {
    $.ajax({
      url: search_avail.var.location_url,
      method: "GET",
      dataType: "json",
      contentType: "application/json",
      data: "{}",
      success: function (response) {
        search_avail.var.locations = response;
        search_avail.var.loaded.locations = true;
      },
      error: function (error) {
        console.log("Error loading locations");
      },
    });
  },
  get_places: function () {
    $.ajax({
      url: search_avail.var.places_url,
      method: "GET",
      dataType: "json",
      contentType: "application/json",
      // data: "{}",
      success: function (response) {
        search_avail.var.places = response;
        search_avail.var.loaded.places = true;
        // console.log(response);
      },
      error: function (error) {
        console.log("Error loading places");
      },
    });
  },
  close_dropdowns: function () {
    var vehicledropdown = $("#vehicle-dropdown").css("display");
    var camperdropdown = $("#camper-dropdown").css("display");
    if (vehicledropdown == "none" && camperdropdown == "none") {
    } else {
      search_avail.load_campsite_availabilty();
      $("#camper-dropdown").hide();
      $("#vehicle-dropdown").hide();
      $("#campsite-availablity").removeClass("div-blur");
    }
  },
  vehicle_toggle: function () {
    $("#camper-dropdown").hide();
    var vehicledropdown = $("#vehicle-dropdown").css("display");
    if (vehicledropdown == "none") {
      $("#campsite-availablity").addClass("div-blur");
      $("#vehicle-dropdown").show();
    } else {
      $("#vehicle-dropdown").hide();
      search_avail.load_campsite_availabilty();
      $("#campsite-availablity").removeClass("div-blur");
    }
  },
  campers_toggle: function () {
    $("#vehicle-dropdown").hide();
    var camperdropdown = $("#camper-dropdown").css("display");
    if (camperdropdown == "none") {
      $("#camper-dropdown").show();
      $("#campsite-availablity").addClass("div-blur");
    } else {
      $("#camper-dropdown").hide();
      search_avail.load_campsite_availabilty();
      $("#campsite-availablity").removeClass("div-blur");
    }
  },
  select_days_earlier: function (days) {
    var checkin = $("#checkin").val();
    var checkout = $("#checkout").val();

    var checkin_date = Date.parse(checkin);
    var checkout_date = Date.parse(checkout);
    var checkin_date_moment = moment(checkin_date);
    var checkout_date_moment = moment(checkout_date);
    var checkin_date_moment = checkin_date_moment.subtract(1, "days");
    var checkout_date_moment = checkout_date_moment.subtract(1, "days");
    search_avail.init_dateselection(
      checkin_date_moment.format("YYYY/MM/DD"),
      checkout_date_moment.format("YYYY/MM/DD")
    );
  },
  select_days_later: function (days) {
    var checkin = $("#checkin").val();
    var checkout = $("#checkout").val();

    var checkin_date = Date.parse(checkin);
    var checkout_date = Date.parse(checkout);
    var checkin_date_moment = moment(checkin_date);
    var checkout_date_moment = moment(checkout_date);
    var checkin_date_moment = checkin_date_moment.add(1, "days");
    var checkout_date_moment = checkout_date_moment.add(1, "days");
    search_avail.init_dateselection(
      checkin_date_moment.format("YYYY/MM/DD"),
      checkout_date_moment.format("YYYY/MM/DD")
    );
  },
  select_dates: function (start, end) {
    $("#when-date-range #when-dates").html(
      "<b>Arrive:</b> " +
        start.format("ddd D MMM YY") +
        " <b>Depart:</b> " +
        end.format("ddd D MMM YY")
    );
    const fStartDate = start.format("YYYY/MM/DD");
    const fEndDate = end.format("YYYY/MM/DD");
    $("#checkin").val(fStartDate);
    $("#checkout").val(fEndDate);
    search_avail.update_dates_search_params(fStartDate, fEndDate);
    search_avail.var.camping_period["checkin"] = fStartDate;
    search_avail.var.camping_period["checkout"] = fEndDate;

    var whennights = search_avail.calculate_nights(fStartDate, fEndDate);
    var arrival_days = search_avail.calculate_arrival_days(fStartDate);

    $("#when-nights").html(whennights);
    if (search_avail.var.page == "campground") {
      // search_avail.load_campground_availabilty();
      $("#map-reload").trigger("click");
    }
    if (search_avail.var.page == "campsite-availablity") {
      search_avail.load_campsite_availabilty();
    }
  },
  calculate_nights: function (start, end) {
    var start_dt = Date.parse(start);
    var end_dt = Date.parse(end);

    oneDay = 24 * 60 * 60 * 1000;

    diffDays = Math.round(
      Math.abs((moment(start_dt) - moment(end_dt)) / oneDay)
    );
    // diffDays = diffDays - 1;
    return diffDays;
  },
  calculate_arrival_days: function (start) {
    var date_now = Date.now();
    var date_arrival = Date.parse(start);
    oneDay = 24 * 60 * 60 * 1000;
    diffDays = Math.round(
      Math.abs((moment(date_now) - moment(date_arrival)) / oneDay)
    );
    search_avail.var.arrival_days = diffDays;
    return diffDays;
  },
  select_place_id: function (place_id) {
    var found = false;
    for (let i = 0; i < search_avail.var.places.length; i++) {
      if (search_avail.var.places[i].id == place_id) {
        found = true;
        //alert(search_avail.var.places[i].zoom_level);
        //
        search_avail.select_region(
          search_avail.var.places[i].id,
          search_avail.var.places[i].name,
          search_avail.var.places[i].gps[0],
          search_avail.var.places[i].gps[1],
          search_avail.var.places[i].zoom_level
        );
      }
    }
    if (found == false) {
      $("#loading-error").html(
        '<div class="alert alert-danger" role="alert">Sorry, unable to find places with id ' +
          place_id +
          ".</div>"
      );
    }
  },
  select_campground_id: function (campground_id) {
    var found = false;
    for (
      let i = 0;
      i < search_avail.var.search_locations.features.length;
      i++
    ) {
      if (
        search_avail.var.search_locations.features[i].properties.id ==
          campground_id &&
        search_avail.var.search_locations.features[i].properties.type ==
          "Campground"
      ) {
        found = true;
        search_avail.select_region(
          search_avail.var.search_locations.features[i].properties.id,
          search_avail.var.search_locations.features[i].properties.name,
          search_avail.var.search_locations.features[i].coordinates[0],
          search_avail.var.search_locations.features[i].coordinates[1],
          search_avail.var.search_locations.features[i].properties.zoom_level
        );
      }
    }
    if (found == false) {
      $("#loading-error").html(
        '<div class="alert alert-danger" role="alert">Sorry, unable to find campground with id ' +
          campground_id +
          ".</div>"
      );
      //		 alert('results not found');
    }
  },
  select_remove: function () {
    $("#search-filters").hide();
    $("#search-selections").hide();

    $("#region-park-selection-outer").hide();
    $("#region-park-selection-inner").html("");
    $("#region-park").val("");
    $("#region-park").show();
    $("#notice_div").show();

    $("#mapPopupClose").trigger("click");
  },
  select_region: function (value_id, value_name, coord_1, coord_2, zoom_level) {
    $("#coord_1").val(coord_1);
    $("#coord_2").val(coord_2);
    $("#zoom_level").val(zoom_level);
    $("#search-filters").show();
    $("#search-selections").show();
    // search_avail.load_campground_availabilty();
    // need to open the map first before the campground cards will show
    search_avail.select_filter_tab("campgrounds");
    search_avail.select_filter_tab("map");
    $("#region-park-selection-outer").show();
    $("#region-park-selection-inner").html(value_name);
    $("#ps_search_dropdown").remove();
    $("#region-park").hide();
    $("#notice_div").hide();

    $("#mapPopupClose").trigger("click");
  },
  select_filter_tab: function (tab) {
    $("#card-preview").hide();
    $("#map-preview").hide();
    $("#card-preview-tab").removeClass("active");
    $("#map-preview-tab").removeClass("active");

    if (tab == "campgrounds") {
      $("#card-preview").show();
      $("#card-preview-tab").addClass("active");
      // $("#mapPopupClose").trigger("click");
    }

    if (tab == "map") {
      $("#map-preview").show();
      $("#map-reload").trigger("click");
      $("#map-preview-tab").addClass("active");
    }
  },
  filter_options: function (status) {
    if (status == "open") {
      $("#filter-options").slideDown();
      $("#more-filters").hide();
      $("#hide-filters").show();
    } else {
      $("#filter-options").slideUp();
      $("#hide-filters").hide();
      $("#more-filters").show();
    }
  },
  distance_between_gps: function (lat1, lon1, lat2, lon2, unit) {
    if (lat1 == lat2 && lon1 == lon2) {
      return 0;
    } else {
      var radlat1 = (Math.PI * lat1) / 180;
      var radlat2 = (Math.PI * lat2) / 180;
      var theta = lon1 - lon2;
      var radtheta = (Math.PI * theta) / 180;
      var dist =
        Math.sin(radlat1) * Math.sin(radlat2) +
        Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
      if (dist > 1) {
        dist = 1;
      }

      dist = Math.acos(dist);
      dist = (dist * 180) / Math.PI;
      dist = dist * 60 * 1.1515;
      if (unit == "K") {
        dist = dist * 1.609344;
      }
      if (unit == "N") {
        dist = dist * 0.8684;
      }
      return dist;
    }
  },
  init_dateselection: function (start, end) {
    var dateoverride = $("#date-override").is(":checked");
    if (dateoverride == null) {
      dateoverride = false;
    }

    if (start == null) {
      start = moment().add(0, "days");
    } else {
      var start_date = Date.parse(start);
      start = moment(start_date);
    }
    if (end == null) {
      end = moment().add(1, "days");
    } else {
      var end_date = Date.parse(end);
      end = moment(end_date);
    }

    var change_booking_after_arrival_before_departure = $(
      "#change_booking_after_arrival_before_departure"
    ).val();
    var parkstay_officers_change_arrival = $(
      "#parkstay_officers_change_arrival"
    ).val();
    var is_change_booking = $("#is_change_booking").val();
    var is_parkstay_officers = $("#is_parkstay_officers").val();
    //alert($('#checkin').val());
    // parkstay_officers_change_arrival = 'False';
    if (change_booking_after_arrival_before_departure == "True") {
      $("#departure-date").datepicker({
        format: "dd/mm/yyyy",
        startDate: "+1d",
      });
      if (is_parkstay_officers == "True") {
        $("#when-date-range").daterangepicker(
          {
            minDate: minDate,
            startDate: start,
            endDate: end,
          },
          search_avail.select_dates
        );
      } else {
        // $('#departure-date').datepicker('setStartDate', start.add(1, "days").format('DD-MM-YYYY'));
        // $('#departure-date').datepicker({'setStartDate': start.format('DD-MM-YYYY'), 'minDate': startDate_plus_1 });
      }

      $("#departure-date").change(function () {
        console.log("input's current value: " + this.value);
        var date_split = this.value.split("/");
        var start_date = Date.parse($("#checkin").val());
        var end_date = Date.parse(
          date_split[2] + "/" + date_split[1] + "/" + date_split[0]
        );
        start = moment(start_date);
        end = moment(end_date);
        search_avail.select_dates(start, end);
        //search_avail.init_dateselection($('#checkin').val(), date_split[2]+"/"+date_split[1]+"/"+date_split[0])
      });
    } else {
      var minDate = new Date();
      if (parkstay_officers_change_arrival == "True") {
        //minDate = null;
        minDate = start;
      }

      if (dateoverride == true) {
        $("#when-date-range").daterangepicker(
          {
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
          },
          search_avail.select_dates
        );
      } else {
        if (is_change_booking == "True") {
          // dont initate date range selection
          // $('#arrival-date').datepicker({
          //     format: 'dd/mm/yyyy',
          //     startDate : '+1d',
          // });

          // if (is_parkstay_officers == 'True') {
          $("#when-date-range").daterangepicker(
            {
              minDate: minDate,
              startDate: start,
              endDate: end,
            },
            search_avail.select_dates
          );

          // } else {

          //     $('#arrival-date').datepicker('setEndDate', end.format('DD-MM-YYYY'));
          //  }

          $("#arrival-date").change(function () {
            console.log("input's current value: " + this.value);
            var date_split = this.value.split("/");
            var start_date = Date.parse(
              date_split[2] + "/" + date_split[1] + "/" + date_split[0]
            );
            var end_date = Date.parse($("#checkout").val());
            start = moment(start_date);
            end = moment(end_date);
            search_avail.select_dates(start, end);
            //search_avail.init_dateselection($('#checkin').val(), date_split[2]+"/"+date_split[1]+"/"+date_split[0])
          });
        } else {
          $("#when-date-range").daterangepicker(
            {
              minDate: minDate,
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
            },
            search_avail.select_dates
          );
        }
      }
    }
    search_avail.select_dates(start, end);
  },
  search_pl: function (e, element_id, element_value) {
    if (element_value.length < 2) {
      $("#ps_search_dropdown").remove();
    } else {
      var search_results = [];
      if (search_avail.var.locations) {
        for (let i = 0; i < search_avail.var.locations.features.length; i++) {
          if (
            search_avail.var.locations.features[i].properties.name
              .toLocaleLowerCase()
              .indexOf(element_value.toLocaleLowerCase()) != -1
          ) {
            // search_results.push({'id': search_avail.var.locations.features[i].properties.id , 'name': search_avail.var.locations.features[i].properties.name, 'type' :'locations','coord_1' : search_avail.var.locations.features[i].geometry.coordinates[0], 'coord_2': search_avail.var.locations.features[i].geometry.coordinates[1]});
          }
          // console.log(search_avail.var.locations.features[i].properties.name);
        }
      }

      for (
        let i = 0;
        i < search_avail.var.search_locations.features.length;
        i++
      ) {
        if (
          search_avail.var.search_locations.features[i].properties.name
            .toLocaleLowerCase()
            .indexOf(element_value.toLocaleLowerCase()) != -1
        ) {
          search_results.push({
            id: search_avail.var.search_locations.features[i].properties.id,
            name: search_avail.var.search_locations.features[i].properties.name,
            type: "locations",
            coord_1:
              search_avail.var.search_locations.features[i].coordinates[0],
            coord_2:
              search_avail.var.search_locations.features[i].coordinates[1],
            zoom_level:
              search_avail.var.search_locations.features[i].properties
                .zoom_level,
          });
        }
        // console.log(search_avail.var.locations.features[i].properties.name);
      }

      for (let i = 0; i < search_avail.var.places.length; i++) {
        if (
          search_avail.var.places[i].name
            .toLocaleLowerCase()
            .indexOf(element_value.toLocaleLowerCase()) != -1
        ) {
          search_results.push({
            id: search_avail.var.places[i].id,
            name: search_avail.var.places[i].name,
            type: "places",
            coord_1: search_avail.var.places[i].gps[0],
            coord_2: search_avail.var.places[i].gps[1],
            zoom_level: search_avail.var.places[i].zoom_level,
          });
        }
        // console.log(search_avail.var.places[i].name);
      }

      // console.log("KEY");
      // console.log(e.keyCode);

      if (e.keyCode === 13) {
        if (search_results.length > 0) {
          search_avail.select_region(
            search_results[0]["id"],
            search_results[0]["name"],
            search_results[0]["coord_1"],
            search_results[0]["coord_2"],
            search_results[0]["zoom_level"]
          );
          // $('#region-park-selection').html(search_results[0]['name']);
        }
      } else {
        // Create list for dropdown
        var search_results_html = "";
        var rowcount = 0;

        for (let i = 0; i < search_results.length; i++) {
          // console.log(search_results[i]['name']+"test");
          var search_pattern = RegExp(element_value, "gi");
          var sr = search_results[i]["name"].match(search_pattern);
          for (let s = 0; s < sr.length; s++) {
            var completed = {};
            var sp = RegExp(sr[s], "g");

            search_results[i]["name"] = search_results[i]["name"].replace(
              sp,
              "<span>" + sr[s] + "</span>"
            );
          }

          if (rowcount < 15) {
            var search_name = search_results[i]["name"].replace("'", "&#39;");
            search_results_html +=
              "<div id='search_dropdown_item_" +
              rowcount +
              "' onclick='search_avail.select_region(" +
              search_results[i]["id"] +
              "," +
              '"' +
              search_name +
              '"' +
              "," +
              '"' +
              search_results[i]["coord_1"] +
              '"' +
              "," +
              '"' +
              search_results[i]["coord_2"] +
              '"' +
              "," +
              '"' +
              search_results[i]["zoom_level"] +
              '"' +
              ");'  class='search_dropdown_item_outer'><div class='search_dropdown_item_inner'>" +
              search_results[i]["name"] +
              "</div></div>";
            rowcount = rowcount + 1;
          }
        }

        $("#ps_search_dropdown").remove();
        $("#" + element_id).after(
          "<div id='ps_search_dropdown' class='search_dropdown'><div class='col-sm-12'>" +
            search_results_html +
            "</div></div>"
        );
      }
    }
  },
  select_site: function (button_element) {
    var databutton = $(button_element).target.attr("data-button");
    var button_data = $.parseJSON(databutton);
    var post_data = {};
    $("#search-filters-campsites").hide();
    $("#campsite-availablity").hide();
  },
  delete_multiple_site: function (button_element) {
    var databutton = $(button_element).attr("data-button");
    var button_data = $.parseJSON(databutton);
    const index = search_avail.var.multiplesites.indexOf(
      button_data["campsite_id"]
    );
    if (index > -1) {
      search_avail.var.multiplesites.splice(index, 1);
      search_avail.load_campsite_availabilty();
    }
    if (button_data.hasOwnProperty("campsite_class_id") == true) {
      if (
        search_avail.var.multiplesites_class_totals.hasOwnProperty(
          button_data["campsite_class_id"]
        ) == true
      ) {
        delete search_avail.var.multiplesites_class_totals[
          button_data["campsite_class_id"]
        ];
      }
    }
  },
  select_multiple_site: function (button_element) {
    var databutton = $(button_element).attr("data-button");
    var button_data = $.parseJSON(databutton);

    if (
      search_avail.var.multiplesites.indexOf(button_data["campsite_id"]) !== -1
    ) {
    } else {
      search_avail.var.multiplesites.push(button_data["campsite_id"]);
      // var multipleselect_class_count = $('#multipleselect_class_count-'+button_data['campsite_id']).val();
      search_avail.change_multiselect_class_total(
        button_data["campsite_class_id"],
        1
      );
      search_avail.load_campsite_availabilty();
    }
  },
  change_multiselect_class_total: function (class_id, value, limit) {
    if (value > limit) {
      alert("Entry is more than available");
    } else {
      search_avail.var.multiplesites_class_totals[class_id] = value;
    }
  },
  create_booking: function (button_element) {
    var errortitle = "Error Message";
    if (search_avail.var.selecttype == "multiple") {
      if (search_avail.var.multiplesites.length > 0) {
      } else {
        alert("Please select some sites");
        return;
      }
    }

    var loadingmodal = $("#LoadingPopup");
    loadingmodal.modal("show");
    var databutton = $(button_element).attr("data-button");
    var button_data = $.parseJSON(databutton);
    var post_data = {};

    if (search_avail.var.selecttype == "multiple") {
      button_data["campsite_id"] = search_avail.var.multiplesites[0];
    }

    if (search_avail.var.site_type == 0) {
      // if (button_data['site_type'] == 0) {
      post_data = {
        date_override: search_avail.var.date_override,
        arrival: search_avail.var.camping_period["checkin"],
        departure: search_avail.var.camping_period["checkout"],
        num_adult: search_avail.var.campers["adult"],
        num_child: search_avail.var.campers["children"],
        num_concession: search_avail.var.campers["concession"],
        num_infant: search_avail.var.campers["infant"],
        campsite: button_data["campsite_id"],
        num_vehicle: search_avail.var.vehicles["vehicle"],
        num_campervan: search_avail.var.vehicles["campervan"],
        num_caravan: search_avail.var.vehicles["caravan"],
        num_motorcycle: search_avail.var.vehicles["motorcycle"],
        num_trailer: search_avail.var.vehicles["trailer"],
        change_booking_id: search_avail.var.change_booking_id,
        selecttype: search_avail.var.selecttype,
        multiplesites: JSON.stringify(search_avail.var.multiplesites),
        multiplesites_class_totals: JSON.stringify(
          search_avail.var.multiplesites_class_totals
        ),
      };
    } else {
      post_data = {
        date_override: search_avail.var.date_override,
        arrival: search_avail.var.camping_period["checkin"],
        departure: search_avail.var.camping_period["checkout"],
        num_adult: search_avail.var.campers["adult"],
        num_child: search_avail.var.campers["children"],
        num_concession: search_avail.var.campers["concession"],
        num_infant: search_avail.var.campers["infant"],
        campground_bg: button_data["campground_id"],
        campsite_class: button_data["campsite_class_id"],
        num_vehicle: search_avail.var.vehicles["vehicle"],
        num_campervan: search_avail.var.vehicles["campervan"],
        num_caravan: search_avail.var.vehicles["caravan"],
        num_motorcycle: search_avail.var.vehicles["motorcycle"],
        num_trailer: search_avail.var.vehicles["trailer"],
        change_booking_id: search_avail.var.change_booking_id,
        selecttype: search_avail.var.selecttype,
        multiplesites_class_totals: JSON.stringify(
          search_avail.var.multiplesites_class_totals
        ),
        campground: search_avail.var.campground_id,
      };
      // campsite_class: 75
    }

    $.ajax({
      url: "/api/create_booking/",
      cache: false,
      type: "POST",
      data: post_data,
      error: function (resp, status, error) {
        setTimeout("$('#LoadingPopup').modal('hide');", 800);
        var errormessage =
          "There was error attempting to create a booking for your selection.";
        if (resp.hasOwnProperty("responseJSON")) {
          if (resp.responseJSON.hasOwnProperty("inprogress_booking")) {
            var inprogress_booking = resp.responseJSON.inprogress_booking;
            if (inprogress_booking == true) {
              window.location.reload();
              return;
            }
          }

          if (resp.responseJSON.hasOwnProperty("msg")) {
            if (resp.responseJSON.msg.hasOwnProperty("error")) {
              errormessage = resp.responseJSON.msg.error;
            }

            if (resp.responseJSON.msg.hasOwnProperty("title")) {
              errortitle = resp.responseJSON.msg.title;
            }
          }
        }

        $("#error-title").html(errortitle);

        $("#error-message").html(errormessage);
        $("#MessageBox").modal("show");
      },
      success: function (data) {
        if (data["status"] == "success") {
          window.location = "/booking/";
        } else {
          console.log("Error");
        }
      },
    });
  },
  load_campground_availabilty: function () {
    $.ajax({
      url:
        "/api/campground_availabilty_view/?arrival=" +
        search_avail.var.camping_period["checkin"] +
        "&departure=" +
        search_avail.var.camping_period["checkout"],
      cache: false,
      error: function (request, status, error) {
        // $("#campsite-availablity-results").html("<center><span style='color:red; font-weight:bold;'>Sorry, there was an error loading campsite information.</span></center>");
      },
      success: function (data) {
        search_avail.var.availabity = data;
      },
    });
  },
  load_campsite_availabilty: function () {
    var change_query = "";
    if (search_avail.var.change_booking_id != null) {
      change_query = "&change_booking_id=" + search_avail.var.change_booking_id;
    }

    $("#campsite-availablity-results").html(
      "<center><img style='padding-top: 20px;' height='70' src='/static/ps/img/parkstay_loader_bar_white_500.gif'></center>"
    );

    var campground_release_date = new Date(search_avail.var.campground_release_date);
    var campground_departure_date = new Date(search_avail.var.camping_period["checkout"]);

    if (search_avail.var.campground_release_date == null || search_avail.var.campground_release_date == 'None') {

        if (search_avail.var.arrival_days >= search_avail.var.max_advance_booking) {
          if (search_avail.var.permission_to_make_advanced_booking == true) {
            // permission granted
          } else {
            $("#campsite-availablity-results").html(
              "<center style='color:red' release_date='True' >Please choose a shorter arrival date</center>"
            );
            return;
          }
        }

    } else {

      if (campground_departure_date > campground_release_date) {
        if (search_avail.var.permission_to_make_advanced_booking == true) {
          // permission granted
        } else {
          $("#campsite-availablity-results").html(
            "<center style='color:red' max_booking='True' >Please choose a shorter departure date.</center>"
          );
          return;
        }
      }
    }

    // if (search_avail.var.arrival_days > search_avail.var.max_advance_booking) {
    //   if (search_avail.var.permission_to_make_advanced_booking == true) {
    //     // permission granted
    //   } else {
    //     $("#campsite-availablity-results").html(
    //       "<center style='color:red'>Please choose a shorter arrival date.</center>"
    //     );
    //     return;
    //   }
    // }

    $.ajax({
      url:
        "/api/campsite_availablity_view/" +
        search_avail.var.campground_id +
        "/?arrival=" +
        search_avail.var.camping_period["checkin"] +
        "&departure=" +
        search_avail.var.camping_period["checkout"] +
        "&num_adult=" +
        search_avail.var.campers["adult"] +
        "&num_child=" +
        search_avail.var.campers["children"] +
        "&num_concession=" +
        search_avail.var.campers["concession"] +
        "&num_infant=" +
        search_avail.var.campers["infant"] +
        "&gear_type=all" +
        change_query,
      cache: false,
      error: function (request, status, error) {
        $("#campsite-availablity-results").html(
          "<center><span style='color:red; font-weight:bold;'>Sorry, there was an error loading campsite information.</span></center>"
        );
      },
      success: function (data) {
        // if (search_avail.var.permission_to_make_advanced_booking == true) {
        // } else {
        //   if (data.booking_time_open == false) {
        //     $("#campsite-availablity-results").html(
        //       "<div class='alert alert-primary' role='alert'>Booking availability for this campground have not yet open for bookings.  Please try booking after " +
        //         data["release_time_friendly"] +
        //         "</div>"
        //     );
        //     return;
        //   }
        // }
        var tents = $("#filter-checkbox-tent").is(":checked");
        var campervan = $("#filter-checkbox-campervan").is(":checked");
        var campertrailer = $("#filter-checkbox-campertrailer").is(":checked");

        var features_checked = new Set();

        var tents = $("#filter-checkbox-tent").is(":checked");
        var campervan = $("#filter-checkbox-campervan").is(":checked");
        var campertrailer = $("#filter-checkbox-campertrailer").is(":checked");

        $("#search-filters-campsites")
          .find("input")
          .each(function () {
            if (this.id.substring(0, 15) == "filter-feature-") {
              var filter_element_id = this.id;
              var feature_id = this.id.substring(15);
              var is_checked = $("#" + filter_element_id).is(":checked");
              if (is_checked == true) {
                features_checked.add(parseInt(feature_id));
              }
            }
          });

        var campsitehtml = "";
        var campsitehtmlbeforeselected = "";
        var campsitehtmlbefore = "";
        var campsitehtmlafter = "";
        var campsitehtmlmiddle = "";
        var campsitehtmlmiddlestart = "";
        var campsitehtmlmiddleend = "";

        var campsitehtmlbox = "";
        var site_type = data.site_type;
        search_avail.var.site_type = data.site_type;
        search_avail.var.campground_release_date = data.release_date;
        search_avail.var.campground_booking_open_date = data.booking_open_date;
        var current_booking_campsite_id = data.current_booking_campsite_id;
        var current_booking_campsite_class_id =
          data.current_booking_campsite_class_id;
        var current_booking_selection = false;
        var campground_id = data.id;
        var campsites = data.sites;
        var change_booking_after_arrival_before_departure = $(
          "#change_booking_after_arrival_before_departure"
        ).val();

        search_avail.var.multiplesites_options.min_people = 0;
        search_avail.var.multiplesites_options.max_people = 0;

        for (let s = 0; s < campsites.length; s++) {
          campsitehtml = "";
          current_booking_selection = false;
          var append_site = true;
          var campsite_available = true;
          var campsite_price = parseFloat("0.00");
          var class_name = "";
          var product_box_header_class = "product-box-header-noavail";
          var priceavail = "product-available-price-noavail";

          // Filters Start
          if (search_avail.var.selecttype == "multiple") {
            search_avail.var.multiplesites_options.min_people =
              search_avail.var.multiplesites_options.min_people +
              campsites[s].min_people;
            search_avail.var.multiplesites_options.max_people =
              search_avail.var.multiplesites_options.max_people +
              campsites[s].max_people;
          } else {
            if (
              search_avail.var.campers["total_people"] >=
                campsites[s].min_people &&
              search_avail.var.campers["total_people"] <=
                campsites[s].max_people
            ) {
              if (
                search_avail.var.campers["adult"] == 0 &&
                search_avail.var.campers["concession"] == 0
              ) {
                append_site = false;
              }
            } else {
              append_site = false;
            }
          }

          if (append_site == true) {
            var gearType = campsites[s].gearType;

            if (tents == true && gearType.tent == false) {
              append_site = false;
            }

            if (campervan == true && gearType.campervan == false) {
              append_site = false;
            }

            if (campertrailer == true && gearType.caravan == false) {
              append_site = false;
            }
          }

          if (append_site == true) {
            var gearType = campsites[s].gearType;

            if (
              search_avail.var.vehicles["vehicle"] > 0 &&
              gearType.vehicle == false
            ) {
              append_site = false;
            }
            if (
              search_avail.var.vehicles["campervan"] > 0 &&
              gearType.campervan == false
            ) {
              append_site = false;
            }

            if (
              search_avail.var.vehicles["motorcycle"] > 0 &&
              gearType.motorcycle == false
            ) {
              append_site = false;
            }

            if (
              search_avail.var.vehicles["trailer"] > 0 &&
              gearType.trailer == false
            ) {
              append_site = false;
            }

            if (
              search_avail.var.vehicles["caravan"] > 0 &&
              gearType.caravan == false
            ) {
              append_site = false;
            }
          }

          if (append_site == true) {
            if (search_avail.var.selecttype == "multiple") {
              // Check max vehicle after clicking proceed (total selected campsite after)
            } else {
              if (
                search_avail.var.vehicles["total_vehicles_occupied_space"] >
                campsites[s].max_vehicles
              ) {
                append_site = false;
              }
            }
            //if (search_avail.var.vehicles['total_vehicles_occupied_space'] == 0) {
            //         append_site = false;
            //}
          }

          // if campsites[s].max_vehicles

          if (append_site == true) {
            var campsite_features = campsites[s].features;
            var feats = new Set(
              campsite_features.map(function (x) {
                return x.id;
              })
            );

            for (var x of features_checked) {
              if (!feats.has(x)) {
                append_site = false;
              }
            }
          }

          // Filters End
          for (let p = 0; p < campsites[s].availability.length; p++) {
            campsite_price =
              campsite_price + parseFloat(campsites[s].availability[p][2]);
            if (campsites[s].availability[p][0] == true) {
            } else {
              campsite_available = false;
            }
          }

          if (campsite_available == true) {
            if (append_site == true) {
              product_box_header_class = "product-box-header-avail";
              priceavail = "product-available-price-avail";
            } else {
              product_box_header_class = "product-box-header-avail-nomatch";
              priceavail = "product-available-price-avail-nomatch";
            }
          }

          if (campsites[s].class) {
            class_name = " - " + data.classes[campsites[s].class];
          }

          campsitehtml =
            campsitehtml +
            "<div class='col-12 col-sm-12 col-md-6 col-lg-6 col-xl-4 col-xxl-3'><center>";
          campsitehtml = campsitehtml + "<div class='product-box' >";
          campsitehtml =
            campsitehtml +
            "<div class='product-box-header " +
            product_box_header_class +
            "'><h2>" +
            campsites[s].name +
            " " +
            class_name +
            "</h2></div>";
          if (site_type == 1 || site_type == 2) {
            if (current_booking_campsite_class_id == campsites[s].type) {
              current_booking_selection = true;
              if (search_avail.var.selecttype == "single") {
                campsitehtml =
                  campsitehtml +
                  "<div class='product-selected-site' >SELECTED IN CURRENT BOOKING</div>";
              } else {
                campsitehtml =
                  campsitehtml +
                  "<div class='product-not-selected-site' >&nbsp;</div>";
              }
            } else {
              campsitehtml =
                campsitehtml +
                "<div class='product-not-selected-site' >&nbsp;</div>";
            }
          } else {
            if (current_booking_campsite_id == campsites[s].id) {
              current_booking_selection = true;
              if (search_avail.var.selecttype == "single") {
                campsitehtml =
                  campsitehtml +
                  "<div class='product-selected-site' >SELECTED IN CURRENT BOOKING</div>";
              } else {
                campsitehtml =
                  campsitehtml +
                  "<div class='product-not-selected-site' >&nbsp;</div>";
              }
            } else {
              campsitehtml =
                campsitehtml +
                "<div class='product-not-selected-site' >&nbsp;</div>";
            }
          }

          campsitehtml =
            campsitehtml +
            "<div><i class='bi-people-fill' alt='Vehicle(s)' title='Vehicle(s)' ></i> " +
            campsites[s].min_people +
            " to " +
            campsites[s].max_people +
            " <i class='bi-p-square-fill'></i> " +
            campsites[s].max_vehicles +
            " </div>";

          //campsitehtml = campsitehtml + "<div class='product-availablity'>";

          //for(let f = 0; f < campsites[s].features.length; f++) {
          //	campsitehtml = campsitehtml + "<div class='product-availablity-features'>"+campsites[s].features[f].name+"</div>";
          //}

          //campsitehtml = campsitehtml + "</div>";
          campsitehtml =
            campsitehtml +
            "<div class='product-availablity-short-description'>" +
            campsites[s].short_description +
            "</div>";

          if (campsites[s].hasOwnProperty("warning")) {
            campsitehtml =
              campsitehtml +
              "<div id='campsite-warning-" +
              campsites[s].id +
              "' class='campsite-warning'>" +
              campsites[s].warning +
              "</div>";
          } else {
            campsitehtml =
              campsitehtml +
              "<div id='campsite-warning-" +
              campsites[s].id +
              "'>&nbsp;</div>";
          }

          campsitehtml = campsitehtml + "<div class='row'>";
          campsitehtml = campsitehtml + "<div class='col-3'>";

          campsitehtml =
            campsitehtml +
            "<button class='btn btn-dark product-availablity-status' te='product-availablity-status product-availablity-selection-green' onfocus='search_avail.show_avail_by_day(" +
            campsites[s].id +
            ")'>Check Availability</button>";
          // if (campsite_available == true) {

          //         if (append_site == true) {
          // 	          campsitehtml = campsitehtml + "<button class='btn btn-dark product-availablity-status' te='product-availablity-status product-availablity-selection-green' onfocus='search_avail.show_avail_by_day("+campsites[s].id+")'>Check Availability</button>";
          //                      } else {
          // 	  campsitehtml = campsitehtml + "<i class='bi bi-slash-square-fill product-availablity-status product-availablity-selection-grey' ></i>";
          //      }
          // } else {
          //          campsitehtml = campsitehtml + "<i class='bi bi-x-square-fill product-availablity-status product-availablity-selection-red' ></i>";
          // }

          campsitehtml =
            campsitehtml +
            "<div id='campsite-availablity-by-day" +
            campsites[s].id +
            "' class='product-available-dates-box' >";
          campsitehtml = campsitehtml + "<h4>Availablity</h4>";
          campsitehtml =
            campsitehtml +
            "<table cellpadding='0' cellspacing='0' style=''><tr>";
          var availloop = 0;
          for (let a = 0; a < campsites[s].availability.length; a++) {
            var da = campsites[s].availability[a][5];
            var dasplit = da.split("-");
            var avail_calender = "product-available-date-noavail";

            if (campsites[s].availability[a][0] == true) {
              avail_calender = "product-available-date-avail";
            }

            campsitehtml =
              campsitehtml +
              "<td class='product-available-date " +
              avail_calender +
              "'>" +
              dasplit[2] +
              "/" +
              dasplit[1] +
              "</td>";
            availloop = availloop + 1;
            if (availloop > 4) {
              campsitehtml = campsitehtml + "</tr><tr>";
              availloop = 0;
            }
          }

          campsitehtml = campsitehtml + "</tr></table>";
          campsitehtml = campsitehtml + "</div>";
          campsitehtml = campsitehtml + "</div>";

          campsitehtml =
            campsitehtml + "<div class='col-9 product-available-price-box'>";
          campsitehtml = campsitehtml + "<div class='" + priceavail + "'>";
          if (campsite_available == true && append_site == true) {
            campsitehtml =
              campsitehtml + "  AUD: $" + campsite_price.toFixed(2);
          } else {
            campsitehtml = campsitehtml + "&nbsp;&nbsp;";
          }
          campsitehtml = campsitehtml + "</div>";

          if (campsite_available == true) {
            var key_id = 0;
            if (campsites[s].site_type == 0) {
              key_id = campsites[s].id;
            } else {
              key_id = campground_id;
            }

            var buttondata = {
              site_type: site_type,
              campsite_id: campsites[s].id,
              campground_id: campground_id,
              campsite_class_id: campsites[s].type,
              selecttype: "single",
            };
            var buttondatamany = buttondata;
            buttondatamany["selecttype"] = "multiple";
            var databutton = JSON.stringify(buttondata);
            var databuttonmany = JSON.stringify(buttondatamany);
            var cs_status = "unknown";

            if (append_site == true) {
              if (search_avail.var.mcs_enabled == true) {
                if (
                  search_avail.var.multiplesites.indexOf(campsites[s].id) !== -1
                ) {
                  cs_status = "selected";
                  var mulitpleselect_class_count = 1;
                  if (
                    campsites[s].type in
                    search_avail.var.multiplesites_class_totals
                  ) {
                    mulitpleselect_class_count =
                      search_avail.var.multiplesites_class_totals[
                        campsites[s].type
                      ];
                  }
                  if (search_avail.var.site_type == 0) {
                  } else {
                    campsitehtml =
                      campsitehtml +
                      "<input type='number' value='" +
                      mulitpleselect_class_count +
                      "' onchange='search_avail.change_multiselect_class_total(" +
                      campsites[s].type +
                      ",this.value, " +
                      campsites[s].site_left +
                      ")' style='width:40px' max='" +
                      campsites[s].site_left +
                      "' min='1' id='multipleselect_class_count-" +
                      campsites[s].type +
                      "' >&nbsp;";
                  }

                  campsitehtml =
                    campsitehtml +
                    "<button type='button' class='btn btn-warning' id='bookingcampsite' data-button='" +
                    databuttonmany +
                    "'   onclick='search_avail.delete_multiple_site(this)' +key_id++site_type+ ><i class='bi bi-check-circle-fill'></i> UNSELECT</button>&nbsp;";
                  if (search_avail.var.site_type == 0) {
                  } else {
                    campsitehtml =
                      campsitehtml +
                      "<br><span style='border: 1px solid #d7d7d7;background-color: #ffffff;font-size: 10px;padding:0;'>" +
                      campsites[s].site_left +
                      " available</span>";
                  }
                } else {
                  campsitehtml =
                    campsitehtml +
                    "<button type='button' class='btn btn-primary' id='bookingcampsite' data-button='" +
                    databuttonmany +
                    "'   onclick='search_avail.select_multiple_site(this)' +key_id++site_type+ >Select</button>&nbsp;";
                }
              } else {
                campsitehtml =
                  campsitehtml +
                  "<button type='button' class='btn btn-success' id='bookingcampsite' data-button='" +
                  databutton +
                  "'   onclick='search_avail.create_booking(this)' +key_id++site_type+ >";
                if (change_booking_after_arrival_before_departure == "True") {
                  campsitehtml = campsitehtml + "Change Now";
                } else {
                  campsitehtml = campsitehtml + "Book Now";
                }
                campsitehtml = campsitehtml + "</button>";
                cs_status = "free";
              }
            } else {
              campsitehtml =
                campsitehtml +
                "<button type='button' class='btn btn-secondary avail-font-bold' id='bookingcampsite' >NO MATCH</button>";
              cs_status = "nomatch";
            }
          } else {
            if (append_site == true) {
              campsitehtml =
                campsitehtml +
                "<button type='button' class='btn btn-danger avail-font-bold' id='bookingcampsite' >Not Available</button>";
              cs_status = "notavailable";
            } else {
              campsitehtml =
                campsitehtml +
                "<button type='button' class='btn btn-secondary avail-font-bold' id='bookingcampsite' >NO MATCH</button>";
              cs_status = "noavailablenotmatch";
            }
          }

          campsitehtml = campsitehtml + "</div>";
          campsitehtml = campsitehtml + "</div>";
          //  current_booking_campsite_id
          campsitehtml = campsitehtml + "</center></div>";
          // campsitehtml = campsitehtml + "</div>";

          //if (search_avail.var.campers['total_people'] >= campsites[s].min_people && search_avail.var.campers['total_people']  <= campsites[s].max_people) {
          //} else {
          //        append_site = false;
          //}

          //if (append_site == true) {
          //     var gearType = campsites[s].gearType;
          //
          //     if (tents == true && gearType.tent == false) {
          //                append_site = false;
          //     }

          //     if (campervan == true && gearType.campervan == false) {
          //                append_site = false;
          //     }

          //     if (campertrailer == true && gearType.caravan == false) {
          //                append_site = false;
          //     }
          // }

          // if (append_site == true) {
          //     var campsite_features = campsites[s].features;
          //     var feats = new Set(campsite_features.map(function(x) {
          //         return x.id;
          //     }));

          //     for (var x of features_checked) {
          //	   if (!feats.has(x)) {
          //		append_site = false;
          //	   }

          //     }
          // }
          if (current_booking_selection == true) {
            campsitehtmlbeforeselected =
              campsitehtmlbeforeselected + campsitehtml;
          } else {
            if (change_booking_after_arrival_before_departure == "True") {
            } else {
              if (append_site == true) {
                if (campsite_available == true) {
                  campsitehtmlbefore = campsitehtmlbefore + campsitehtml;
                } else {
                  campsitehtmlmiddlestart =
                    campsitehtmlmiddlestart + campsitehtml;
                  //     campsitehtmlafter= campsitehtmlafter + campsitehtml;
                }
              } else {
                if (campsite_available == true) {
                  campsitehtmlafter = campsitehtmlafter + campsitehtml;
                  // campsitehtmlmiddlestart= campsitehtmlmiddlestart + campsitehtml;
                } else {
                  campsitehtmlmiddleend = campsitehtmlmiddleend + campsitehtml;
                }

                ////campsitehtmlmiddle= campsitehtmlmiddle + campsitehtml;
              }
            }
          }
        }
        var campsiteresultserror = "";
        if (
          campsitehtmlbeforeselected == "" &&
          campsitehtmlbefore == "" &&
          campsitehtmlafter == "" &&
          campsitehtmlmiddlestart == "" &&
          campsitehtmlmiddleend == ""
        ) {
          campsiteresultserror =
            "<center><span style='color:red; font-weight:bold;'>Sorry, there was no results matching your filter selection.</span></center>";
        }

        $("#campsite-availablity-results").html(
          "<div class='row align-items-center'>" +
            campsiteresultserror +
            campsitehtmlbeforeselected +
            campsitehtmlbefore +
            campsitehtmlmiddlestart +
            campsitehtmlmiddleend +
            campsitehtmlafter +
            "</div>"
        );
      },
    });
  },
  search_availabilty_locations: function () {},
  eventPath: function (evt) {
    var path = (evt.composedPath && evt.composedPath()) || evt.path,
      target = evt.target;

    if (path != null) {
      // Safari doesn't include Window, but it should.
      return path.indexOf(window) < 0 ? path.concat(window) : path;
    }

    if (target === window) {
      return [window];
    }

    function getParents(node, memo) {
      memo = memo || [];
      var parentNode = node.parentNode;

      if (!parentNode) {
        return memo;
      } else {
        return getParents(parentNode, memo.concat(parentNode));
      }
    }

    return [target].concat(getParents(target), window);
  },
  bellflash: function () {
    var current_class = $("#bell-flash").attr("class");
    if (current_class == "bi-bell-fill") {
      $("#bell-flash").attr("class", "bi-bell");
    } else {
      $("#bell-flash").attr("class", "bi-bell-fill");
    }
    setTimeout("search_avail.bellflash();", 1000);
  },
  init_cg: function () {
    if (
      search_avail.var.loaded.locations == false ||
      search_avail.var.loaded.search_locations == false ||
      search_avail.var.loaded.places == false
    ) {
      $("#LoadingPopup").modal("show");
      setTimeout("search_avail.init_cg()", 1000);
    } else {
      var queryString = window.location.search;
      var urlParams = new URLSearchParams(queryString);
      var DEFAULT_SEARCH_AVAILABILITY_LOCATION = $(
        "#DEFAULT_SEARCH_AVAILABILITY_LOCATION"
      ).val();
      var campground_id = urlParams.get("campground_id");
      if (campground_id != null) {
        search_avail.select_campground_id(parseInt(campground_id));
      } else {
        if (DEFAULT_SEARCH_AVAILABILITY_LOCATION > 0) {
          search_avail.select_place_id(
            parseInt(DEFAULT_SEARCH_AVAILABILITY_LOCATION)
          );
        }
      }

      $("#LoadingPopup").modal("hide");
    }
  },
  init: function () {
    var enodes = [];
    search_avail.bellflash();

    //$('#departure-date').datepicker({
    //    format: 'dd/mm/yyyy',
    //    startDate : '+1d',
    //});

    //$('#departure-date').change(function(){
    //       console.log("input's current value: " + this.value);
    //       var date_split = this.value.split("/");
    //       search_avail.init_dateselection($('#checkin').val(), date_split[2]+"/"+date_split[1]+"/"+date_split[0])
    //});

    $(document).on("click", function (event) {
      var closedropdowns = true;
      var $target = $(event.target);
      enodes = [];
      enodes = search_avail.eventPath(event);
      if (typeof enodes === "undefined") {
        enodes = [];
      }

      for (let i = 0; i < enodes.length; i++) {
        if ("classList" in enodes[i]) {
          if ("value" in enodes[i].classList) {
            var classlist_path = enodes[i].classList.value.split(" ");
            for (let c = 0; c < classlist_path.length; c++) {
              if ("selection-dropdown" == classlist_path[c]) {
                closedropdowns = false;
              }
              if ("selection-informbox" == classlist_path[c]) {
                closedropdowns = false;
              }
            }
          }
        }
      }

      if (closedropdowns == true) {
        search_avail.close_dropdowns();
      }
    });

    $("#multiple-campsite-selection").on("click", function () {
      search_avail.var.mcs_enabled = $(this).is(":checked");
      if (search_avail.var.mcs_enabled == true) {
        $("#proceed-booking").show();
        search_avail.var.selecttype = "multiple";
      } else {
        $("#proceed-booking").hide();
        search_avail.var.selecttype = "single";
      }
      search_avail.load_campsite_availabilty();
    });

    $("#date-override").on("click", function () {
      var dateoverride = $("#date-override").is(":checked");
      search_avail.var.date_override = dateoverride;
      search_avail.init_dateselection(
        search_avail.var.arrival,
        search_avail.var.departure
      );
    });
  },
  update_dates_search_params: function (arrival, departure) {
    const url = new URL(window.location);
    url.searchParams.set("arrival", arrival);
    url.searchParams.set("departure", departure);
    history.pushState(null, "", url);
  },
  get_dates_from_params: function () {
    const urlParams = new URLSearchParams(window.location.search);
    const dates = {
      arrival: undefined,
      departure: undefined,
    };
    try {
      const arrival = urlParams.get("arrival");
      const departure = urlParams.get("departure");
      dates.arrival = isNaN(Date.parse(arrival)) ? undefined : arrival;
      dates.departure = isNaN(Date.parse(departure)) ? undefined : departure;
    } catch (error) {
      console.log(error);
    }
    return dates;
  },
  focus_map: function () {
    if($("#map-preview-tab").hasClass("active")) {
        document.getElementById('search-filters').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  },
  showMapLoader: function () {
      $('#map-preview').find('.loading-map').show();
      $('#map-preview').find('.map-container').css('opacity', '0.5');
  },
  hideMapLoader: function () {
      $('#map-preview').find('.loading-map').hide();
      $('#map-preview').find('.map-container').css('opacity', '1');
  },
};
