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
from parkstay import utils_cache
from parkstay import utils

def build_campground_calender(params):
        "Build Full Campground calender as DB is slow to query individually."
        today = date.today()
        start_date = params['start_date']
        period_days = params['period_days']
        release_start = None
        campground_id = None
        if 'campground_id' in params:
            campground_id = params['campground_id']

        end_date = start_date + timedelta(days=period_days)

        if 'status' in params:
            status = params['status']
        else:
            status={1: 'available', 2: 'booked', 3: 'closed'}

        try:
           campground_calender = {}

           cg = None
           if campground_id:
               cg = models.Campground.objects.filter(id=int(campground_id))
           else:
               cg = models.Campground.objects.all()

           for c in cg:
               print ("Campground ID "+str(c.id)+"")
               release_start = None
               data_file = settings.BASE_DIR+"/datasets/"+str(c.id)+"-campground-availablity.json"
               if os.path.isfile(data_file):
                  f = open(data_file, "r")
                  datajsonstring = f.read()
                  try:
                      campground_calender = json.loads(datajsonstring)
                  except: 
                      campground_calender = {'options': {}, 'campsites': {}, 'campsite_ids':[]}
               else:
                   campground_calender = {'options': {}, 'campsites': {}, 'campsite_ids':[]}

               release_period = utils.get_release_date_for_campground(c.id)

               if "release_date" in release_period:
                    if release_period["release_date"] is None:
                        pass
                    else:
                        release_start = release_period["release_date"] - timedelta(days=1)
                        
                        release_date_diff = 0
                        if release_start:
                            release_date_diff = end_date - release_period["release_date"]
               
           
            #    crd = models.CampgroundReleaseDate.objects.all().order_by('-id')
            #    release_start = None
            #    release_date_diff = None
            #    if crd.count() > 0:                    
            #         release_start = crd[0].release_date
            #         release_date_diff = end_date - crd[0].release_date
               
               campsites = models.Campsite.objects.filter(campground=c)
               # Build Campsite Period Dataset
               for cs in campsites:
                   if cs.id not in campground_calender['campsite_ids']:
                       campground_calender['campsite_ids'].append(cs.id)
                   if str(cs.id) not in campground_calender['campsites']:
                       campground_calender['campsites'][str(cs.id)] = {}

                   dayscount = 0
                   for day in range(0, period_days):
                       nextday = today + timedelta(days=day)
                       nextday_string = nextday.strftime('%Y-%m-%d')
                       campground_calender['campsites'][str(cs.id)][nextday_string] = status[1]
                    
               # campsite bookings cancelled make available
               csbooking_cancelled = models.CampsiteBooking.objects.filter(booking__is_canceled=True, campsite__in=campground_calender['campsite_ids'], date__gte=start_date, date__lte=end_date) 
               
               for csb in csbooking_cancelled:
                   date_string = csb.date.strftime('%Y-%m-%d')
                   if str(csb.campsite.id) in campground_calender['campsites']:
                       if date_string in campground_calender['campsites'][str(csb.campsite.id)]:
                            campground_calender['campsites'][str(csb.campsite.id)][date_string] = status[1]

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

                   for day in range(0, closure_diff.days):
                       nextday = closure_start + timedelta(days=day)
                       nextday_string = nextday.strftime('%Y-%m-%d')
                       for cs_id in campground_calender['campsite_ids']:
                           if str(cs_id) in campground_calender['campsites']:
                                if nextday_string in campground_calender['campsites'][str(cs_id)]:
                                     campground_calender['campsites'][str(cs_id)][nextday_string] = status[3]

               # Build Campground closures
               csbr_qs = models.CampsiteBookingRange.objects.filter(
                   Q(campsite__in=campground_calender['campsite_ids']),
                   Q(status=1),
                   Q(range_start__lt=end_date) & (Q(range_end__gte=start_date) | Q(range_end__isnull=True))
               )
               
               for closure in csbr_qs:
                   closure_start = closure.range_start
                   if closure.range_end:
                        closure_end = closure.range_end
                   else:
                        closure_end = end_date

                   closure_diff = closure_end - closure_start
                   for day in range(0, closure_diff.days):
                       nextday = closure_start + timedelta(days=day)
                       nextday_string = nextday.strftime('%Y-%m-%d')
                       if str(closure.campsite.id) in campground_calender['campsites']:
                           if nextday_string in campground_calender['campsites'][str(closure.campsite.id)]:
                                campground_calender['campsites'][str(closure.campsite.id)][nextday_string] = status[3]


               for cs in campsites:
                   dayscount = 0
                   for day in range(0, period_days):
                        nextday = today + timedelta(days=day)
                        nextday_string = nextday.strftime('%Y-%m-%d')

                        if release_start:

                            # if nextday == release_start:
                            #     nowtime = datetime.now()
                            #     nowdatetime_string = nowtime.strftime("%Y-%m-%d")
                            #     campground_release_time = '10:00:00'
                            #     if cs.campground.release_time:
                            #         campground_release_time = cs.campground.release_time.strftime("%H:%M:%S")

                            #     campground_opentime = datetime.strptime(nowdatetime_string+' '+campground_release_time, '%Y-%m-%d %H:%M:%S')
                            #     if nowtime > campground_opentime:
                            #         pass
                            #     else:
                            #         if str(cs.id) in campground_calender['campsites']:
                            #             print ("OPEN TODAY")                                    
                            #             if nextday_string in campground_calender['campsites'][str(cs.id)]:
                            #                 campground_calender['campsites'][str(cs.id)][nextday_string] = status[3]                                  
                                
                            if nextday > release_start:
                                if str(cs.id) in campground_calender['campsites']:
                                    if nextday_string in campground_calender['campsites'][str(cs.id)]:
                                        campground_calender['campsites'][str(cs.id)][nextday_string] = status[3]                         
                        else:                            
                            # 180 days plus 14 days booking period
                            if day > 193:
                                if str(cs.id) in campground_calender['campsites']:
                                    if nextday_string in campground_calender['campsites'][str(cs.id)]:
                                        campground_calender['campsites'][str(cs.id)][nextday_string] = status[3]                                




                     
               # campsite bookings
               csbooking = models.CampsiteBooking.objects.filter(booking__is_canceled=False, campsite__in=campground_calender['campsite_ids'], date__gte=start_date, date__lte=end_date) 
               
               for csb in csbooking:
                   date_string = csb.date.strftime('%Y-%m-%d')
                   if str(csb.campsite.id) in campground_calender['campsites']:
                       if date_string in campground_calender['campsites'][str(csb.campsite.id)]:
                            campground_calender['campsites'][str(csb.campsite.id)][date_string] = status[2]

               lcsbooking = models.CampsiteBookingLegacy.objects.filter(is_cancelled=False, campsite_id__in=campground_calender['campsite_ids'], date__gte=start_date, date__lte=end_date)
               for lcsb in lcsbooking:
                   date_string = lcsb.date.strftime('%Y-%m-%d')
                   if str(lcsb.campsite_id) in campground_calender['campsites']:
                         if date_string in campground_calender['campsites'][str(lcsb.campsite_id)]:
                                campground_calender['campsites'][str(lcsb.campsite_id)][date_string] = status[2]
                    
               f = open(data_file, "w")
               f.write(json.dumps(campground_calender, indent=4))
               f.close() 

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)



def build_campground_daily_calender(params):
        today = date.today()
        start_date = params['start_date']
        period_days = params['period_days']
        campground_id = None
        if 'campground_id' in params:
            campground_id = params['campground_id']

        end_date = start_date + timedelta(days=period_days)

        if 'status' in params:
            status = params['status']
        else:
            status={1: 'available', 2: 'booked', 3: 'closed'}
        try:
           daily_calender = {"campgrounds": {}}
           for day in range(0, params['period_days']+1):
               nextday = params['start_date'] + timedelta(days=day)
               nextday_string = nextday.strftime('%Y-%m-%d')
               print ("Building daily file for "+nextday_string)

               data_file = settings.BASE_DIR+"/datasets/daily/"+str(nextday_string)+"-availablity.json"
               cg = utils_cache.all_campgrounds()        
               for c in cg:
                    try:
                        cg_id = c['id']
                        cg_calender = {}
                        campground_data_file = settings.BASE_DIR+"/datasets/"+str(cg_id)+"-campground-availablity.json"
                        if os.path.isfile(campground_data_file):
                            f = open(campground_data_file, "r")
                            datajsonstring = f.read()
                            cg_calender = json.loads(datajsonstring)
                            #print (cg_calender)

                        if c['campground_type'] == 0:
                            daily_calender['campgrounds'][cg_id] = {}

                            campsites = utils_cache.all_campground_campsites(c['id'])
                           
                            for cs in campsites:
                                cs_id = cs['id']
                                avail_status = params['status'][1]
                                if 'campsites' in cg_calender:
                                    if str(cs_id) in cg_calender['campsites']:
                                        if nextday_string in cg_calender['campsites'][str(cs_id)]:
                                                avail_status = cg_calender['campsites'][str(cs_id)][nextday_string]

                                if cs_id not in daily_calender['campgrounds'][cg_id]:
                                    daily_calender['campgrounds'][cg_id][cs_id] = {}

                                daily_calender['campgrounds'][cg_id][cs_id][nextday_string] = avail_status
                    except Exception as e:
                        print ("ERROR Writing Daily")
                        print (e)


               f = open(data_file, "w")
               f.write(json.dumps(daily_calender, indent=4))
               f.close()

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)

