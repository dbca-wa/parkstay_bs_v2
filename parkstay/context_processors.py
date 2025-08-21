from django.conf import settings
from parkstay import models
from parkstay import utils
from ledger_api_client import utils as ledger_api_utils
from django.core.cache import cache
from django.utils import timezone
import json
import hashlib
import uuid

def parkstay_url(request):
    session_id = request.COOKIES.get('sessionid', None)
    is_authenticated = False
    booking_timer = 0
    checkouthash = hashlib.sha256(str(uuid.uuid4()).encode('utf-8')).hexdigest()
    if 'ps_booking' in request.session:
        checkouthash =  hashlib.sha256(str(request.session["ps_booking"]).encode('utf-8')).hexdigest()
    #user_request = request.user
    #if user_request.is_authenticated is True:
    #    is_authenticated = True
   
    if 'is_authenticated' in request.session:
        if request.session['is_authenticated'] is True:
             is_authenticated = True

    if request.path.startswith('/ledger-api/payment-details'):
       booking_timer = 400
       if 'ps_booking' in request.session:
           try:
               booking = models.Booking.objects.get(pk=request.session['ps_booking'])
               booking_timer = (booking.expiry_time-timezone.now()).seconds if booking else -1      
           except:
               pass

    # staff need to login and logout for permissions to refresh
    parkstay_permissions_cache = cache.get('parkstay_url_permissions'+str(is_authenticated)+str(session_id))
    #parkstay_officers = ledger_api_utils.user_in_system_group(request.user.id,'Parkstay Officers')
    parkstay_officers = None
    if is_authenticated is True:
        parkstay_officers = ledger_api_utils.user_in_system_group(request.session['user_obj']['user_id'],'Parkstay Officers')
        
    parkstay_permissions = {'special_permissions': False}
    if parkstay_permissions_cache is None:
        for pg in models.ParkstayPermission.PERMISSION_GROUP:
            parkstay_permissions['p'+str(pg[0])] = False

        #if request.user.is_authenticated:
        if is_authenticated is True:
            #parkstay_permissions_obj = models.ParkstayPermission.objects.filter(email=request.user.email)
            parkstay_permissions_obj = models.ParkstayPermission.objects.filter(email=request.session['user_obj']['email'])
            for pp in parkstay_permissions_obj:
                if pp.active is True:
                   parkstay_permissions['p'+str(pp.permission_group)] = True
                   parkstay_permissions['special_permissions'] = True
        cache.set('parkstay_url_permissions'+str(is_authenticated)+str(session_id), json.dumps(parkstay_permissions),  86400)
    else:
        parkstay_permissions = json.loads(parkstay_permissions_cache)

    lt = utils.get_ledger_totals()
    public_site_closure = utils.public_site_closure()

    return {
        'EXPLORE_PARKS_SEARCH': '{}'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_CONTACT': '{}/contact-us'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_CONSERVE': '{}/know/conserving-our-parks'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_PEAK_PERIODS': '{}/know/when-visit'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_ENTRY_FEES': '{}/know/park-entry-fees'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_TERMS': '{}/know/online-camp-site-booking-terms-and-conditions'.format(settings.EXPLORE_PARKS_URL),
        'PARKSTAY_EXTERNAL_URL': settings.PARKSTAY_EXTERNAL_URL,
        'DEV_STATIC': settings.DEV_STATIC,
        'DEV_STATIC_URL': settings.DEV_STATIC_URL,
        'DEV_STATIC_SEARCH_AVAIL': settings.DEV_STATIC_SEARCH_AVAIL if hasattr(settings, 'DEV_STATIC_SEARCH_AVAIL') else None,
        'DEV_STATIC_SEARCH_AVAIL_URL': settings.DEV_STATIC_SEARCH_AVAIL_URL if hasattr(settings, 'DEV_STATIC_SEARCH_AVAIL_URL') else None,
        'VERSION_NO': settings.VERSION_NO,
        'WAITING_QUEUE_ENABLED': settings.WAITING_QUEUE_ENABLED,
        'GIT_COMMIT_DATE' : settings.GIT_COMMIT_DATE,
        'GIT_COMMIT_HASH' : settings.GIT_COMMIT_HASH,
        'QUEUE_DOMAIN' : settings.QUEUE_DOMAIN,
        'QUEUE_URL' : settings.QUEUE_URL,
        'QUEUE_ACTIVE_HOSTS' : settings.QUEUE_ACTIVE_HOSTS,
        'QUEUE_GROUP_NAME' : settings.QUEUE_GROUP_NAME,
        'LEDGER_UI_URL' : settings.LEDGER_UI_URL,
        'PARKSTAY_PERMISSIONS' : parkstay_permissions,
        'template_group' : 'parksv2',
        'LEDGER_SYSTEM_ID' : settings.PS_PAYMENT_SYSTEM_ID.replace("S","0"),
        'template_title' : '',
        'ledger_totals': lt,
        'parkstay_officers' : parkstay_officers,
        'booking_timer' : booking_timer,
        'checkouthash' : checkouthash,
        'public_site_closure' : public_site_closure
    }
