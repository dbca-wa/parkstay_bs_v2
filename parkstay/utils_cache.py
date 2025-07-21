from django.core.cache import cache
from parkstay import models as parkstay_models
from django.conf import settings
from django.db.models import Max
import json

def all_campgrounds():
    cg_array = []

    dumped_data = cache.get('utils_cache.all_campgrounds')
    #dumped_data = None
    if dumped_data is None:
        grounds = parkstay_models.Campground.objects.all()
        for cg in grounds:
            cg_array.append({'id': cg.id, 'campground_name': cg.name,'campground_type': cg.campground_type})
        cache.set('utils_cache.all_campgrounds', json.dumps(cg_array),  86400)
    else:
        cg_array = json.loads(dumped_data)

    return cg_array


def all_campground_campsites(cg_id):
    cs_array = []
    dumped_data = cache.get('utils_cache.all_campground_campsites('+str(cg_id)+')')
    if dumped_data is None:
        campsites = parkstay_models.Campsite.objects.filter(campground_id=cg_id)
        for cs in campsites:
              cs_array.append({'id': cs.id, 'campground_name': cs.name})
        cache.set('utils_cache.all_campground_campsites('+str(cg_id)+')', json.dumps(cs_array),  86400)
    else:
        cs_array = json.loads(dumped_data)
    return cs_array


def get_campground(campground_id):
    from parkstay import utils
    cg_array = {}
    campground_dumped_data = cache.get('utils_cache.get_campground('+str(campground_id)+')')
    #campground_dumped_data = None
    if campground_dumped_data is None:
        campground_query = parkstay_models.Campground.objects.get(id=campground_id)
        campground = {}
        campground['id'] = campground_query.id
        campground['name'] = campground_query.name
        campground['campground_type'] = campground_query.campground_type
        campground['description'] = campground_query.description
        campground['about'] = campground_query.about
        campground['booking_information'] = campground_query.booking_information
        campground['campsite_information'] = campground_query.campsite_information
        campground['facilities_information'] = campground_query.facilities_information
        campground['campground_rules'] = campground_query.campground_rules
        campground['fee_information'] = campground_query.fee_information
        campground['health_and_safety_information'] = campground_query.health_and_safety_information
        campground['location_information'] = campground_query.location_information
        campground['campground_map'] = ''
        if campground_query.campground_map:
            campground['campground_map'] = campground_query.campground_map.url
        campground['max_advance_booking'] = campground_query.max_advance_booking
        campground['release_time'] = campground_query.release_time.strftime("%H:%M:%S")
        campground['campground_image'] = ""
        if campground_query.campground_image:
            campground['campground_image'] = campground_query.campground_image.image_size(1200,800)


        campground['camping_images'] = []
        campimages = parkstay_models.CampgroundImage.objects.filter(campground_id=campground_query.id)
        for ci in campimages:
            campground['camping_images'].append({ 'image_url': ci.image.url })


        campground['park_id'] = None
        if campground_query.park:
             campground['park_id'] = campground_query.park.id


        campground['campground_notices_red'] = 0
        campground['campground_notices_orange'] = 0
        campground['campground_notices_blue'] = 0

        campground_notices_query = parkstay_models.CampgroundNotice.objects.filter(campground_id=campground_query.id).order_by("order")

        campground_notices_array = []
        for cnq in campground_notices_query:
               if cnq.notice_type == 0:
                   campground['campground_notices_red'] = campground['campground_notices_red'] + 1
               if cnq.notice_type == 1:
                   campground['campground_notices_orange'] = campground['campground_notices_orange'] + 1
               if cnq.notice_type == 2:
                   campground['campground_notices_blue'] = campground['campground_notices_blue'] + 1
               campground_notices_array.append({'id': cnq.id, 'notice_type' : cnq.notice_type,'message': cnq.message})

        campground['campground_notices'] = campground_notices_array
        max_people = parkstay_models.Campsite.objects.filter(campground_id=campground_id).aggregate(Max('max_people'))["max_people__max"]
        max_vehicles = parkstay_models.Campsite.objects.filter(campground_id=campground_id).aggregate(Max('max_vehicles'))["max_vehicles__max"]
        campground['largest_camper'] = max_people
        campground['largest_vehicle'] = max_vehicles

        release_period = utils.get_release_date_for_campground(campground_id)
        campground['release_date'] = None
        campground['booking_open_date'] = None
        if release_period['release_date']:
            campground['release_date'] = release_period['release_date'].strftime('%Y-%m-%d')
        if release_period['booking_open_date']:
            campground['booking_open_date'] = release_period["booking_open_date"].strftime('%Y-%m-%d')



        cache.set('utils_cache.get_campground('+str(campground_id)+')', json.dumps(campground),  3600)
    else:
       campground = json.loads(campground_dumped_data)


    park = get_park(campground['park_id'])
    cg_array['campground'] = campground
    cg_array['park'] = park

    return cg_array


def get_park(park_id):
   park = {}
   park_dumped_data = cache.get('utils_cache.get_park('+str(park_id)+')')
   if park_dumped_data is None:
       if park_id:
            park_query = parkstay_models.Park.objects.get(id=park_id)
            park['id'] = park_query.id
            park['name'] = park_query.name
            park['alert_count'] = park_query.alert_count
            park['alert_url'] = settings.ALERT_URL
   
       cache.set('utils_cache.get_park('+str(park_id)+')', json.dumps(park),  86400)
   else:
       park = json.loads(park_dumped_data)
   return park


def get_features():
    features_obj = []
    feat_dumped_data = cache.get('utils_cache.get_features()')

    if feat_dumped_data is None:
        features_query = parkstay_models.Feature.objects.filter(type=1)
        for f in features_query:
            features_obj.append({'id': f.id,'name': f.name, 'symb': 'RF8G', 'description': f.description, 'type': f.type, 'key': 'twowheel','remoteKey': [f.name]})

        cache.set('utils_cache.get_features()', json.dumps(features_obj),  86400)
    else:
        features_obj = json.loads(feat_dumped_data)

    return features_obj

def get_notices():
    notices_dumped_data = cache.get('utils_cache.get_notices()')

    if notices_dumped_data is None:
        notices_obj = {}

        notices_query = parkstay_models.Notice.objects.all().order_by("order")

        notices_array = []
        for nq in notices_query:
               notices_array.append({'id': nq.id, 'notice_type' : nq.notice_type, 'message': nq.message, 'active': nq.active})

        notices_obj['notices'] = notices_array
        cache.set('utils_cache.get_notices()', json.dumps(notices_obj), 86400)
    else:
       notices_obj = json.loads(notices_dumped_data)
    return notices_obj

def get_my_booking_notices():
    my_booking_notices_dumped_data = cache.get('utils_cache.get_my_booking_notices()')

    if my_booking_notices_dumped_data is None:
        my_booking_notices_obj = {}

        my_booking_notices_query = parkstay_models.MyBookingNotice.objects.all().order_by("order")
        
        notices_array = []
        for mbnq in my_booking_notices_query:
               notices_array.append({'id': mbnq.id, 'notice_type' : mbnq.notice_type, 'message': mbnq.message, 'active': mbnq.active})

        my_booking_notices_obj['booking_notices'] = notices_array
        cache.set('utils_cache.get_my_booking_notices()', json.dumps(my_booking_notices_obj), 86400)
    else:
        my_booking_notices_obj = json.loads(my_booking_notices_dumped_data)
    return my_booking_notices_obj


def get_campground_release_date():
    release_date_obj = {"release_period": [], "active": False}    
    release_date_obj_data = cache.get('CampgroundReleaseDate')

    if release_date_obj_data is None:
        release_date_query = parkstay_models.CampgroundReleaseDate.objects.filter(active=True).order_by('release_date')    
        for rd in release_date_query:
            
            row = {}
            row['release_date'] = rd.release_date.strftime('%Y-%m-%d')
            row['booking_open_date'] = rd.booking_open_date.strftime('%Y-%m-%d')
            row['campground'] = None
            if rd.campground:
                row['campground'] = rd.campground.id
            release_date_obj['release_period'].append(row)
        if release_date_query.count() > 0:
            release_date_obj["active"] = True

        # if release_date_query.count() > 0:
        #     release_date_obj['release_date'] = release_date_query[0].release_date.strftime('%Y-%m-%d')
        # else:
        #     release_date_obj['release_date'] = None
        cache.set('CampgroundReleaseDate', json.dumps(release_date_obj),  30)        
    else:        
        release_date_obj = json.loads(release_date_obj_data)       
    return release_date_obj


def remove_custom_content_page(slug):
    """
    Remove the custom content page from cache.
    :param slug: The slug of the page to remove.
    """
    cache_key = f'page_content_{slug}'
    cache.delete(cache_key)
def set_custom_content_page(page):
    """
    Set the custom content page in cache.
    :param page: The Page object to cache.
    """
    cache_key = f'page_content_{page.slug}'
    item = {
        'id': page.id,
        'title': page.title,
        'slug': page.slug,
        'content': page.content,
        'created': page.created.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_on': page.updated_on.strftime('%Y-%m-%d %H:%M:%S')
    }
    cache.set(cache_key, item, 86400 * 30)  # Cache for 30 days
    return item
