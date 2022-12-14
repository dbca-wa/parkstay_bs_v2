from django.core.management.base import BaseCommand
from django.utils import timezone
#from mooring.models import RegisteredVessels
from parkstay import models
from datetime import datetime
from django.conf import settings
import json
import requests

from datetime import timedelta, datetime

class Command(BaseCommand):
    help = 'Import campsite booking from legecy.'


    def add_arguments(self, parser):
        parser.add_argument('-d' '--days', type=str, help='Enter days please')


    def handle(self, *args, **options):

        try:
           print ("Importing Legacy Booking Campsite Records")
           days_arg = options['d__days']
           if days_arg:
              days_arg = int(days_arg)
           else:
              days_arg=1

           CAMPSITE_BOOKING_API_KEY = settings.CAMPSITE_BOOKING_API_KEY

           count = 0
           while (count < days_arg):
               print (count)
               nowtime = datetime.now() - timedelta(days=count)
               print (nowtime.strftime('%Y-%m-%d'))
               count = count + 1

               url = settings.LEGACY_BOOKING_URL + '/api/campsitebookings?api_key='+CAMPSITE_BOOKING_API_KEY+'&specified_date=true&lookup_date='+nowtime.strftime('%Y-%m-%d')
               #url = settings.LEGACY_BOOKING_URL + '/api/campsitebookings?api_key='+CAMPSITE_BOOKING_API_KEY+'&today_updates_only=true'
               json_resp = requests.get(url, verify=False)
               data = json_resp.json()
               nowtime = datetime.now()
               recordschanges =0 
               recordscreated =0
               for d in data:
                   cb = models.CampsiteBookingLegacy.objects.filter(campsite_booking_id=d['id'])
                   if cb.count() > 0:
                       cbl = cb[0]
                       cbl.campsite_booking_id=d['id']
                       cbl.campsite_id=d['campsite_id']
                       cbl.date=d['date']
                       cbl.booking_type=d['booking_type']
                       cbl.legacy_booking_id=d['booking_id']
                       cbl.updated = nowtime
                       cbl.is_cancelled = d['is_canceled']
                       cbl.save()
                       recordschanges = recordschanges + 1
                   else:
                        models.CampsiteBookingLegacy.objects.create(campsite_booking_id=d['id'],
                                                            campsite_id=d['campsite_id'],
                                                            date=d['date'],
                                                            booking_type=d['booking_type'],
                                                            legacy_booking_id=d['booking_id'],
                                                            is_cancelled = d['is_canceled']
                                                           )
                        recordscreated = recordscreated + 1
               print ("Records Updated "+str(recordschanges))
               print ("Records Created "+str(recordscreated))

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
