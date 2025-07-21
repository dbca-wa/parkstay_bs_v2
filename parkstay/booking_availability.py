from parkstay import models
from parkstay import utils
from datetime import datetime, timedelta, date
from decimal import Decimal
from django.db.models import Q
from django.conf import settings
from django.core.cache import cache
from parkstay.helpers import is_officer
from django.db.models import Max
from ledger_api_client import utils as ledger_api_utils
from parkstay import utils_cache
import json


def get_campground(campground_id):
     cg_hash = {} 
     cached_data = cache.get('api.get_campground('+str(campground_id)+')')   
     
     if cached_data is None:
         ground = models.Campground.objects.get(id=campground_id)
         if ground:              
                cg_hash['id'] = ground.id
                cg_hash['name'] = ground.name
                cg_hash['campground_type'] = ground.campground_type
                cg_hash['site_type'] = ground.site_type
                cg_hash['long_description']  = ground.long_description
                cg_hash['campground_map_url'] = ''
                cg_hash['campground_map'] = ''
                cg_hash['release_time'] = ground.release_time.strftime("%H:%M:%S")
                cg_hash['release_time_friendly'] = ground.release_time.strftime("%I:%M %p")
                cg_hash['max_advance_booking'] = ground.max_advance_booking

                release_period = utils.get_release_date_for_campground(campground_id)
                cg_hash['release_date'] = None
                cg_hash['booking_open_date'] = None
                if release_period['release_date']:
                    cg_hash['release_date'] = release_period['release_date'].strftime('%Y-%m-%d')
                if release_period['booking_open_date']:
                    cg_hash['booking_open_date'] = release_period["booking_open_date"].strftime('%Y-%m-%d')

                if ground.campground_map:
                   cg_hash['campground_map_url'] = ground.campground_map.url
                   cg_hash['campground_map'] = {'path': ground.campground_map.path}
                # Increasing cache will cause delays in release availablity on then campsite screen
                cache.set('api.get_campground('+str(campground_id)+')', json.dumps(cg_hash),  30)
                
     else:         
         cg_hash = json.loads(cached_data)         
     return cg_hash


def get_features():
    cached_data = cache.get('booking_availability.get_features()')
    features_array = {}
    if cached_data is None:
        features = models.Feature.objects.all()
        for f in features:
             features_array[f.id] = {'id': f.id, 'name': f.name, 'description': f.description, 'type': f.type }
        cache.set('booking_availability.get_features()', json.dumps(features_array),  86400)
    else:
        features_array = json.loads(cached_data)

    return features_array
    

def get_campsites_for_campground(ground, gear_type):
    sites_qs = None
    sites_array = []
    cached_data = cache.get('booking_availability.get_campsites_for_campground:'+str(ground['id']))
    features_array = get_features() 
    cached_data = None
    if cached_data is None:
        sites_qs = models.Campsite.objects.filter(campground_id=ground['id']).values('id','campground_id','name','campsite_class_id','wkb_geometry','tent','campervan','caravan','min_people','max_people','max_vehicles','description','campground__max_advance_booking','campsite_class__name','short_description','vehicle','motorcycle','trailer').order_by('name')
        for cs in sites_qs:
            sites_qs_features = models.Campsite.objects.filter(id=cs['id']).values('features')
            row = {}
            row['id'] = cs['id']
            row['campground_id'] = cs['campground_id']
            row['name'] = cs['name']
            row['campsite_class_id'] = cs['campsite_class_id']
            row['campsite_class__name'] = cs['campsite_class__name']
            wkb_geometry_array = None
            if cs['wkb_geometry']: 
                  wkb_geometry_array = [cs['wkb_geometry'][0],cs['wkb_geometry'][1]]
            row['wkb_geometry'] = wkb_geometry_array
            
            row['tent'] = cs['tent']
            row['vehicle'] = cs['vehicle']
            row['motorcycle'] = cs['motorcycle']
            row['campervan'] = cs['campervan']
            row['caravan'] = cs['caravan']
            row['trailer'] = cs['trailer']
            row['min_people'] = cs['min_people']
            row['max_people'] = cs['max_people']
            row['max_vehicles'] = cs['max_vehicles']
            row['description'] = cs['description']
            row['short_description'] = cs['short_description']
            row['campground__max_advance_booking'] = cs['campground__max_advance_booking']
            row['features'] = []
            for cs_feature in sites_qs_features:
                feature_id_str = str(cs_feature['features'])
                if feature_id_str in features_array:
                     row['features'].append(features_array[feature_id_str])
            sites_array.append(row) 
        cache.set('booking_availability.get_campsites_for_campground:'+str(ground['id']), json.dumps(sites_array),  86400)
    else:
        sites_array = json.loads(cached_data)
    cs_rows = []
    for cs in sites_array:
         row = {}
         row['id'] = cs['id']
         row['campground_id'] = cs['campground_id'] 
         row['name'] = cs['name']
         row['campsite_class_id'] = cs['campsite_class_id']
         row['campsite_class__name'] = cs['campsite_class__name']
         row['wkb_geometry'] = cs['wkb_geometry']
         row['features'] = cs['features']
         row['tent'] = cs['tent']
         row['vehicle'] = cs['vehicle']
         row['motorcycle'] = cs['motorcycle']
         row['campervan'] = cs['campervan']
         row['caravan'] = cs['caravan']
         row['trailer'] = cs['trailer']
         row['min_people'] = cs['min_people']
         row['max_people'] = cs['max_people']
         row['max_vehicles'] = cs['max_vehicles']
         row['description'] = cs['description']
         row['campground__max_advance_booking'] = cs['campground__max_advance_booking']
         row['short_description'] = cs['short_description']
         if row['short_description'] is None:
             row['short_description'] = ''
         if gear_type == 'all':
             cs_rows.append(row)
         if gear_type == 'tent' and cs['tent'] is True:
             cs_rows.append(row)
         if gear_type == 'campervan' and cs['campervan'] is True:
             cs_rows.append(row)
         if gear_type == 'caravan' and cs['caravan'] is True:
             cs_rows.append(row)

    return cs_rows

def not_bookable_online(ongoing_booking,ground,start_date,end_date,num_adult,num_concession,num_child,num_infant,gear_type):
        length = max(0, (end_date - start_date).days)
        context = {}
        if gear_type != 'all':
            context[gear_type] = True
        sites_qs = models.Campsite.objects.filter(campground=ground).filter(**context)

        rates = {
            siteid: {
                date: num_adult * info['adult'] + num_concession * info['concession'] + num_child * info[
                    'child'] + num_infant * info['infant']
                for date, info in dates.items()
            } for siteid, dates in utils.get_visit_rates(sites_qs, start_date, end_date).items()
        }

        availability = utils.get_campsite_availability(sites_qs, start_date, end_date)

        # Added campground_type to enable offline booking more info in frontend
        result = {
            'id': ground.id,
            'name': ground.name,
            'long_description': ground.long_description,
            'campground_type': ground.campground_type,
            'map': ground.campground_map.url if ground.campground_map else None,
            'ongoing_booking': True if ongoing_booking else False,
            'ongoing_booking_id': ongoing_booking.id if ongoing_booking else None,
            'arrival': start_date.strftime('%Y/%m/%d'),
            'days': length,
            'adults': 1,
            'children': 0,
            'maxAdults': 30,
            'maxChildren': 30,
             'sites': [],
             'classes': {},
        }
        return result

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        #print (obj.isoformat())
        return str(obj.isoformat())
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError ("Type %s not serializable" % type(obj))


def get_campground_rates(campground_id):

    rates_array = []
    cached_data = cache.get('booking_availability.get_campground_rates_'+str(campground_id))
    #cached_data = None
    if cached_data is None:
        rates_qs = models.CampsiteRate.objects.filter(campsite__campground_id=campground_id).values('id','campsite','rate','allow_public_holidays','date_start','date_end','rate_type','price_model','reason','details','update_level','campsite_id','rate__adult','rate__concession','rate__child','rate__infant')

        for r in rates_qs:
              row = {}
              row['id'] = int(r['id'])
              row['campsite'] = r['campsite']
              row['campsite_id'] = r['campsite']
              row['rate'] = r['rate']
              row['allow_public_holidays'] = r['allow_public_holidays']
              row['date_start'] = r['date_start'].strftime('%Y-%m-%d')
              if r['date_end']:
                  row['date_end'] = r['date_end'].strftime('%Y-%m-%d')
              else:
                  row['date_end'] = None
              row['rate_type'] = r['rate_type']
              row['price_model'] = r['price_model']
              row['reason'] = r['reason']
              row['details'] = r['details']
              row['update_level'] = r['update_level']
              row['campsite_id'] = r['campsite_id']
              row['rate__adult'] = str(r['rate__adult'])
              row['rate__concession'] = str(r['rate__concession'])
              row['rate__child'] = str(r['rate__child'])
              row['rate__infant'] = str(r['rate__infant'])
              rates_array.append(row)

        cache.set('booking_availability.get_campground_rates_'+str(campground_id), json.dumps(rates_array, default=json_serial),  86400)
    else:
        rates_array = json.loads(cached_data)

    return rates_array 

def get_visit_rates(campground_id, campsites_array, start_date, end_date):
    """Fetch the per-day pricing for each visitor type over a range of visit dates."""
    # fetch the applicable rates for the campsites
    #rates_qs = CampsiteRate.objects.filter(
    #    Q(campsite_id__in=campsites_qs),
    #    Q(date_start__lt=end_date) & (Q(date_end__gte=start_date) | Q(date_end__isnull=True))
    #).prefetch_related('rate')
    rates_qs = get_campground_rates(campground_id)
    #print (rates_qs)
    # prefill all slots
    duration = (end_date - start_date).days
    results = {}
    for site in campsites_array:
        results[site['pk']] = {}
        for i in range(duration):
             results[site['pk']][start_date + timedelta(days=i)] = {'adult': Decimal('0.00'), 'child': Decimal('0.00'),'concession': Decimal('0.00'), 'infant': Decimal('0.00')} 
            

    # make a record of the earliest CampsiteRate for each site
    early_rates = {}
    for rate in rates_qs:
        rate_date_start = datetime.strptime(rate['date_start'], "%Y-%m-%d").date()
        if rate['campsite_id'] not in early_rates:
            early_rates[rate['campsite_id']] = rate
        elif datetime.strptime(early_rates[rate['campsite_id']]['date_start'], "%Y-%m-%d").date()  > rate_date_start:
            early_rates[rate['campsite_id']] = rate
       
        rate_date_start = datetime.strptime(rate['date_start'], "%Y-%m-%d").date()
        if rate['date_end'] is None:
            rate_date_end = None
        else:
            rate_date_end = datetime.strptime(rate['date_end'], "%Y-%m-%d").date()

        # for the period of the visit overlapped by the rate, set the amounts
        start = max(start_date, rate_date_start)

        # End and start date are the same leading to the lod rate enot going thru the loop
        # Add 1 day if date_end exists(to cover all days before the new rate),previously it was skipping 2 days before the new rate date
        if(rate_date_end):
            rate_date_end += timedelta(days=1)

        end = min(end_date, rate_date_end) if rate_date_end else end_date
        for i in range((end-start).days):
            if rate['campsite_id'] in results:
               results[rate['campsite_id']][start+timedelta(days=i)]['adult'] = Decimal(rate['rate__adult'])
               results[rate['campsite_id']][start+timedelta(days=i)]['concession'] = Decimal(rate['rate__concession'])
               results[rate['campsite_id']][start+timedelta(days=i)]['child'] = Decimal(rate['rate__child'])
               results[rate['campsite_id']][start+timedelta(days=i)]['infant'] = Decimal(rate['rate__infant'])

    # complain if there's a Campsite without a CampsiteRate
    if len(early_rates) < len(rates_qs):
    #if len(early_rates) < rates_qs.count():
        print('Missing CampsiteRate coverage!')
    # for ease of testing against the old datasets, if the visit dates are before the first
    # CampsiteRate date, use that CampsiteRate as the pricing model.
    for site_pk, rate in early_rates.items():
        if start_date < rate_date_start:
            start = start_date
            end = datetime.strptime(rate['date_start'], "%Y-%m-%d").date()
            for i in range((end - start).days):
                results[site_pk][start + timedelta(days=i)]['adult'] = rate['rate__adult']
                results[site_pk][start + timedelta(days=i)]['concession'] = rate['rate__concession']
                results[site_pk][start + timedelta(days=i)]['child'] = rate['rate.child']
                results[site_pk][start + timedelta(days=i)]['infant'] = rate['rate__infant']
    return results

def get_campground_booking_range_is_open(campground_id, start_date):
    print ("get_campground_booking_range_is_open:"+str(campground_id))
    cgbr_cl = get_campground_booking_range(campground_id, 0)
    for c in cgbr_cl:
        end_date = start_date + timedelta(days=1)

        range_start = datetime.strptime(c['range_start'], "%Y-%m-%d").date()
        if c['range_end'] is None:
            range_end = datetime.now().date() +  timedelta(days=1) 
        else:
            range_end = datetime.strptime(c['range_end'], "%Y-%m-%d").date()

        if range_start < end_date and range_end > start_date:
            print ("Campground Closed")
            return False 

    return True


def get_campground_booking_range(campground_id, status):

    table_array = []
    cached_data = cache.get('booking_availability.get_campground_booking_range'+str(campground_id))
    #cached_data = None
    if cached_data is None:
        cgbr_qs = models.CampgroundBookingRange.objects.filter(
             Q(campground__id=campground_id),
             #Q(status=1),
            #Q(range_start__lt=end_date) & (Q(range_end__gte=start_date) | Q(range_end__isnull=True)),
        ).values('id','campground','min_sites','max_sites','created','updated_on','status','closure_reason','details','range_start','range_end','closure_reason__text')

        for r in cgbr_qs:
              row = {}
              row['id'] = int(r['id'])
              row['campground'] = r['campground']
              row['min_sites'] = r['min_sites']
              row['max_sites'] = r['max_sites']
              row['created'] = r['created'].strftime('%Y-%m-%d %H:%M:%S.%f')

              if r['range_start']:
                  row['range_start'] = r['range_start'].strftime('%Y-%m-%d')
              else:
                  row['range_start'] = None
              if r['range_end']:
                  row['range_end'] = r['range_end'].strftime('%Y-%m-%d')
              else:
                  row['range_end'] = None

              if r['updated_on']:
                  row['updated_on'] = r['updated_on'].strftime('%Y-%m-%d %H:%M:%S.%f')
              else:
                  row['updated_on'] = None

              row['status'] = r['status']
              row['closure_reason'] = r['closure_reason']
              row['details'] = r['details']
              row['closure_reason__text'] = r['closure_reason__text']

              table_array.append(row)

        cache.set('booking_availability.get_campground_booking_range'+str(campground_id), json.dumps(table_array, default=json_serial),  86400)
        print ("NOT CACEHED")
    else:
        print ("CACHED RATES")
        table_array = json.loads(cached_data)
    filtered_table_array = []
    for t in table_array:
        append_row = False
        if status == int(t['status']):
             append_row = True
        if append_row is True:
            filtered_table_array.append(t)
    return filtered_table_array


def get_campsite_availability(ground_id, sites_array, start_date, end_date, user=None, change_booking_id=None):
    is_officer_boolean = False
    can_make_advanced_booking = False
    change_booking_id_obj = None
    nowtime = datetime.now()
    parkstay_officers = False    
    gca = get_campground(ground_id)  
    release_date_obj = utils_cache.get_campground_release_date()

    release_date = None
    booking_open_date = None
    today = date.today()

    campground_release_date = utils.get_release_date_for_campground(ground_id)
    release_date = campground_release_date["release_date"]
    booking_open_date = campground_release_date["booking_open_date"]  
    # Check if campground has specific open periods
    # for rd in release_date_obj['release_period']:
    #     if rd['campground'] == ground_id:
    #         rd_release_date = datetime.strptime(rd['release_date'], "%Y-%m-%d").date()
    #         rd_booking_open_date= datetime.strptime(rd['booking_open_date'], "%Y-%m-%d").date()
    #         if today >= rd_booking_open_date:
    #             release_date = rd_release_date
    #             booking_open_date = rd_booking_open_date

    # if release_date is None:
    #     for rd in release_date_obj['release_period']:
    #         if rd['campground'] == None or rd['campground'] == ground_id:
    #             rd_release_date = datetime.strptime(rd['release_date'], "%Y-%m-%d").date()
    #             rd_booking_open_date = datetime.strptime(rd['booking_open_date'], "%Y-%m-%d").date()
    #             if today >= rd_booking_open_date:
    #                 release_date = rd_release_date
    #                 booking_open_date = rd_booking_open_date                
    
    # if release_date is None:
    #     release_date = datetime.strptime(release_date_obj['release_date'], "%Y-%m-%d").date()    
    # print ("RELEASE")
    # print (release_date)

    if user:
        if models.ParkstayPermission.objects.filter(email=user.email,permission_group=5).count() > 0:
             can_make_advanced_booking = True
        parkstay_officers = ledger_api_utils.user_in_system_group(user.id,'Parkstay Officers')
 
    if user:
       is_officer_boolean = is_officer(user) 
    """Fetch the availability of each campsite in a queryset over a range of visit dates."""
    sa_qy = []
    for s in sites_array:
          sa_qy.append(s['pk'])
    if change_booking_id is not None:
        change_booking_id = int(change_booking_id)
        change_booking_id_query = models.Booking.objects.filter(id=change_booking_id)
        if change_booking_id_query.count() > 0:
            change_booking_id_obj = change_booking_id_query[0]        
    # get current booking from change booking id

    # fetch all of the single-day CampsiteBooking objects within the date range for the sites
    bookings_qs = None
    if change_booking_id is None:
        bookings_qs = models.CampsiteBooking.objects.filter(
            campsite_id__in=sa_qy,
            date__gte=start_date,
            date__lt=end_date,
            booking__is_canceled=False,
        ).exclude(booking_type=3,booking__expiry_time__lt=nowtime).order_by('date', 'campsite__name')

    else:
        bookings_qs = models.CampsiteBooking.objects.filter(
            campsite_id__in=sa_qy,
            date__gte=start_date,
            date__lt=end_date,
            booking__is_canceled=False,
            ).exclude(booking_id=change_booking_id).exclude(booking_type=3,booking__expiry_time__lt=nowtime).order_by('date', 'campsite__name')
      
    legacy_bookings = models.CampsiteBookingLegacy.objects.filter(campsite_id__in=sa_qy,
                                                            date__gte=start_date,
                                                            date__lt=end_date,
                                                            is_cancelled=False  
                                                            )
    # prefill all slots as 'open'
    duration = (end_date - start_date).days
    #duration = (end_date + timedelta(days=1) - start_date).days
    results = {site['pk']: {start_date + timedelta(days=i): ['open', None] for i in range(duration)} for site in sites_array}
 
    # generate a campground-to-campsite-list map
    campground_map = {ground_id: []}
    for cs in sites_array:
          if cs['pk'] not in campground_map[ground_id]:
              campground_map[ground_id].append(cs['pk'])
    #campground_map = {cg[0]: [cs.pk for cs in sites_array if cs.campground.pk == cg[0]] for cg in campsites_qs.distinct('campground').values_list('campground')}
    #{167: [1926, 1934, 1938, 1942, 1946, 1948, 1950, 1935, 1939, 1943, 1927, 1928, 1936, 1940, 1944, 1929, 1931, 1930, 1932, 1933, 1937, 1941, 1945, 1947, 1949, 1951, 1952, 1953, 1954, 1955, 1925]}
    # strike out whole campground closures
    cgbr_qs = get_campground_booking_range(ground_id, 1)
    #cgbr_qs = models.CampgroundBookingRange.objects.filter(
    #    Q(campground__id=ground_id),
    #    Q(status=1),
    #    Q(range_start__lt=end_date) & (Q(range_end__gte=start_date) | Q(range_end__isnull=True)),
    #)
    for closure in cgbr_qs:
        closure_range_start = datetime.strptime(closure['range_start'], "%Y-%m-%d").date()
        if closure['range_end']:
            closure_range_end  = datetime.strptime(closure['range_end'], "%Y-%m-%d").date()
        else:
            closure_range_end  = end_date
        start = max(start_date, closure_range_start)
        end = min(end_date, closure_range_end) if closure_range_end else end_date
        today = date.today()
        reason = closure['closure_reason__text']
        diff = (end - start).days
        for i in range(diff):
            for cs in campground_map[closure['campground']]:
                theday = start + timedelta(days=i)
                if start + timedelta(days=i) == today:
                    is_open = get_campground_booking_range_is_open(closure['campground'], start + timedelta(days=i))
                    if not is_open:
                    #if not closure.campground._is_open(start + timedelta(days=i)):
                        if start + timedelta(days=i) in results[cs]:
                            results[cs][start + timedelta(days=i)][0] = 'closed'
                            results[cs][start + timedelta(days=i)][1] = str(reason)
                else:
                    if start + timedelta(days=i) in results[cs]:
                        results[cs][start + timedelta(days=i)][0] = 'closed'
                        results[cs][start + timedelta(days=i)][1] = str(reason)

    sa_qy = []
    for s in sites_array:
        sa_qy.append(s['pk'])

    # strike out campsite closures
    csbr_qs = models.CampsiteBookingRange.objects.filter(
        Q(campsite_id__in=sa_qy),
        Q(status=1),
        Q(range_start__lt=end_date) & (Q(range_end__gte=start_date) | Q(range_end__isnull=True))
    )
    for closure in csbr_qs:
        start = max(start_date, closure.range_start)
        end = min(end_date, closure.range_end) if closure.range_end else end_date
        today = date.today()
        reason = closure.closure_reason.text
        diff = (end - start).days
        for i in range(diff):
            if start + timedelta(days=i) == today:
                pass
                if not closure.campsite._is_open(start + timedelta(days=i)):
                    if start + timedelta(days=i) in results[closure.campsite.pk]:
                        results[closure.campsite.pk][start + timedelta(days=i)][0] = 'closed'
                        results[closure.campsite.pk][start + timedelta(days=i)][1] = str(reason)
            else:
                if start + timedelta(days=i) in results[closure.campsite.pk]:
                    results[closure.campsite.pk][start + timedelta(days=i)][0] = 'closed'
                    results[closure.campsite.pk][start + timedelta(days=i)][1] = str(reason)

    # strike out black bookings
    # for b in bookings_qs.filter(booking_type=2):
    
    #legacy bookings
    for lb in legacy_bookings:
        if lb.booking_type == 2:
             results[lb.campsite_id][lb.date][0] = 'closed'

    for b in bookings_qs:    
        if b.booking_type == 2:
            results[b.campsite.pk][b.date][0] = 'closed'

    # add booking status for real bookings
    # for b in bookings_qs.exclude(booking_type=2):
    #for b in bookings_qs.exclude(booking_type=2):

    #legacy bookings
    for lb in legacy_bookings.exclude(booking_type=2):
        if lb.booking_type != 2:
           if results[lb.campsite_id][lb.date][0] == 'closed':
               results[lb.campsite_id][lb.date][0] = 'closed & booked'
           else:
               results[lb.campsite_id][lb.date][0] = 'booked'

    for b in bookings_qs.exclude(booking_type=2):
        if b.booking_type != 2:
            if results[b.campsite.pk][b.date][0] == 'closed':
                results[b.campsite.pk][b.date][0] = 'closed & booked'
            else:
                results[b.campsite.pk][b.date][0] = 'booked'

    # strike out days before today
    today = date.today()
    if start_date < today:
        for i in range((min(today, end_date) - start_date).days):
            for key, val in results.items():
            #    pass
                 if change_booking_id is not None:
                     if change_booking_id > 0 and  start_date <= today:
                        if parkstay_officers is  True:                        
                            print ("Parkstay Officer Past Date Override")
                        else:
                            if start_date != change_booking_id_obj.arrival:                                                        
                                val[start_date + timedelta(days=i)][0] = 'pastdate'
                                                    
                     else:
                          pass
                          val[start_date + timedelta(days=i)][0] = 'tooearly'
                 else:   
                     pass
                     val[start_date + timedelta(days=i)][0] = 'tooearly'
                 #val[start_date + timedelta(days=i)][0] = 'tooearly'

    # strike out days after the max_advance_booking
    if user == None or (not can_make_advanced_booking):
        
        for site in sites_array:     
             
            stop = today + timedelta(days=site['data']['campground__max_advance_booking'])            
            stop_mark = min(max(stop, start_date), end_date)
            if release_date is None:   
                if start_date > stop:
                    for i in range((end_date - stop_mark).days):
                        results[site['pk']][stop_mark + timedelta(days=i)][0] = 'toofar'

                # add to restrict the 180 days (max advance open times to a specific open time)   
                if start_date == stop:
                    nowtime = datetime.now()
                    nowdatetime_string = nowtime.strftime("%Y-%m-%d")
                    campground_opentime = datetime.strptime(nowdatetime_string+' '+gca["release_time"], '%Y-%m-%d %H:%M:%S')                
                    
                    if nowtime >= campground_opentime:
                        pass
                    else:
                        for i in range((end_date - stop_mark).days):
                            results[site['pk']][stop_mark + timedelta(days=i)][0] = 'toofar'                         
    
            if release_date is not None: 
                stop_mark_rd = min(max(release_date, start_date), end_date  ) 
        
                if end_date > release_date:
                    for i in range((end_date - stop_mark_rd).days):                 
                        results[site['pk']][stop_mark_rd + timedelta(days=i)][0] = 'closed'  
                    # utils.get_release_date_for_campground is linked to the time release date and will provide 
                    # new release dates when campground open time equals current time

                # if end_date == release_date:
                    # print (range((end_date - stop_mark_rd).days))
                    # for i in range((end_date - stop_mark_rd).days):                        
                    #     nowtime = datetime.now()
                    #     nowdatetime_string = nowtime.strftime("%Y-%m-%d")
                    #     campground_opentime = datetime.strptime(nowdatetime_string+' '+gca["release_time"], '%Y-%m-%d %H:%M:%S')
                    #     print ('OPEN')
                    #     print (campground_opentime)
                    #     if nowtime >= campground_opentime:
                    #         pass
                    #     else:
                    #         for i in range((end_date - stop_mark_rd).days):
                    #             results[site['pk']][stop_mark_rd + timedelta(days=i)][0] = 'closed'  

                    # nowtime = datetime.now()
                    # nowdatetime_string = nowtime.strftime("%Y-%m-%d")
                    # campground_opentime = datetime.strptime(nowdatetime_string+' '+gca["release_time"], '%Y-%m-%d %H:%M:%S')
                                        
                    # if nowtime >= campground_opentime:                        
                    #     pass
                    # else:   
                    #     # Departure date will not have any dates in availability data so need to use previous day.        
                    #     results[site['pk']][release_date - timedelta(days=1)][0] = 'closed'                                                                                    
                           

    # Added this section to allow officers to book camp dated after the max_advance_booking
    elif user != None and can_make_advanced_booking:        
        pass

    # Get the current stay history
    stay_history = models.CampgroundStayHistory.objects.filter(
        Q(range_start__lte=start_date, range_end__gte=start_date) |  # filter start date is within period
        Q(range_start__lte=end_date, range_end__gte=end_date) |  # filter end date is within period
        Q(Q(range_start__gt=start_date, range_end__lt=end_date) & Q(range_end__gt=today)),  # filter start date is before and end date after period
        campground_id=ground_id)
    if stay_history:
        max_days = min([x.max_days for x in stay_history])
    else:
        max_days = settings.PS_MAX_BOOKING_LENGTH
    # strike out days after the max_stay period
    if user == None or (not can_make_advanced_booking):
        for site in sites_array:
            stop = start_date + timedelta(days=max_days)
            stop_mark = min(max(stop, start_date), end_date)
            for i in range((end_date - stop_mark).days):
                results[site['pk']][stop_mark + timedelta(days=i)][0] = 'toofar'
    # Added this section to allow officers to book camp dated after the max_advance_booking
    elif user != None and can_make_advanced_booking:
        pass

    return results


def campground_booking_information(context, campground_id):

        campground_query = models.Campground.objects.get(id=campground_id)
        max_people = models.Campsite.objects.filter(campground_id=campground_id).aggregate(Max('max_people'))["max_people__max"]
        max_vehicles = models.Campsite.objects.filter(campground_id=campground_id).aggregate(Max('max_vehicles'))["max_vehicles__max"]

        context['cg']['campground']['id'] = campground_query.id
        context['cg']['campground']['name'] = campground_query.name
        context['cg']['campground']['largest_camper'] = max_people
        context['cg']['campground']['largest_vehicle'] = max_vehicles
        context['cg']['campground']['park'] = {}
        context['cg']['campground']['park']['id'] = campground_query.park.id
        context['cg']['campground']['park']['alert_count'] = campground_query.park.alert_count
        context['cg']['campground']['park']['alert_url'] = settings.ALERT_URL

        context['cg']['campground_notices_red'] = 0
        context['cg']['campground_notices_orange'] = 0
        context['cg']['campground_notices_blue'] = 0

        campground_notices_query = models.CampgroundNotice.objects.filter(campground_id=campground_id)

        campground_notices_array = []
        for cnq in campground_notices_query:
               if cnq.notice_type == 0:
                   context['cg']['campground_notices_red'] = context['cg']['campground_notices_red'] + 1
               if cnq.notice_type == 1:
                   context['cg']['campground_notices_orange'] = context['cg']['campground_notices_orange'] + 1
               if cnq.notice_type == 2:
                   context['cg']['campground_notices_blue'] = context['cg']['campground_notices_blue'] + 1

               campground_notices_array.append({'id': cnq.id, 'notice_type' : cnq.notice_type,'message': cnq.message})

        features_obj = []
        context['cg']['campground_notices'] = campground_notices_array

        return context




