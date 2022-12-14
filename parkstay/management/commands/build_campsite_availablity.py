from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
#from mooring.models import RegisteredVessels
from parkstay import models
from datetime import datetime
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timedelta, date, timezone as timezone_dt
import requests
import json
import os
from datetime import timedelta

class Command(BaseCommand):
    help = 'Rebuild '

    def handle(self, *args, **options):
        today = date.today()
        start_date = today 
        period_days = 730 
        end_date = today + timedelta(days=period_days)
        status={1: 'available', 2: 'booked', 3: 'closed'}
        print ("Start Date")
        print (today)
        print ("End Date")
        print (end_date)

        try:
           campground_calender = {} 
           cg = models.Campground.objects.all()
           for c in cg:
               print ("CAMPGROUND ID"+str(c.id))
               data_file = settings.BASE_DIR+"/datasets/"+str(c.id)+"-campground-availablity.json"
               if os.path.isfile(data_file):
                  f = open(data_file, "r")
                  datajsonstring = f.read()
                  campground_calender = json.loads(datajsonstring)
               else:
                   campground_calender = {'options': {}, 'campsites': {}, 'campsite_ids':[]}
               campsites = models.Campsite.objects.filter(campground=c)
               # Build Campsite Period Dataset
               for cs in campsites:
                   campground_calender['campsite_ids'].append(cs.id)
                   campground_calender['campsites'][cs.id] = {}
                   dayscount = 0
                   for day in range(0, period_days):
                       nextday = today + timedelta(days=day)
                       nextday_string = nextday.strftime('%Y-%m-%d')
                       campground_calender['campsites'][cs.id][nextday_string] = status[1]

               # Build Campground Closure 
               cgbr_qs = models.CampgroundBookingRange.objects.filter(
                   Q(campground=c),
                   Q(status=1),
                   Q(range_start__lt=end_date) & (Q(range_end__gt=start_date) | Q(range_end__isnull=True))
               )

               for closure in cgbr_qs:
                   closure_start = closure.range_start
                   if closure.range_end:
                       closure_end = closure.range_end
                   else:
                       closure_end = end_date
                   closure_diff = closure_end - closure_start

                   for day in range(0, closure_diff.days+1):
                       nextday = closure_start + timedelta(days=day)
                       nextday_string = nextday.strftime('%Y-%m-%d')
                       for cs_id in campground_calender['campsite_ids']:
                           if cs_id in campground_calender['campsites']:
                                if nextday_string in campground_calender['campsites'][cs_id]:
                                     campground_calender['campsites'][cs_id][nextday_string] = status[3]

               # Build Campground closures
               csbr_qs = models.CampsiteBookingRange.objects.filter(
                   Q(campsite__in=campground_calender['campsite_ids']),
                   Q(status=1),
                   Q(range_start__lt=end_date) & (Q(range_end__gt=start_date) | Q(range_end__isnull=True))
               )

               for closure in csbr_qs:
                   closure_start = closure.range_start
                   if closure.range_end:
                        closure_end = closure.range_end
                   else:
                        closure_end = end_date

                   closure_diff = closure_end - closure_start
                   for day in range(0, closure_diff.days+1):
                       nextday = closure_start + timedelta(days=day)
                       nextday_string = nextday.strftime('%Y-%m-%d')
                       if closure.campsite.id in campground_calender['campsites']:
                           if nextday_string in campground_calender['campsites'][closure.campsite.id]:
                                campground_calender['campsites'][closure.campsite.id][nextday_string] = status[3]

               # campsite bookings
               csbooking = models.CampsiteBooking.objects.filter(booking__is_canceled=False, campsite__in=campground_calender['campsite_ids'], date__gt=start_date, date__lt=end_date) 
               for csb in csbooking:
                   date_string = csb.date.strftime('%Y-%m-%d')
                   if csb.campsite.id in campground_calender['campsites']:
                       if date_string in campground_calender['campsites'][csb.campsite.id]:
                            campground_calender['campsites'][csb.campsite.id][date_string] = status[2]

               lcsbooking = models.CampsiteBookingLegacy.objects.filter(is_cancelled=False, campsite_id__in=campground_calender['campsite_ids'], date__gt=start_date, date__lt=end_date)
               print ("LEGACY")
               for lcsb in lcsbooking:
                   date_string = lcsb.date.strftime('%Y-%m-%d')
                   print (lcsb.campsite_id)
                   if lcsb.campsite_id in campground_calender['campsites']:
                         if date_string in campground_calender['campsites'][lcsb.campsite_id]:
                                campground_calender['campsites'][lcsb.campsite_id][date_string] = status[2]
                    
               f = open(data_file, "w")
               f.write(json.dumps(campground_calender, indent=4))
               f.close() 


           print ("Completed")
        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
