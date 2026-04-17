var management = {
    var: {
	    'csrf_token': null,
	    'test': 'test',	  
        'peak_groups': [], 
        'bulk_refund_cancel' : [],
        'peak_groups_url': '/api/peak_groups/',
        'peak_groups_save_url' : '/api/save_peak_group/',
        'peak_periods_url': '/api/peak_periods/',
        'peak_period_save_url': '/api/save_peak_period/',
        'bulk_refund_url': '/api/bulk_refund/',
        'bulk_refund_save_url': '/api/save_bulk_refund_period/',        
        //'peak_periods_save_url' : '',
	    'booking_policy_url': '/api/booking_policy/',
        'booking_policy_save_url' : '/api/save_booking_policy/',
	    'booking_policy_id_selected': null,
        'peak_period_collapsed_id' : null,
        'peak_group_collapsed_id' : null,
	    'peak_group_id_selection' : null
    },
    load_peak_periods: function(peakgroup_id) {
	        console.log('load_peak_periods');
	        management.var.peak_group_id_selection = peakgroup_id;
                $('#peak-periods-tbody').html('<tr><td colspan=5 align="center"><div class="spinner-border text-primary" role="status"> <span class="visually-hidden">Loading...</span></div></td></tr>');
                $.ajax({
                    url: management.var.peak_periods_url+"?peakgroup_id="+peakgroup_id,
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    success: function (response) {
			var html = '';
                        if (response.length > 0) {
                              for (let i = 0; i < response.length; i++) {
                                  html+= "<tr>";
                                  html+= " <td>"+response[i].id+"</td>";
                                  html+= " <td>"+response[i].start_date+"</td>";
                                  html+= " <td>"+response[i].end_date+"</td>";
                                  html+= " <td class='text-center'>";

                                  if (response[i].active == true) {
                                     html+= '<i style="color: #00f300" class="bi bi-check-circle-fill"></i>';
                                  } else {
                                     html+= '<i style="color: #f30000" class="bi bi-x-circle-fill"></i>';
                                  }

                                  html+= "</td>";
				  html+= "<td align='right'>";
				  var buttondata='{"peakperiod_id": '+response[i].id+'}';
                                  var buttondata_delete='{"peakperiod_id": '+response[i].id+', "action" : "delete"}';
				  html+= "<button type='button' class='btn btn-primary btn-sm peakrow' button-data='"+buttondata+"' >Edit</button>";
                                  html+= "&nbsp;<button type='button' class='btn btn-danger btn-sm peaksave' button-data='"+buttondata_delete+"' >Delete</button>";
                                  html+= '&nbsp;&nbsp;<div class="spinner-border text-primary" role="status" style="display:none" id="peakperiod-loader-'+response[i].id+'">';
                                  html+= '<span class="visually-hidden">Loading...</span>';
                                  html+= '</div>';
				  html+= "</td>";
                                  html+= "</tr>";

                                  // edit collapse start
				  html+= "<tr style='display:none' id='rowcollapse-"+response[i].id+"'>";
				  html+= "<td>";
                                  html+= "&nbsp;";
				  html+= "</td>";
				  html+= "<td>";
                                  html+= '<input type="text" class="form-control bs-datepicker" id="row-start-date-'+response[i].id+'" value="'+response[i].start_date+'">';
				  html+= "</td>";
                                  html+= "<td>";
                                  html+= '<input type="text" class="form-control bs-datepicker" id="row-end-date-'+response[i].id+'" value="'+response[i].end_date+'">';
                                  html+= "</td>";
			          html+= "<td>";
                                  html+= "";
                                  html+= '<select class="form-select" aria-label="" id="row-active-'+response[i].id+'">';
                                  html+= '<option value="true"';

				  if (response[i].active == true) { 
				     html+= ' selected ';
			          }

			          html+= '>Active</option>';
                                  html+= '<option value="false"';
				  if (response[i].active == false) {
                                     html+= ' selected ';
				  }

				  html+= '>Inactive</option>';
                                  html+= '</select>';
                                  html+= "</td>";
				  html+= "<td align='right'>";

				  var buttondata='{"peakperiod_id": '+response[i].id+'}';
                                  //html+= '<div class="spinner-border text-primary" role="status" style="display:none" id="peakperiod-loader-'+response[i].id+'">';
                                  //html+= '<span class="visually-hidden">Loading...</span>';
                                  //html+= '</div>&nbsp;&nbsp;&nbsp;';
                                  html+= "<button type='button' class='btn btn-success btn-sm peaksave' button-data='"+buttondata+"' >Save</button>";
				  html+= "</td>";
				  html+= "</tr>";
				  
				  // edit collapse end

			      }
 
                              $('#peak-periods-tbody').html(html);
                              $( ".peakrow" ).click(function() {
                                         
                                    if (management.var.peak_period_collapsed_id != null) {
			                    $('#rowcollapse-'+management.var.peak_period_collapsed_id).hide();			
				    }


                                    var buttondata = $(this)[0].attributes['button-data'].value;
                                    var buttondata_obj = JSON.parse(buttondata);
                                    $('#rowcollapse-'+buttondata_obj['peakperiod_id']).show();
                                    management.var.peak_period_collapsed_id = buttondata_obj['peakperiod_id'];
                              });

			      $( ".peaksave" ).click(function() {
				        console.log('peaksave');				      
					var buttondata = $(this)[0].attributes['button-data'].value;
				        var buttondata_obj = JSON.parse(buttondata);

				        console.log(buttondata);
				        management.save_peak_period(buttondata_obj);
			      });
		              $('.bs-datepicker').datepicker({"format": "dd/mm/yyyy"});		
                        } else {
                              $('#peak-periods-tbody').html("<tr><td colspan='4' class='text-center'>No results found<td></tr>");
                        }
		       
			console.log(response);
                    },
                    error: function (error) {
		        $('#period-popup-error').html("Error Loading peak periods");
			$('#period-popup-error').show();
			$('#peak-periods-tbody').html('');

                        console.log('Error loading peak periods');
                    },
                });
    },
    load_booking_policy_options: function() { 
                $.ajax({
                    url: management.var.peak_groups_url,
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    // data: "{}",
                    success: function (response) {
                          management.var.peak_groups = response;
                    },
                    error: function (error) {
                        console.log('Error loading peak groups');
                    },
                });
    },
    load_booking_refund_cancel_options: function() {         
                $.ajax({
                    url: management.var.bulk_refund_url,
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    // data: "{}",
                    success: function (response) {
                          management.var.bulk_refund_cancel = response;
                    },
                    error: function (error) {
                        console.log('Error loading bulk refund cancel');
                    },
                });
    },
    load_booking_refund_cancel: function() {
        
	        $('#booking-refund-cancel-tbody').html('<tr><td colspan=5 align="center"><div class="spinner-border text-primary" role="status"> <span class="visually-hidden">Loading...</span></div></td></tr>');
	        $('#peakgroup_progress_loader').hide();
	        $("#group-name").prop('disabled', false);
	        $('#peak-status').prop('disabled', false);

                $.ajax({
                    url: management.var.bulk_refund_url,
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    // data: "{}",
                    success: function (response) {
			var html ='';
			if (response.length > 0) { 
                            for (let i = 0; i < response.length; i++) {
                                    html+= "<tr>";
                                    html+= " <td>"+response[i].id+"</td>";
                                    html+= "      <td>"+response[i].bulk_name+"</td>";
                                    html+= "      <td>";

                                    if (response[i].paused == true) {
                                        html+= '        <i style="color: #5614a1" class="bi bi-stop-circle-fill"></i>';
                                    } else {

                                        if (response[i].bulk_status == 2) {
                                            html+= '        <i style="color: #00f300" class="bi bi-check-circle-fill"></i>';
                                        } else if (response[i].bulk_status == 1) {
                                            html+= '        <i style="color: #0229d4" class="bi bi-play-circle-fill"></i>';
                                        } else if (response[i].bulk_status == 0) {
                                            html+= '        <i style="color: #f5c730" class="bi bi-dash-circle-fill"></i>';                                        
                                        } else {
                                            html+= '        <i style="color: #f30000" class="bi bi-x-circle-fill"></i>';
                                        }
                                    }

                                    html+= "           </td>";
                                    html+= "           <td class='text-end'>";
                                    var data_button = '{"id": '+response[i].id+'}';
                                    var data_button_delete = '{"group_id": '+response[i].id+', "action": "delete"}';
                                    html+= "          <button type='button' class='btn btn-primary btn-sm' data-bs-backdrop='static' data-keyboard='false' data-bs-toggle='modal' data-bs-target='#ViewPeakPeriodModal' data-button='"+data_button+"' >Check Processing</button>";                                    
				                    html+= "           <button class='btn btn-danger btn-sm peakgroupsave' button-data='"+data_button_delete+"' >Pause</button>";
                                    html+= '&nbsp;&nbsp;<div class="spinner-border text-primary" role="status" style="display:none" id="peakgroup-loader-'+response[i].id+'">';
                                    html+= '<span class="visually-hidden">Loading...</span>';
                                    html+= '</div>';

                                    html+= "           </td>";
                                    html+= "       </tr>";
                                  
                                    // save start
                                    html+= "<tr style='display:none' id='pg-rowcollapse-"+response[i].id+"'>";
                                    html+= "<td>";
                                    html+= "&nbsp;";
                                    html+= "</td>";

                                    html+= "<td>";
                                    html+= '<input type="text" class="form-control" id="row-group-name-'+response[i].id+'" value="'+response[i].name+'">';
                                    html+= "</td>";
                                    html+= "<td>";
                                    html+= "";
                                    html+= '<select class="form-select" aria-label="" id="row-group-active-'+response[i].id+'">';
                                    html+= '<option value="true"';

                                    if (response[i].active == true) {
                                        html+= ' selected ';
                                    }

                                    html+= '>Active</option>';
                                    html+= '<option value="false"';
                                    if (response[i].active == false) {
                                        html+= ' selected ';
                                    }

                                    html+= '>Inactive</option>';
                                    html+= '</select>';
                                    html+= "</td>";
                                    html+= "<td align='right'>";

                                    var buttondata='{"group_id": '+response[i].id+', "action": "save"}';
                                    //html+= '<div class="spinner-border text-primary" role="status" style="display:none" id="peakgroup-loader-'+response[i].id+'">';
                                    //html+= '<span class="visually-hidden">Loading...</span>';
                                    //html+= '</div>&nbsp;&nbsp;&nbsp;';
                                    html+= "<button type='button' class='btn btn-success btn-sm peakgroupsave' button-data='"+buttondata+"' >Save</button>";
                                    html+= "</td>";
                                    html+= "</tr>";
                                    // save end
		            }

			    $('#booking-refund-cancel-tbody').html(html);

                            $(".peakgroup-row" ).click(function() {

                                  if (management.var.peak_group_collapsed_id != null) {
                                          $('#pg-rowcollapse-'+management.var.peak_group_collapsed_id).hide();
                                  }

                                  console.log($(this)[0].attributes);
                                  var buttondata = $(this)[0].attributes['data-button'].value;
                                  var buttondata_obj = JSON.parse(buttondata);
                                  $('#pg-rowcollapse-'+buttondata_obj['id']).show();
                                  management.var.peak_group_collapsed_id = buttondata_obj['id'];
                            });

                            $(".peakgroupsave" ).click(function() {
                                      console.log('peakgroupsave');
                                      var buttondata = $(this)[0].attributes['button-data'].value;
                                      var buttondata_obj = JSON.parse(buttondata);

                                      console.log(buttondata);
                                      management.save_peak_group(buttondata_obj);
                            });

		 	} else {
				$('#peak-groups-tbody').html("<tr><td colspan='4' class='text-center'>No results found<td></tr>");
			}
                    },
                    error: function (error) {
                        console.log('Error loading peak groups');
                    },
                });
    },
    load_booking_policys: function() {
	console.log("LOAD");
	$('#booking-policy-tbody').html('<tr><td colspan=5 align="center"><div class="spinner-border text-primary" role="status"> <span class="visually-hidden">Loading...</span></div></td></tr>');

	$('#bookingpolicy_progress_loader').hide();
        $.ajax({
            url: management.var.booking_policy_url,
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            // data: "{}",
            success: function (response_data) {
                var html ='';
                response = response_data['dataitems'];
		policy_types = response_data['policy_types'];

                if (response.length > 0) {
                    for (let i = 0; i < response.length; i++) {    

                          html+= "<tr>";
                          html+= " <td>"+response[i].id+"</td>";
                          html+= " <td>"+response[i].policy_name+"</td>";

                          html+= " <td class='text-left' align='left'>";

                          if (response[i].active == true) {
                             html+= '<i style="color: #00f300" class="bi bi-check-circle-fill"></i>';
                          } else {
                             html+= '<i style="color: #f30000" class="bi bi-x-circle-fill"></i>';
                          }

                          html+= "</td>";
                          html+= "<td align='right'>";
                          var buttondata='{"policy_id" : '+response[i].id+', "no_policy" : "'+response[i].no_policy+'" ,"policy_name" : "'+response[i].policy_name+'","policy_amount": "'+response[i].amount+'", "policy_type" : "'+response[i].policy_type+'","active": "'+response[i].active+'", "grace_time": "'+response[i].grace_time+'","peak_policy_enabled": "'+response[i].peak_policy_enabled+'","peak_policy_type": "'+response[i].peak_policy_type+'","peak_group": "'+response[i].peak_group+'","peak_amount":"'+response[i].peak_amount+'", "peak_grace_time": "'+response[i].peak_grace_time+'","policy_types_list": '+JSON.stringify(policy_types)+',"arrival_limit_enabled": "'+response[i].arrival_limit_enabled+'", "arrival_time" : "'+response[i].arrival_time+'", "peak_arrival_limit_enabled" : "'+response[i].peak_arrival_limit_enabled+'", "peak_arrival_time":"'+response[i].peak_arrival_time+'"  }';
                          var buttondata_delete='{"policy_id": '+response[i].id+', "action" : "delete"}';
                          html+= "<button type='button' class='btn btn-primary btn-sm edit-booking-policy' button-data='"+buttondata+"' >Edit</button>";
                          html+= "&nbsp;<button type='button' class='btn btn-danger btn-sm booking-policy-delete' button-data='"+buttondata_delete+"' >Delete</button>";
                          html+= '&nbsp;&nbsp;<div class="spinner-border text-primary" role="status" style="display:none" id="peakperiod-loader-'+response[i].id+'">';
                          html+= '<span class="visually-hidden">Loading...</span>';
                          html+= '</div>';
                          html+= "</td>";
                          html+= "</tr>";

                    }
                    $('#booking-policy-tbody').html(html);

                    $( ".booking-policy-delete" ).click(function() {
                    	  console.log('booking-policy-delete');
                    	  var buttondata = $(this)[0].attributes['button-data'].value;
                    	  var buttondata_obj = JSON.parse(buttondata);
			  
                          management.var.booking_policy_id_selected = buttondata_obj['policy_id'] 
                    	  console.log(buttondata);
                    	  management.save_booking_policy(buttondata_obj);
                    });
                    

                    // open edit popup start
                    $(".edit-booking-policy" ).click(function() {
			  $('#create-policy-btn').hide();
			  $('#save-policy-btn').show();
			  $('#bookingpolicy-loader-popup').hide();
			  $('#EditBookingPolicyModal').modal('show');
			  var nopolicy = $('#no-policy');
                          var policyname = $('#policy-name');
                          var policytype = $('#policy-type');
                          var policyamount = $('#policy-amount');
                          var policygracetime = $('#policy-grace-time');
                          var peakpolicyenabled = $('#peak-policy-enabled');

                          var peakpolicytype = $('#peak-policy-type');
                          var peakpolicygroup = $('#peak-policy-group');
                          var peakpolicyamont = $('#peak-policy-amont');
                          var peakpolicygracetime = $('#peak-policy-grace-time');
                          var policyactive = $('#policy-active');

                          var policyarrivalenabled = $('#policy-arrival-enabled');
		          var policyarrivaltime = $('#policy-arrival-time');

		          var peakpolicyarrivalenabled = $('#peak-policy-arrival-enabled');
		          var peakpolicyarrivaltime = $('#peak-policy-arrival-time');

			  nopolicy.prop('disabled', false);
                          policyname.prop('disabled', false);
                          policytype.prop('disabled', false);
                          policyamount.prop('disabled', false);
                          policygracetime.prop('disabled', false);
                          peakpolicyenabled.prop('disabled', false);
                          peakpolicytype.prop('disabled', false);
                          peakpolicygroup.prop('disabled', false);
                          peakpolicyamont.prop('disabled', false);
                          peakpolicygracetime.prop('disabled', false);
                          policyactive.prop('disabled', false);

                          policyarrivalenabled.prop('disabled', false);
			  policyarrivaltime.prop('disabled', false);

                          peakpolicyarrivalenabled.prop('disabled', false);
			  peakpolicyarrivaltime.prop('disabled', false);


                          var buttondata = $(this)[0].attributes['button-data'].value;
                          var buttondata_obj = JSON.parse(buttondata);

			  if (buttondata_obj['no_policy'] == 'true') {
                                $('#no-policy').prop('checked', true);
				$('#booking-policy-details').hide();
		          } else {
                                nopolicy.prop('checked', false);
				$('#booking-policy-details').show();
			  }

			  if (buttondata_obj['peak_policy_enabled'] == 'true') {
				$('#peak-policy-enabled').prop('checked', true);
			        $("#peak-policy-options").show();
		          } else {
                                $('#peak-policy-enabled').prop('checked', false);
				$("#peak-policy-options").hide();
			  }
                          if (buttondata_obj['arrival_limit_enabled'] == 'true') {
                                $('#policy-arrival-enabled').prop('checked', true);
                          } else {
                                $('#policy-arrival-enabled').prop('checked', false);
                          }
                          if (buttondata_obj['peak_arrival_limit_enabled'] == 'true') {
                                $('#peak-policy-arrival-enabled').prop('checked', true);
                          } else {
                                $('#peak-policy-arrival-enabled').prop('checked', false);
                          }


                          $('#policy-name').val(buttondata_obj['policy_name']);
			  $('#policy-amount').val(buttondata_obj['policy_amount']);
			  $('#policy-grace-time').val(buttondata_obj['grace_time']);
			  $('#peak-policy-amont').val(buttondata_obj['peak_amount']);
                          $('#peak-policy-grace-time').val(buttondata_obj['peak_grace_time']);
			  $('#policy-active').val(buttondata_obj['active']);

			  //$('#policy-arrival-enabled').val(buttondata_obj['arrival_limit_enabled']);
                          $('#policy-arrival-time').val(buttondata_obj['arrival_time']);
			  //$('#peak-policy-arrival-enabled').val(buttondata_obj['peak_arrival_limit_enabled']);
                          $('#peak-policy-arrival-time').val(buttondata_obj['peak_arrival_time']);
			  // policy_types_list = JSON.parse(buttondata_obj['policy_types_list']);
			  //var policy_types_list = buttondata_obj['policy_types_list'];
			  //var policy_type_html ="";
                          //for (let i = 0; i < policy_types_list.length; i++) {
			  //       policy_type_html = policy_type_html + "<option value='"+buttondata_obj['policy_types_list'][i]['id']+"'>"+buttondata_obj['policy_types_list'][i]['name']+"</option>";
                          //       console.log(buttondata_obj['policy_types_list'][i]);
			  //}
			  //$("#peak-policy-type").html(policy_type_html);
			  //$("#policy-type").html(policy_type_html);
			  $("#policy-type").val(buttondata_obj['policy_type']);
                          $('#peak-policy-type').val(buttondata_obj['peak_policy_type']);

                          //var edit_policy_group_html = '';
                          //for (let i = 0; i < management.var.peak_groups.length; i++) {
                          //          edit_policy_group_html = edit_policy_group_html + "<option value='"+management.var.peak_groups[i].id+"'>"+management.var.peak_groups[i].name+"</option>";
		          //}
                          //$('#peak-policy-group').html(edit_policy_group_html);
			  $('#peak-policy-group').val(buttondata_obj['peak_group']);
                          management.var.booking_policy_id_selected = buttondata_obj['policy_id']
                          //$('#pg-rowcollapse-'+buttondata_obj['id']).show();
                    });
                    // open edit popup end


                } else {
  			$('#booking-policy-tbody').html("<tr><td colspan='3' class='text-center'>No results found<td></tr>");

	 	}
                    var policy_types_list = policy_types;
                    var policy_type_html ="";
                    for (let i = 0; i < policy_types_list.length; i++) {
                           policy_type_html = policy_type_html + "<option value='"+policy_types_list[i]['id']+"'>"+policy_types_list[i]['name']+"</option>";
                    }

                    $("#peak-policy-type").html(policy_type_html);
                    $("#policy-type").html(policy_type_html);

                    var edit_policy_group_html = '';
                    for (let i = 0; i < management.var.peak_groups.length; i++) {
                              edit_policy_group_html = edit_policy_group_html + "<option value='"+management.var.peak_groups[i].id+"'>"+management.var.peak_groups[i].name+"</option>";
                    }
                    $('#peak-policy-group').html(edit_policy_group_html);

            },
            error: function (error) {
                console.log('Error loading peak groups');
            },
        });
    },
    load_peak_groups: function() {
	        $('#peak-groups-tbody').html('<tr><td colspan=5 align="center"><div class="spinner-border text-primary" role="status"> <span class="visually-hidden">Loading...</span></div></td></tr>');
	        $('#peakgroup_progress_loader').hide();
	        $("#group-name").prop('disabled', false);
	        $('#peak-status').prop('disabled', false);

                $.ajax({
                    url: management.var.peak_groups_url,
                    method: 'GET',
                    dataType: 'json',
                    contentType: 'application/json',
                    // data: "{}",
                    success: function (response) {
			var html ='';
			if (response.length > 0) { 
                            for (let i = 0; i < response.length; i++) {
                                  html+= "<tr>";
                                  html+= " <td>"+response[i].id+"</td>";
                                  html+= "      <td>"+response[i].name+"</td>";
                                  html+= "      <td>";

			          if (response[i].active == true) {
                                     html+= '        <i style="color: #00f300" class="bi bi-check-circle-fill"></i>';
			          } else {
                                     html+= '        <i style="color: #f30000" class="bi bi-x-circle-fill"></i>';
			          }

                                  html+= "           </td>";
                                  html+= "           <td class='text-end'>";
				  var data_button = '{"id": '+response[i].id+'}';
				  var data_button_delete = '{"group_id": '+response[i].id+', "action": "delete"}';
                                  html+= "          <button type='button' class='btn btn-primary btn-sm' data-bs-backdrop='static' data-keyboard='false' data-bs-toggle='modal' data-bs-target='#ViewPeakPeriodModal' data-button='"+data_button+"' >View Periods</button>";
                                  html+= "                <button class='btn btn-primary btn-sm peakgroup-row' data-button='"+data_button+"' >Edit</button>";
				  html+= "           <button class='btn btn-danger btn-sm peakgroupsave' button-data='"+data_button_delete+"' >Delete</button>";
                                  html+= '&nbsp;&nbsp;<div class="spinner-border text-primary" role="status" style="display:none" id="peakgroup-loader-'+response[i].id+'">';
                                  html+= '<span class="visually-hidden">Loading...</span>';
                                  html+= '</div>';

                                  html+= "           </td>";
                                  html+= "       </tr>";
                                  
				  // save start
                                  html+= "<tr style='display:none' id='pg-rowcollapse-"+response[i].id+"'>";
                                  html+= "<td>";
                                  html+= "&nbsp;";
                                  html+= "</td>";

                                  html+= "<td>";
                                  html+= '<input type="text" class="form-control" id="row-group-name-'+response[i].id+'" value="'+response[i].name+'">';
                                  html+= "</td>";
                                  html+= "<td>";
                                  html+= "";
                                  html+= '<select class="form-select" aria-label="" id="row-group-active-'+response[i].id+'">';
                                  html+= '<option value="true"';

                                  if (response[i].active == true) {
                                     html+= ' selected ';
                                  }

                                  html+= '>Active</option>';
                                  html+= '<option value="false"';
                                  if (response[i].active == false) {
                                     html+= ' selected ';
                                  }

                                  html+= '>Inactive</option>';
                                  html+= '</select>';
                                  html+= "</td>";
                                  html+= "<td align='right'>";

                                  var buttondata='{"group_id": '+response[i].id+', "action": "save"}';
                                  //html+= '<div class="spinner-border text-primary" role="status" style="display:none" id="peakgroup-loader-'+response[i].id+'">';
                                  //html+= '<span class="visually-hidden">Loading...</span>';
                                  //html+= '</div>&nbsp;&nbsp;&nbsp;';
                                  html+= "<button type='button' class='btn btn-success btn-sm peakgroupsave' button-data='"+buttondata+"' >Save</button>";
                                  html+= "</td>";
                                  html+= "</tr>";
                                  // save end
		            }

			    $('#peak-groups-tbody').html(html);

                            $(".peakgroup-row" ).click(function() {

                                  if (management.var.peak_group_collapsed_id != null) {
                                          $('#pg-rowcollapse-'+management.var.peak_group_collapsed_id).hide();
                                  }

                                  console.log($(this)[0].attributes);
                                  var buttondata = $(this)[0].attributes['data-button'].value;
                                  var buttondata_obj = JSON.parse(buttondata);
                                  $('#pg-rowcollapse-'+buttondata_obj['id']).show();
                                  management.var.peak_group_collapsed_id = buttondata_obj['id'];
                            });

                            $(".peakgroupsave" ).click(function() {
                                      console.log('peakgroupsave');
                                      var buttondata = $(this)[0].attributes['button-data'].value;
                                      var buttondata_obj = JSON.parse(buttondata);

                                      console.log(buttondata);
                                      management.save_peak_group(buttondata_obj);
                            });

		 	} else {
				$('#peak-groups-tbody').html("<tr><td colspan='4' class='text-center'>No results found<td></tr>");
			}
                    },
                    error: function (error) {
                        console.log('Error loading peak groups');
                    },
                });
    },
    save_booking_policy: function(buttondata_obj) {
	 console.log("save_booking_policy");

	 var nopolicy = $('#no-policy');
         var action = buttondata_obj['action'];
	 console.log(action);
	 var policy_id = management.var.booking_policy_id_selected;
         var policyname = $('#policy-name');
	 var policytype = $('#policy-type');
	 var policyamount = $('#policy-amount');
	 var policygracetime = $('#policy-grace-time');
	 var peakpolicyenabled = $('#peak-policy-enabled');

         var policyarrivalenabled = $('#policy-arrival-enabled');
	 var policyarrivaltime = $('#policy-arrival-time');

	 var peakpolicytype = $('#peak-policy-type');
	 var peakpolicygroup = $('#peak-policy-group');
	 var peakpolicyamont = $('#peak-policy-amont');
	 var peakpolicygracetime = $('#peak-policy-grace-time');
	 var policyactive = $('#policy-active');

	 var peakpolicyarrivalenabled = $('#peak-policy-arrival-enabled');
	 var peakpolicyarrivaltime = $('#peak-policy-arrival-time');

	 var ppe = 'false';
         if (peakpolicyenabled.is(":checked") == true ) { 
	    ppe='true';
	 }

	 var nop = 'false';
         if (nopolicy.is(":checked") == true) {
             nop = 'true';
	 }
         var pae = 'false';
	 if (policyarrivalenabled.is(":checked") == true) {
             pae = 'true';
	 }

	 var ppae = 'false';
	 if (peakpolicyarrivalenabled.is(":checked") == true) {
             ppae = 'true';
         }

         var data = {'action' : action, 'no_policy': nop, 'policy_id': policy_id, 'policyname': policyname.val(), 'policytype': policytype.val(), 'policyamount': policyamount.val(), 'policygracetime': policygracetime.val(),   'peakpolicyenabled': ppe, 'peakpolicytype': peakpolicytype.val(), 'peakpolicygroup': peakpolicygroup.val(), 'peakpolicyamont': peakpolicyamont.val(), 'peakpolicygracetime': peakpolicygracetime.val(), 'policyactive': policyactive.val(), 'policyarrivalenabled': pae, 'policyarrivaltime' : policyarrivaltime.val(), 'peakpolicyarrivalenabled': ppae, 'peakpolicyarrivaltime' : peakpolicyarrivaltime.val()};

         $('#booking-policy-popup-error').html('');
         $('#booking-policy-popup-error').hide();
         $('#bookingpolicy-loader-popup').show();

	 nopolicy.prop('disabled', true);
         policyname.prop('disabled', true);
         policytype.prop('disabled', true);
	 policyamount.prop('disabled', true);
	 policygracetime.prop('disabled', true);
	 peakpolicyenabled.prop('disabled', true);
	 peakpolicytype.prop('disabled', true);
	 peakpolicygroup.prop('disabled', true);
	 peakpolicyamont.prop('disabled', true);
	 peakpolicygracetime.prop('disabled', true);
	 policyactive.prop('disabled', true);

	 policyarrivalenabled.prop('disabled', true);
	 policyarrivaltime.prop('disabled', true);

	 peakpolicyarrivalenabled.prop('disabled', true);
	 peakpolicyarrivaltime.prop('disabled', true);

	 

         //$('#'+loader_id).show();
         //$('.peakrow').prop('disabled', true);
         //$("#"+start_id).prop('disabled', true);
         //$('#'+end_id).prop('disabled', true);
         //$('#'+active_id).prop('disabled', true);

         $.ajax({
             url: management.var.booking_policy_save_url,
             method: "POST",
             headers: {'X-CSRFToken' : management.var.csrf_token },
             data: JSON.stringify({'payload': data,}),
             contentType: "application/json",
             success: function(data) {
		   management.load_booking_policys();
		   $('#EditBookingPolicyModal').modal('hide');
                   //$('#'+loader_id).hide();
                   //$("#"+start_id).prop('disabled', false);
                   //$('#'+end_id).prop('disabled', false);
                   //$('#'+active_id).prop('disabled', false);
                   //$('.peakrow').prop('disabled',false);
                   $('#booking-policy-flat-success').html("Successfully Updated");
                   $('#booking-policy-flat-success').show();
                   setTimeout("$('#booking-policy-flat-success').fadeOut('slow');",3000);
		   $('#bookingpolicy-loader-popup').hide();
                   //management.load_peak_periods(management.var.peak_group_id_selection);
             },
             error: function(errMsg) {
		   $('#bookingpolicy-loader-popup').hide();
		   nopolicy.prop('disabled', false)  
                   policyname.prop('disabled', false);
		   policytype.prop('disabled', false);
		   policyamount.prop('disabled', false);
		   policygracetime.prop('disabled', false);
		   peakpolicyenabled.prop('disabled', false);
		   peakpolicytype.prop('disabled', false);
		   peakpolicygroup.prop('disabled', false);
		   peakpolicyamont.prop('disabled', false);
		   peakpolicygracetime.prop('disabled', false);
		   policyactive.prop('disabled', false);

                   policyarrivalenabled.prop('disabled', false);
	           policyarrivaltime.prop('disabled', false);

	           peakpolicyarrivalenabled.prop('disabled', false);
	           peakpolicyarrivaltime.prop('disabled', false);


                   //$('#'+loader_id).hide();
                   //$("#"+start_id).prop('disabled', false);
                   //$('#'+end_id).prop('disabled', false);
                   //$('#'+active_id).prop('disabled', false);
                   //$('.peakrow').prop('disabled',false);

                   $('#booking-policy-popup-error').html(errMsg.responseJSON.message);
                   $('#booking-policy-popup-error').show();
                   //management.load_peak_groups();
                   // alert(JSON.stringify(errMsg));
             }
         });



    },
    save_peak_period: function(buttondata_obj) {
	 var peakperiod_id = null;
	 var startdate = {'val': function(){return ''}, 'prop': function(){return false} };
         var enddate = {'val': function(){return ''}, 'prop': function(){return false} };
	 var active = {'val': function(){return ''}, 'prop': function(){return false} };
         var action = null;
         var loader_id = '';
	 var start_id = '';

         if (buttondata_obj['action'] == 'create') {
             action ='create';
	     startdate = $('#new-start-date');
	     enddate = $('#new-end-date');
	     active = $('#new-active');
	     loader_id = 'peakperiod-loader-create';
             start_id = 'new-start-date';
	     end_id = 'new-end-date';
	     active_id = 'new-active';
         } else if (buttondata_obj['action'] == 'delete') {
	     action = 'delete'
	     peakperiod_id = buttondata_obj['peakperiod_id'];
             loader_id = 'peakperiod-loader-'+peakperiod_id;
	     start_id = 'row-start-date-'+peakperiod_id;
	     end_id = 'row-end-date-'+peakperiod_id;
	     active_id = 'row-active-'+peakperiod_id;
         } else {
             action = 'save';
	     peakperiod_id = buttondata_obj['peakperiod_id'];
             startdate = $('#row-start-date-'+peakperiod_id);
	     enddate = $('#row-end-date-'+peakperiod_id);
	     active = $('#row-active-'+peakperiod_id);
             loader_id = 'peakperiod-loader-'+peakperiod_id;
	     start_id = 'row-start-date-'+peakperiod_id;
	     end_id = 'row-end-date-'+peakperiod_id;
	     active_id = 'row-active-'+peakperiod_id;
         } 

	 var data = {'action' : action, 'period_id': peakperiod_id, 'start_date': startdate.val(), 'end_date' : enddate.val(), 'active' : active.val(), 'peakgroup_id': management.var.peak_group_id_selection};

         $('#period-popup-error').html('');
	 $('#period-popup-error').hide();

         $('#'+loader_id).show();
         $('.peakrow').prop('disabled', true);
         $("#"+start_id).prop('disabled', true);
         $('#'+end_id).prop('disabled', true);
         $('#'+active_id).prop('disabled', true);

         $.ajax({
             url: management.var.peak_period_save_url,
             method: "POST",
             headers: {'X-CSRFToken' : management.var.csrf_token },
             data: JSON.stringify({'payload': data,}),
             contentType: "application/json",
             success: function(data) {
                   $('#'+loader_id).hide();
                   $("#"+start_id).prop('disabled', false);
                   $('#'+end_id).prop('disabled', false);
                   $('#'+active_id).prop('disabled', false);
                   $('.peakrow').prop('disabled',false);
		   $('#period-popup-success').html("Successfully Updated");
		   $('#period-popup-success').show();
		   setTimeout("$('#period-popup-success').fadeOut('slow');",1000);
		   management.load_peak_periods(management.var.peak_group_id_selection);
             },
             error: function(errMsg) {
                   $('#'+loader_id).hide();
                   $("#"+start_id).prop('disabled', false);
                   $('#'+end_id).prop('disabled', false);
                   $('#'+active_id).prop('disabled', false);
                   $('.peakrow').prop('disabled',false);

                   $('#period-popup-error').html(errMsg.responseJSON.message);
                   $('#period-popup-error').show();
                   //management.load_peak_groups();
                   // alert(JSON.stringify(errMsg));
             }
         });
    },
    save_peak_group: function(buttondata_obj) {

	     var group_id = null;
             var group_name = {'val': function(){return ''}, 'prop': function(){return false} };
	     var peak_status = {'val': function(){return ''}, 'prop': function(){return false}};
	     var peakgroup_progress_loader = null;
            
             if (buttondata_obj['action'] == 'create') {
	         group_name = $('#group-name');
                 peak_status = $('#peak-status');
		 peakgroup_progress_loader = $('#peakgroup_progress_loader_create');
	     } else if (buttondata_obj['action'] == 'delete') { 
		 group_id = buttondata_obj['group_id'];
                 peakgroup_progress_loader = $('#peakgroup-loader-'+group_id);
	     } else {
		 group_id = buttondata_obj['group_id'];
		 group_name = $('#row-group-name-'+buttondata_obj['group_id']);
		 peak_status = $('#row-group-active-'+buttondata_obj['group_id']);
		 peakgroup_progress_loader = $('#peakgroup-loader-'+group_id);
	     }

             var data = {'action': buttondata_obj['action'], 'group_id': group_id, 'group_name' : group_name.val(),'peak_status': peak_status.val()};
	     
             $('#pg-rowcollapse-'+group_id).hide();
             peakgroup_progress_loader.show();
             group_name.prop('disabled', true);
	     peak_status.prop('disabled', true);
	     $('#group-flat-success').hide();
             $('#group-flat-error').hide();
	     $('#popup-error').hide();
             $.ajax({
                 url: management.var.peak_groups_save_url,
                 method: "POST",  
		 headers: {'X-CSRFToken':management.var.csrf_token},
                 data: JSON.stringify({'payload': data,}),
                 contentType: "application/json",
                 success: function(data) {
		       peakgroup_progress_loader.hide();
		       group_name.prop('disabled', false);
		       peak_status.prop('disabled', false);
		       management.load_peak_groups();

                       $('#group-close-modal').click();
		       $('#group-flat-success').html("Successfull");
		       $('#group-flat-success').show();

                       // alert(JSON.stringify(data));
                 },
                 error: function(errMsg) {
	             group_name.prop('disabled', false);
	             peak_status.prop('disabled', false);
		     peakgroup_progress_loader.hide();
                     if (buttondata_obj['action'] == 'save') { 
			  $('#group-flat-error').html(errMsg.responseJSON.message);
                          $('#group-flat-error').show();
			  $('#pg-rowcollapse-'+management.var.peak_group_collapsed_id).show();
	             } else if (buttondata_obj['action'] == 'delete') {
			  $('#group-flat-error').html(errMsg.responseJSON.message);
			  $('#group-flat-error').show();
                     } else {
		          $('#popup-error').html(errMsg.responseJSON.message);
		          $('#popup-error').show();
		     }
		     // management.load_peak_groups();
                     // alert(JSON.stringify(errMsg));
                 }
             });

	     //$('#close-modal').click();
    },	    
    save_booking_refund_cancel: function(buttondata_obj) {

	    var bulk_id = null;
        var bulk_name = {'val': function(){return ''}, 'prop': function(){return false} };
	    var bulk_refund_cancel_list = {'val': function(){return ''}, 'prop': function(){return false}};
        var refund_type = {'val': function(){return ''}, 'prop': function(){return false}};
        var cancel_booking = {'val': function(){return ''}, 'prop': function(){return false}};
        var email_for_booking = {'val': function(){return ''}, 'prop': function(){return false}};
	    var bulk_progress_loader = null;
            
        if (buttondata_obj['action'] == 'create') {
	        bulk_name = $('#bulk-name');
            bulk_refund_cancel_list = $('#bulk-refund-cancel-list');		    
            refund_type = $('#refund-type');
            cancel_booking = $('#cancel-booking');
            email_for_booking = $('#email-for-booking');

            bulk_progress_loader = $('#peakgroup_progress_loader_create');
        
        var data = {'action': buttondata_obj['action'], 'bulk_id': bulk_id, 'bulk_name' : bulk_name.val(), 'refund_type' : refund_type.val(), 'cancel_booking': cancel_booking.val(), 'email_for_booking': email_for_booking.val(),'bulk_refund_cancel_list': bulk_refund_cancel_list.val()};
	    
        $('#pg-rowcollapse-'+bulk_id).hide();
        bulk_progress_loader.show();
        bulk_name.prop('disabled', true);
        bulk_refund_cancel_list.prop('disabled', true);

        refund_type.prop('disabled', true);
        cancel_booking.prop('disabled', true);
        email_for_booking.prop('disabled', true);

        $('#refund-cancel-flat-success').hide();
        $('#refund-cancel-flat-error').hide();
        $('#popup-error').hide();

        $.ajax({
            url: management.var.bulk_refund_save_url,
            method: "POST",  
            headers: {'X-CSRFToken':management.var.csrf_token},
            data: JSON.stringify({'payload': data,}),
            contentType: "application/json",
            success: function(data) {
    	        bulk_progress_loader.hide();
	    	    bulk_name.prop('disabled', false);
		        bulk_refund_cancel_list.prop('disabled', false);
                refund_type.prop('disabled', false);
                cancel_booking.prop('disabled', false);
                email_for_booking.prop('disabled', false);

		        management.load_peak_groups();

                $('#group-close-modal').click();
		        $('#refund-cancel-flat-success').html("Successfull");
		        $('#refund-cancel-flat-success').show();
                       // alert(JSON.stringify(data));
                },
                error: function(errMsg) {
	    	    bulk_name.prop('disabled', false);
		        bulk_refund_cancel_list.prop('disabled', false);
                refund_type.prop('disabled', false);
                cancel_booking.prop('disabled', false);
                email_for_booking.prop('disabled', false);
		        bulk_progress_loader.hide();

                if (buttondata_obj['action'] == 'save') { 
			        $('#refund-cancel-flat-error').html(errMsg.responseJSON.message);
                    $('#refund-cancel-flat-error').show();
			        $('#pg-rowcollapse-'+management.var.peak_group_collapsed_id).show();
	            } else if (buttondata_obj['action'] == 'delete') {
			        $('#refund-cancel-flat-error').html(errMsg.responseJSON.message);
			        $('#refund-cancel-flat-error').show();
                } else {
		            $('#popup-error').html(errMsg.responseJSON.message);
		            $('#popup-error').show();
		        }
            }

             });
        }

    },	
    init: function() {
    }
}
management.init();

