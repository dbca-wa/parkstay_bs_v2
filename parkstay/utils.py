from datetime import datetime, timedelta, date, timezone as timezone_dt
import logging
import traceback
import threading
from decimal import Decimal
from django.conf import settings
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils import timezone

#from ledger.payments.models import Invoice, CashTransaction
from ledger_api_client.ledger_models import Invoice
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from ledger_api_client.utils import oracle_parser, update_payments
from ledger_api_client.utils import create_basket_session, create_checkout_session, place_order_submission, use_existing_basket, use_existing_basket_from_invoice, calculate_excl_gst
from parkstay import models as parkstay_models
from parkstay.models import (Campground, Campsite, CampsiteRate, CampsiteBooking, Booking, BookingInvoice, CampsiteBookingRange, CampgroundBookingRange, CampgroundStayHistory, ParkEntryRate, BookingVehicleRego, CampsiteBookingLegacy)
from parkstay.serialisers import BookingRegoSerializer, ParkEntryRateSerializer, RateSerializer
from parkstay.emails import send_booking_invoice, send_booking_confirmation
from parkstay.exceptions import BindBookingException
from parkstay import booking_availability
import hashlib
import json
#from ledger.basket.models import Basket

###### WRITE order api to ledger_api_client.order to retreive order information
#from oscar.apps.order.models import Order 
from ledger_api_client.utils import Order

#############################################################################
logger = logging.getLogger('booking_checkout')


def create_booking_by_class(request,campground_id, multiplesites_class_totals, start_date, end_date, num_adult=0, num_concession=0, num_child=0, num_infant=0, num_vehicle=0,num_motorcycle=0,num_campervan=0,num_trailer=0, num_caravan=0, old_booking=None):
    """Create a new temporary booking in the system."""

    user_logged_in = None
    if request.user.is_authenticated:
           user_logged_in = request.user


    # get campground
    campground = Campground.objects.get(pk=campground_id)

    num_adult_pool = num_adult
    num_concession_pool = num_concession
    num_child_pool = num_child
    num_infant_pool = num_infant

    min_people = 0
    max_people = 0
    max_vehicles = 0
    for ms in multiplesites_class_totals.keys():
        msrange = int(multiplesites_class_totals[ms]) + 1
        campsite_class_id = ms
        for x in range(1, msrange):

            # fetch all the campsites and applicable rates for the campground
            sites_qs = Campsite.objects.filter(
                campground=campground,
                campsite_class=campsite_class_id
            )
            min_people = min_people + sites_qs[0].min_people
            max_people = max_people + sites_qs[0].max_people 
            max_vehicles = max_vehicles  + sites_qs[0].max_vehicles
    # TODO: date range check business logic
    # TODO: number of people check? this is modifiable later, don't bother
    if num_vehicle > max_vehicles:
        raise ValidationError('Number of vehicle is more than allowed for total campsite selected.')


    # the CampsiteBooking table runs the risk of a race condition,
    # wrap all this behaviour up in a transaction
    with transaction.atomic():

        # Create a new temporary booking with an expiry timestamp 
        booking = Booking.objects.create(
            booking_type=3,
            arrival=start_date,
            departure=end_date,
            details={
                'num_adult': num_adult,
                'num_concession': num_concession,
                'num_child': num_child,
                'num_infant': num_infant,
                'num_vehicle': num_vehicle,
                'num_campervan' : num_campervan,
                'num_motorcycle' : num_motorcycle,
                'num_trailer' : num_trailer,
                'num_caravan' : num_caravan
            },
            expiry_time=timezone.now() + timedelta(seconds=settings.BOOKING_TIMEOUT),
            campground=campground,
            old_booking=old_booking,
            campsite_oracle_code=campground.oracle_code
        )

        row_num_adult = 0
        row_num_concession = 0
        row_num_child = 0
        row_num_infant = 0

        for ms in multiplesites_class_totals.keys():
            msrange = int(multiplesites_class_totals[ms]) + 1
            campsite_class_id = ms

            for x in range(1, msrange):

                # fetch all the campsites and applicable rates for the campground
                sites_qs = Campsite.objects.filter(
                    campground=campground,
                    campsite_class=campsite_class_id
                )

                ground = {"id": campground_id}     
                sites_qs_bs = booking_availability.get_campsites_for_campground(ground,'all')   
                sites_array = []
                for s in sites_qs_bs:  
                    for cs in sites_qs:
                        if s['id'] == cs.id:        
                            sites_array.append({'pk': s['id'], 'data': s})

                row_num_adult = 0
                row_num_concession = 0
                row_num_child = 0
                row_num_infant = 0

                rna = sites_qs[0].max_people

                if rna > 0:
                    if num_adult_pool >= rna:
                         row_num_adult = rna
                         num_adult_pool = num_adult_pool - rna
                         rna = rna - rna
                    else:
                        if num_adult_pool > 0:
                          row_num_adult = num_adult_pool
                          rna = rna - row_num_adult
                          num_adult_pool = num_adult_pool - num_adult_pool
                if rna > 0:
                    if num_concession_pool >= rna:
                          row_num_concession = rna
                          num_concession_pool = num_concession_pool - rna
                          rna = rna - rna
                    else:
                        if num_concession_pool > 0:
                            row_num_concession = num_concession_pool
                            rna = rna - num_concession_pool
                            num_concession_pool = num_concession_pool - num_concession_pool

                if rna > 0:
                    if num_child_pool >= rna:
                        row_num_child = rna
                        num_child_pool = num_child_pool - rna
                        rna = rna - rna
                    else:
                        if num_child_pool > 0:
                           row_num_child = num_child_pool
                           rna = rna - num_child_pool
                           num_child_pool = num_child_pool - num_child_pool

                if rna > 0:
                    if num_infant_pool >= rna:
                        row_num_infant = rna
                        num_infant_pool = num_infant_pool - rna
                        rna = rna - rna
                    else:
                        if num_infant_pool > 0:
                           row_num_infant = num_infant_pool
                           rna = rna - num_child_pool
                           num_infant_pool = num_infant_pool - num_infant_pool

                #ground = booking_availability.get_campground(campground_id)
                #sites_qs = get_campsites_for_campground(ground,gear_type)
                #sites_array = []
                #for s in sites_qs:
                #    sites_array.append({'pk': s['id'], 'data': s})

                if not sites_qs.exists():
                    raise ValidationError('No matching campsites found.')
                # get availability for sites, filter out the non-clear runs
                #availability = get_campsite_availability(sites_qs, start_date, end_date, user_logged_in,old_booking)
                availability = booking_availability.get_campsite_availability(campground.id,sites_array, start_date, end_date,user_logged_in, old_booking)
                excluded_site_ids = set()
                for site_id, dates in availability.items():
                    if not all([v[0] == 'open' for k, v in dates.items()]):
                        excluded_site_ids.add(site_id)
                # create a list of campsites without bookings for that period
                sites = [x for x in sites_qs if x.pk not in excluded_site_ids]

                if not sites:
                    raise ValidationError('Campsite class unavailable for specified time period.')

                # TODO: add campsite sorting logic based on business requirements
                # for now, pick the first campsite in the list
                site = sites[0]

                # Prevent booking if max people passed
                total_people = num_adult + num_concession + num_child # + num_infant
                
                if total_people > max_people:
                    raise ValidationError('Maximum number of people exceeded for the selected campsite')
                # Prevent booking if less than min people
                if total_people < min_people:
                    raise ValidationError('Number of people is less than the minimum allowed for the selected campsite')
 
                ## Create a new temporary booking with an expiry timestamp (default 20mins)
                #booking = Booking.objects.create(
                #    booking_type=3,
                #    arrival=start_date,
                #    departure=end_date,
                #    details={
                #        'num_adult': num_adult,
                #        'num_concession': num_concession,
                #        'num_child': num_child,
                #        'num_infant': num_infant,
                #        'num_vehicle': num_vehicle,
                #        'num_campervan' : num_campervan,
                #        'num_motorcycle' : num_motorcycle,
                #        'num_trailer' : num_trailer,
                #        'num_caravan' : num_caravan
                #    },
                #    expiry_time=timezone.now() + timedelta(seconds=settings.BOOKING_TIMEOUT),
                #    campground=campground,
                #    old_booking=old_booking,
                #    campsite_oracle_code=sites_qs[0].campground.oracle_code
                #)


                daily_rate_hash = {}
                daily_rates = [get_campsite_current_rate(request, c, booking.arrival.strftime('%Y-%m-%d'), booking.departure.strftime('%Y-%m-%d')) for c in sites_qs]
                for dr in daily_rates[0]:
                    daily_rate_hash[dr['date']] = dr



                for i in range((end_date - start_date).days):
                    cs=site
                    booking_date = start_date + timedelta(days=i)

                    total_amount_adult = Decimal(daily_rate_hash[str(booking_date)]['rate']['adult']) * int(row_num_adult)
                    total_amount_concession = Decimal(daily_rate_hash[str(booking_date)]['rate']['concession']) * int(row_num_concession)
                    total_amount_child = Decimal(daily_rate_hash[str(booking_date)]['rate']['child']) * int(row_num_child)
                    total_amount_infant = Decimal(daily_rate_hash[str(booking_date)]['rate']['infant']) * int(row_num_infant)
                    total_day_amount = total_amount_adult + total_amount_concession + total_amount_child + total_amount_infant
                    booking_policy_id = daily_rate_hash[str(booking_date)]['booking_policy']

                    BP = None
                    if booking_policy_id:

                        BP_obj = parkstay_models.BookingPolicy.objects.filter(id=booking_policy_id, active=True)
                        if BP_obj.count() > 0:
                            BP = BP_obj[0]
                        else:
                            raise ValidationError("This campground does not contain an active booking policy")

                    else:
                        raise ValidationError("This campground does not contain a booking policy")



                    cb = CampsiteBooking.objects.create(
                        campsite=cs,
                        booking_type=3,
                        date=start_date + timedelta(days=i),
                        booking=booking,
                        booking_policy=BP,
                        amount_adult=total_amount_adult,
                        amount_infant=total_amount_infant,
                        amount_child=total_amount_child,
                        amount_concession=total_amount_concession
                    )

    # On success, return the temporary booking
    return booking

def create_booking_by_site(request,sites_qs, start_date, end_date, num_adult=0, num_concession=0, num_child=0, num_infant=0,num_vehicle=0,num_campervan=0,num_motorcycle=0,num_trailer=0, num_caravan=0, cost_total=0, override_price=None, override_reason=None, override_reason_info=None, send_invoice=False, overridden_by=None, customer=None, updating_booking=False, override_checks=False,  do_not_send_invoice=False,old_booking=None):
    """Create a new temporary booking in the system for a set of specific campsites."""


    user_logged_in = None
    if request.user.is_authenticated:
           user_logged_in = request.user

    # the CampsiteBooking table runs the risk of a race condition,
    # wrap all this behaviour up in a transaction 
    #old_booking_id = None
    #if old_booking:
    #    old_booking_id = old_booking
    sites_array = []
    campsite_qs = Campsite.objects.filter(pk__in=sites_qs)
    ground = {"id": campsite_qs[0].campground.id}     
    sites_qs = booking_availability.get_campsites_for_campground(ground,'all')   

    for s in sites_qs:  
        for cs in campsite_qs:
            if s['id'] == cs.id:        
                sites_array.append({'pk': s['id'], 'data': s})

    num_adult_pool = num_adult
    num_concession_pool = num_concession
    num_child_pool = num_child
    num_infant_pool = num_infant
    selecttype = request.POST.get('selecttype',None)
    multiplesites = json.loads(request.POST.get('multiplesites', "[]"))
    total_vehicle = num_vehicle + num_campervan + num_trailer + num_caravan 
    total_vehicle = total_vehicle + (num_motorcycle / 2)

    with transaction.atomic():
        # get availability for campsite, error out if booked/closed
        user = overridden_by

        availability = booking_availability.get_campsite_availability(campsite_qs[0].campground.id,sites_array, start_date, end_date,user_logged_in, old_booking)

        for site_id, dates in availability.items():

            if not override_checks:
                if updating_booking:
                    if not all([v[0] in ['open', 'tooearly'] for k, v in dates.items()]):
                        raise ValidationError("Someone hit 'Book now' before you and campsite availability changed after this webpage was loaded. <BR>Reload the page using your browser controls to update availability information.")
                else:
                    if not all([v[0] == 'open' for k, v in dates.items()]):
                        raise ValidationError("Someone hit 'Book now' before you and campsite availability changed after this webpage was loaded. <BR>Reload the page using your browser controls to update availability information.")
            else:

                if not all([v[0] in ['open', 'tooearly', 'closed', 'closed & booked'] for k, v in dates.items()]):
                    raise ValidationError("Someone hit 'Book now' before you and campsite availability changed after this webpage was loaded. <BR>Reload the page using your browser controls to update availability information.")

        if not override_checks:
            # Prevent booking if max people passed
            total_people = num_adult + num_concession + num_child #+ num_infant
            min_people = sum([cs.min_people for cs in campsite_qs])
            max_people = sum([cs.max_people for cs in campsite_qs])
            max_vehicles = sum([cs.max_vehicles for cs in campsite_qs])
                
            if total_vehicle > max_vehicles:
                raise ValidationError('Number of vehicle is more than allowed for total campsite selected.')

            if total_people > max_people:
                raise ValidationError('Maximum number of people exceeded for the selected campsite(s)')
            # Prevent booking if less than min people
            if total_people < min_people:
                raise ValidationError('Number of people is less than the minimum allowed for the selected campsite(s)')

        # Create a new temporary booking with an expiry timestamp (default 20mins)
        booking = Booking.objects.create(
            booking_type=3,
            arrival=start_date,
            departure=end_date,
            details={
                'num_adult': num_adult,
                'num_concession': num_concession,
                'num_child': num_child,
                'num_infant': num_infant,
                'num_vehicle': num_vehicle,
                'num_campervan' : num_campervan,
                'num_motorcycle' : num_motorcycle,
                'num_trailer' : num_trailer,
                'num_caravan' : num_caravan,
                'multiplesites': multiplesites,
                'selecttype' : selecttype
            },
            cost_total=cost_total,
            override_price=Decimal(override_price) if (override_price is not None) else None,
            override_reason=override_reason,
            override_reason_info=override_reason_info,
            send_invoice=send_invoice,
            overridden_by=overridden_by,
            expiry_time=timezone.now() + timedelta(seconds=settings.BOOKING_TIMEOUT),
            campground=campsite_qs[0].campground,
            customer=customer,
            do_not_send_invoice=do_not_send_invoice,
            old_booking=old_booking,
            campsite_oracle_code=campsite_qs[0].campground.oracle_code
        )
                 
        daily_rate_hash = {}
        daily_rates = [get_campsite_current_rate(request, c, booking.arrival.strftime('%Y-%m-%d'), booking.departure.strftime('%Y-%m-%d')) for c in campsite_qs]
        for dr in daily_rates[0]:
            daily_rate_hash[dr['date']] = dr
        total_cost_calculated = Decimal('0.00')
        for cs in campsite_qs:
            #num_adult_pool = num_adult
            #num_concession_pool = num_concession
            #num_child_pool = num_child
            #num_infant_pool = num_infant

            #for i in range((end_date - start_date).days):
            #    booking_date = start_date + timedelta(days=i)
            row_num_adult = 0
            row_num_concession = 0
            row_num_child = 0
            row_num_infant = 0
            #print ("ADULT POOL")
            #print (num_adult_pool)
            rna = cs.max_people

            if rna > 0:
                if num_adult_pool >= rna:
                     row_num_adult = rna 
                     num_adult_pool = num_adult_pool - rna
                     rna = rna - rna
                else:
                    if num_adult_pool > 0:
                      row_num_adult = num_adult_pool
                      rna = rna - row_num_adult
                      num_adult_pool = num_adult_pool - num_adult_pool
            if rna > 0:
                if num_concession_pool >= rna:
                      row_num_concession = rna
                      num_concession_pool = num_concession_pool - rna
                      rna = rna - rna
                else:
                    if num_concession_pool > 0:
                        row_num_concession = num_concession_pool
                        rna = rna - num_concession_pool
                        num_concession_pool = num_concession_pool - num_concession_pool

            if rna > 0:
                if num_child_pool >= rna:
                    row_num_child = rna
                    num_child_pool = num_child_pool - rna
                    rna = rna - rna
                else:
                    if num_child_pool > 0:
                       row_num_child = num_child_pool
                       rna = rna - num_child_pool
                       num_child_pool = num_child_pool - num_child_pool

            if rna > 0:
                if num_infant_pool >= rna:
                    row_num_infant = rna
                    num_infant_pool = num_infant_pool - rna
                    rna = rna - rna
                else:
                    if num_infant_pool > 0:
                       row_num_infant = num_infant_pool
                       rna = rna - num_child_pool
                       num_infant_pool = num_infant_pool - num_infant_pool


            for i in range((end_date - start_date).days):
                booking_date = start_date + timedelta(days=i)

               
                total_amount_adult = Decimal(daily_rate_hash[str(booking_date)]['rate']['adult']) * int(row_num_adult)
                total_amount_concession = Decimal(daily_rate_hash[str(booking_date)]['rate']['concession']) * int(row_num_concession)
                total_amount_child = Decimal(daily_rate_hash[str(booking_date)]['rate']['child']) * int(row_num_child)
                total_amount_infant = Decimal(daily_rate_hash[str(booking_date)]['rate']['infant']) * int(row_num_infant)

                total_day_amount = total_amount_adult + total_amount_concession + total_amount_child + total_amount_infant 
                booking_policy_id = daily_rate_hash[str(booking_date)]['booking_policy']

                BP = None
                if booking_policy_id:
                    BP_obj = parkstay_models.BookingPolicy.objects.filter(id=booking_policy_id, active=True)
                    if BP_obj.count() > 0:
                        BP = BP_obj[0]
                    else:
                        raise ValidationError("This campground does not contain an active booking policy")
                
                else:
                    raise ValidationError("This campground does not contain a booking policy")
                
                total_cost_calculated = total_cost_calculated + total_day_amount
                cb = CampsiteBooking.objects.create(
                    campsite=cs,
                    booking_type=3,
                    date=start_date + timedelta(days=i),
                    booking=booking,
                    booking_policy=BP,
                    amount_adult=total_amount_adult,
                    amount_infant=total_amount_infant,
                    amount_child=total_amount_child,
                    amount_concession=total_amount_concession
                )

    booking.cost_total = total_cost_calculated
    booking.save()
    # On success, return the temporary booking
    return booking


def get_open_campgrounds(campsites_qs, start_date, end_date):
    """Fetch the set of campgrounds (from a set of campsites) with spaces open over a range of visit dates."""
    # short circuit: if start date is before today, return nothing
    today = date.today()
    if start_date < today:
        return set()

    # remove from the campsite list any entries with bookings
    campsites_qs = campsites_qs.exclude(
        campsitebooking__date__range=(start_date, end_date - timedelta(days=1))
        # and also campgrounds where the book window is outside of the max advance range
    ).exclude(
        campground__max_advance_booking__lt=(start_date - today).days
    )

    # get closures at campsite and campground level
    cgbr_qs = CampgroundBookingRange.objects.filter(
        Q(campground__in=[x[0] for x in campsites_qs.distinct('campground').values_list('campground')]),
        Q(status=1),
        Q(range_start__lt=end_date) & (Q(range_end__gt=start_date) | Q(range_end__isnull=True))
    )
    cgbr = set([x[0] for x in cgbr_qs.values_list('campground')])

    csbr_qs = CampsiteBookingRange.objects.filter(
        Q(campsite__in=campsites_qs),
        Q(status=1),
        Q(range_start__lt=end_date) & (Q(range_end__gt=start_date) | Q(range_end__isnull=True))
    )
    csbr = set([x[0] for x in csbr_qs.values_list('campsite')])

    # generate a campground-to-campsite-list map with closures removed
    campground_map = {}
    for cs in campsites_qs:
        if (cs.pk in csbr) or (cs.campground.pk in cgbr):
            continue
        if cs.campground.pk not in campground_map:
            campground_map[cs.campground.pk] = []
        campground_map[cs.campground.pk].append(cs.pk)

    return set(campground_map.keys())


def get_campsite_availability(campsites_qs, start_date, end_date, user = None, old_booking=None):
    nowtime = datetime.now()
    can_make_advanced_booking = False
    if user:
        if parkstay_models.ParkstayPermission.objects.filter(email=user.email,permission_group=5).count() > 0:
             can_make_advanced_booking = True

    sa_qy = []
    for s in campsites_qs:
          sa_qy.append(s.id)


    # Added line to use is_officer from helper methods
    from parkstay.helpers import is_officer
    """Fetch the availability of each campsite in a queryset over a range of visit dates."""
    if old_booking is not None:
    # fetch all of the single-day CampsiteBooking objects within the date range for the sites
         bookings_qs = CampsiteBooking.objects.filter(
             campsite__in=campsites_qs,
             date__gte=start_date,
             date__lt=end_date,
             booking__is_canceled=False,
         ).exclude(booking_id=old_booking).exclude(booking_type=3,booking__expiry_time__lt=nowtime).order_by('date', 'campsite__name')
    else:
         bookings_qs = CampsiteBooking.objects.filter(
             campsite__in=campsites_qs,
             date__gte=start_date,
             date__lt=end_date,
             booking__is_canceled=False,
         ).exclude(booking_type=3,booking__expiry_time__lt=nowtime).order_by('date', 'campsite__name')

    legacy_bookings = CampsiteBookingLegacy.objects.filter(campsite_id__in=sa_qy,
                                                            date__gte=start_date,
                                                            date__lt=end_date,
                                                            is_cancelled=False
                                                            )

    # prefill all slots as 'open'
    duration = (end_date - start_date).days
    results = {site.pk: {start_date + timedelta(days=i): ['open', None] for i in range(duration)} for site in campsites_qs}

    # generate a campground-to-campsite-list map
    campground_map = {cg[0]: [cs.pk for cs in campsites_qs if cs.campground.pk == cg[0]] for cg in campsites_qs.distinct('campground').values_list('campground')}
    print ("CAMPGROUND MAP")
    # strike out whole campground closures
    cgbr_qs = CampgroundBookingRange.objects.filter(
        Q(campground__in=campground_map.keys()),
        Q(status=1),
        Q(range_start__lt=end_date) & (Q(range_end__gte=start_date) | Q(range_end__isnull=True)),
    )
    for closure in cgbr_qs:
        start = max(start_date, closure.range_start)
        end = min(end_date, closure.range_end) if closure.range_end else end_date
        today = date.today()
        reason = closure.closure_reason.text
        diff = (end - start).days
        for i in range(diff):
            for cs in campground_map[closure.campground.pk]:
                if start + timedelta(days=i) == today:
                    if not closure.campground._is_open(start + timedelta(days=i)):
                        if start + timedelta(days=i) in results[cs]:
                            results[cs][start + timedelta(days=i)][0] = 'closed'
                            results[cs][start + timedelta(days=i)][1] = str(reason)
                else:
                    if start + timedelta(days=i) in results[cs]:
                        results[cs][start + timedelta(days=i)][0] = 'closed'
                        results[cs][start + timedelta(days=i)][1] = str(reason)

    # strike out campsite closures
    csbr_qs = CampsiteBookingRange.objects.filter(
        Q(campsite__in=campsites_qs),
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
                if not closure.campsite._is_open(start + timedelta(days=i)):
                    if start + timedelta(days=i) in results[closure.campsite.pk]:
                        results[closure.campsite.pk][start + timedelta(days=i)][0] = 'closed'
                        results[closure.campsite.pk][start + timedelta(days=i)][1] = str(reason)
            else:
                if start + timedelta(days=i) in results[closure.campsite.pk]:
                    results[closure.campsite.pk][start + timedelta(days=i)][0] = 'closed'
                    results[closure.campsite.pk][start + timedelta(days=i)][1] = str(reason)

    # strike out black bookings

    for lb in legacy_bookings:
        if lb.booking_type == 2:
             results[lb.campsite_id][lb.date][0] = 'closed'

    for b in bookings_qs.filter(booking_type=2):
        results[b.campsite.pk][b.date][0] = 'closed'

    # add booking status for real bookings
    # for b in bookings_qs.exclude(booking_type=2):

    #legacy bookings
    for lb in legacy_bookings.exclude(booking_type=2):
        if lb.booking_type != 2:
           if results[lb.campsite_id][lb.date][0] == 'closed':
               results[lb.campsite_id][lb.date][0] = 'closed & booked'
           else:
               print ("BOOKED")
               results[lb.campsite_id][lb.date][0] = 'booked'

    for b in bookings_qs.exclude(booking_type=2):
        if results[b.campsite.pk][b.date][0] == 'closed':
            results[b.campsite.pk][b.date][0] = 'closed & booked'
        else:
            results[b.campsite.pk][b.date][0] = 'booked'

    # strike out days before today
    today = date.today()
    if start_date < today:
        for i in range((min(today, end_date) - start_date).days):
            for key, val in results.items():
                #important to add back in checks
                pass
                #val[start_date + timedelta(days=i)][0] = 'tooearly'
                if old_booking is not None:
                    if old_booking > 0 and start_date <= today:
                       print ("changing booking after arriving")
                       pass
                    else:
                         val[start_date + timedelta(days=i)][0] = 'tooearly'
                else:
                    val[start_date + timedelta(days=i)][0] = 'tooearly'




    # strike out days after the max_advance_booking
    if user == None or (not can_make_advanced_booking):
        for site in campsites_qs:
            stop = today + timedelta(days=site.campground.max_advance_booking)
            stop_mark = min(max(stop, start_date), end_date)
            if start_date > stop:
                for i in range((end_date - stop_mark).days):
                    results[site.pk][stop_mark + timedelta(days=i)][0] = 'toofar'
    # Added this section to allow officers to book camp dated after the max_advance_booking
    elif user != None and can_make_advanced_booking:
        pass

    # Get the current stay history
    stay_history = CampgroundStayHistory.objects.filter(
        Q(range_start__lte=start_date, range_end__gte=start_date) |  # filter start date is within period
        Q(range_start__lte=end_date, range_end__gte=end_date) |  # filter end date is within period
        Q(Q(range_start__gt=start_date, range_end__lt=end_date) & Q(range_end__gt=today)),  # filter start date is before and end date after period
        campground=campsites_qs.first().campground)
    if stay_history:
        max_days = min([x.max_days for x in stay_history])
    else:
        max_days = settings.PS_MAX_BOOKING_LENGTH

    # strike out days after the max_stay period
    if user == None or (not can_make_advanced_booking):
        for site in campsites_qs:
            stop = start_date + timedelta(days=max_days)
            stop_mark = min(max(stop, start_date), end_date)
            for i in range((end_date - stop_mark).days):
                results[site.pk][stop_mark + timedelta(days=i)][0] = 'toofar'
    # Added this section to allow officers to book camp dated after the max_advance_booking
    elif user != None and can_make_advanced_booking:
        pass

    return results


def get_visit_rates(campsites_qs, start_date, end_date):
    """Fetch the per-day pricing for each visitor type over a range of visit dates."""
    # fetch the applicable rates for the campsites
    rates_qs = CampsiteRate.objects.filter(
        Q(campsite__in=campsites_qs),
        Q(date_start__lt=end_date) & (Q(date_end__gte=start_date) | Q(date_end__isnull=True))
    ).prefetch_related('rate')
   
    # prefill all slots
    duration = (end_date - start_date).days
    results = {
        site.pk: {
            start_date + timedelta(days=i): {
                'adult': Decimal('0.00'),
                'child': Decimal('0.00'),
                'concession': Decimal('0.00'),
                'infant': Decimal('0.00')
            } for i in range(duration)
        } for site in campsites_qs
    }

    # make a record of the earliest CampsiteRate for each site
    early_rates = {}
    for rate in rates_qs:
        if rate.campsite.pk not in early_rates:
            early_rates[rate.campsite.pk] = rate
        elif early_rates[rate.campsite.pk].date_start > rate.date_start:
            early_rates[rate.campsite.pk] = rate

        # for the period of the visit overlapped by the rate, set the amounts
        start = max(start_date, rate.date_start)

        # End and start date are the same leading to the lod rate enot going thru the loop
        # Add 1 day if date_end exists(to cover all days before the new rate),previously it was skipping 2 days before the new rate date
        if(rate.date_end):
            rate.date_end += timedelta(days=1)

        end = min(end_date, rate.date_end) if rate.date_end  else end_date
        for i in range((end-start).days):
            results[rate.campsite.pk][start+timedelta(days=i)]['adult'] = rate.rate.adult
            results[rate.campsite.pk][start+timedelta(days=i)]['concession'] = rate.rate.concession
            results[rate.campsite.pk][start+timedelta(days=i)]['child'] = rate.rate.child
            results[rate.campsite.pk][start+timedelta(days=i)]['infant'] = rate.rate.infant

    # complain if there's a Campsite without a CampsiteRate
    if len(early_rates) < rates_qs.count():
        print('Missing CampsiteRate coverage!')
    # for ease of testing against the old datasets, if the visit dates are before the first
    # CampsiteRate date, use that CampsiteRate as the pricing model.
    for site_pk, rate in early_rates.items():
        if start_date < rate.date_start:
            start = start_date
            end = rate.date_start
            for i in range((end - start).days):
                results[site_pk][start + timedelta(days=i)]['adult'] = rate.rate.adult
                results[site_pk][start + timedelta(days=i)]['concession'] = rate.rate.concession
                results[site_pk][start + timedelta(days=i)]['child'] = rate.rate.child
                results[site_pk][start + timedelta(days=i)]['infant'] = rate.rate.infant
    return results


def get_available_campsitetypes(campground_id, start_date, end_date, _list=True):
    try:
        cg = Campground.objects.get(id=campground_id)

        if _list:
            available_campsiteclasses = []
        else:
            available_campsiteclasses = {}

        for _class in cg.campsite_classes:
            sites_qs = Campsite.objects.filter(
                campground=campground_id,
                campsite_class=_class
            )

            if sites_qs.exists():
                # get availability for sites, filter out the non-clear runs
                availability = get_campsite_availability(sites_qs, start_date, end_date)
                sites = {}
                for site_id, dates in availability.items():
                    some_booked = any([v[0] == 'booked' for k, v in dates.items()])
                    some_closed = any([v[0] == 'closed' for k, v in dates.items()])
                    some_closed_and_booked = any([v[0] == 'closed & booked' for k, v in dates.items()])

                    if some_closed_and_booked or (some_booked and some_closed):
                        sites[site_id] = 'closed & booked'
                    elif some_booked:
                        sites[site_id] = 'booked'
                    elif some_closed:
                        sites[site_id] = 'closed'
                    else:
                        sites[site_id] = 'open'

                if sites:
                    if not _list:
                        available_campsiteclasses[_class] = sites
                    else:
                        available_campsiteclasses.append(_class)

        return available_campsiteclasses
    except Campground.DoesNotExist:
        raise Exception('The campsite you are searching does not exist')
    except BaseException:
        raise


def get_available_campsites_list(campsite_qs, request, start_date, end_date):
    from parkstay.serialisers import CampsiteSerialiser
    user = request.user
    campsites = get_campsite_availability(campsite_qs, start_date, end_date, user)
    available = []

    for site_id, dates in campsites.items():
        some_booked = any([v[0] == 'booked' for k, v in dates.items()])
        some_closed = any([v[0] == 'closed' for k, v in dates.items()])
        some_closed_and_booked = any([v[0] == 'closed & booked' for k, v in dates.items()])

        if some_closed_and_booked or (some_booked and some_closed):
            av = 'closed & booked'
        elif some_booked:
            av = 'booked'
        elif some_closed:
            av = 'closed'
        else:
            av = 'open'
        available.append(CampsiteSerialiser(Campsite.objects.get(id=site_id), context={'request': request, 'status': av}).data)
        available.sort(key=lambda x: x['name'])
    return available


def get_available_campsites_list_booking(campsite_qs, request, start_date, end_date, booking):
    '''
        Used to get the available campsites in the selected period
        and the ones currently attached to a booking
    '''
    from parkstay.serialisers import CampsiteSerialiser
    campsites = get_campsite_availability(campsite_qs, start_date, end_date)
    available = []
    for site_id, dates in campsites.items():
        some_booked = any([v[0] == 'booked' for k, v in dates.items()])
        some_closed = any([v[0] == 'closed' for k, v in dates.items()])
        some_closed_and_booked = any([v[0] == 'closed & booked' for k, v in dates.items()])
        if some_closed_and_booked or (some_booked and some_closed):
            av = 'closed & booked'
        elif some_booked:
            av = 'booked'
        elif some_closed:
            av = 'closed'
        else:
            av = 'open'
        available.append(CampsiteSerialiser(Campsite.objects.filter(id=site_id), many=True, context={'request': request, 'status': av}).data[0])
    return available


def get_campsite_current_rate(request, campsite_id, start_date, end_date):
    res = []
    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        for single_date in daterange(start_date, end_date):
            price_history = CampsiteRate.objects.filter(campsite=campsite_id, date_start__lte=single_date).order_by('-date_start')
            if price_history:
                rate = RateSerializer(price_history[0].rate, context={'request': request}).data
                rate['campsite'] = campsite_id
                booking_policy = None
                if price_history[0].booking_policy:
                    booking_policy = price_history[0].booking_policy.id
                res.append({
                    "date": single_date.strftime("%Y-%m-%d"),
                    "rate": rate,
                    "booking_policy" : booking_policy
                })
    return res


def get_campsites_current_rate(request, campsites, start_date, end_date):
    res = []
    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        for single_date in daterange(start_date, end_date):
            price_history = CampsiteRate.objects.filter(campsite__in=campsites, date_start__lte=single_date).order_by('-date_start')
            campsite_prices = {}
            for p in price_history:
                if p.campsite_id not in campsite_prices:
                    campsite_prices[p.campsite_id] = p
                else:
                    if p.date_start > campsite_prices[p.campsite_id].date_start:
                        campsite_prices[p.campsite_id] = p
            if campsite_prices:
                winning_price = campsite_prices.popitem()[1]
                for csid, p in campsite_prices.items():
                    if p.rate.adult < winning_price.rate.adult:
                        winning_price = p

                rate = RateSerializer(winning_price.rate, context={'request': request}).data

                res.append({
                    "date": single_date.strftime("%Y-%m-%d"),
                    "rate": rate,
                    "campsites": campsites
                })

    return res


def get_park_entry_rate(request, start_date):
    res = {}
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        price_history = ParkEntryRate.objects.filter(period_start__lte=start_date).order_by('-period_start')
        if price_history:
            serializer = ParkEntryRateSerializer(price_history, many=True, context={'request': request})
            res = serializer.data[0]
    return res


def booking_total_to_refund(booking):

     booking_totals = {'refund_total': Decimal('0.00')}
     campsitebooking = parkstay_models.CampsiteBooking.objects.filter(booking=booking)
     totalbooking = Decimal('0.00')

     cancellation_data = booking_cancellation_fees(booking)
     for cb in campsitebooking:
          totalbooking = totalbooking + cb.amount_adult + cb.amount_infant + cb.amount_child + cb.amount_concession

     additional_booking = parkstay_models.AdditionalBooking.objects.filter(booking=booking, identifier='vehicles')
     for ab in additional_booking:
          totalbooking = totalbooking + ab.amount
 
     # Before cancellation fees
     totalbooking_no_fees = totalbooking
     # After cancellation fees
     totalbooking = totalbooking - cancellation_data['cancellation_fee']
     booking_totals['refund_total'] = totalbooking
     booking_totals['refund_total_no_fees'] = totalbooking_no_fees
     booking_totals['campsitebooking'] = campsitebooking
     booking_totals['cancellation_data'] = cancellation_data
     return booking_totals


def booking_cancellation_fees(booking):
    cancellation_data = {'old_booking': {},'cancellation_fee': Decimal('0.00')}
    #cancellation_fee = Decimal('0.00')
    #number_of_cancellation_fees = 0
    old_arrival = booking.arrival

    campsite_booking = parkstay_models.CampsiteBooking.objects.filter(booking=booking) 

    for cb in campsite_booking:
        cb_date = cb.date.strftime('%Y-%m-%d')
        cancellation_data['old_booking'][cb_date] = {}
        cancellation_data['old_booking'][cb_date]['exists'] = False
        if cb.booking_policy:
            cancellation_data['old_booking'][cb_date]['booking_policy_id'] = cb.booking_policy.id
        else:
            cancellation_data['old_booking'][cb_date]['booking_policy_id'] = None


    for cb in campsite_booking:
        cb_date = cb.date.strftime('%Y-%m-%d')
        cancellation_data = booking_policy_cancellation_rules(cancellation_data,cb_date,cb,old_arrival,booking)
        #if cancellation_data['old_booking'][cb_date]['exists'] is False:
        #     number_of_cancellation_fees = number_of_cancellation_fees + 1

        #     pg = None
        #     if cb.booking_policy:
        #         pg = parkstay_models.BookingPolicy.objects.get(id=cb.booking_policy.id)
        #     if pg:
        #        policy_type = 'normal'
        #        if pg.peak_policy_enabled is True:
        #               pp = parkstay_models.PeakPeriod.objects.filter(peak_group=pg.peak_group, start_date__lte=cb.date, end_date__gte=cb.date, active=True)
        #               if pp.count():
        #                   policy_type='peak'

        #        if policy_type == 'peak':
        #              if pg.peak_policy_type == 0:
        #                  cancellation_fee = cancellation_fee + pg.peak_amount
        #        else:
        #              if pg.policy_type == 0:
        #                  cancellation_fee = cancellation_fee + pg.amount

    #cancellation_data['cancellation_fee'] = cancellation_fee
    return cancellation_data



def booking_change_fees(booking):
    print ("booking_change_fees")
    #parkstay_models.PeakGroup.
    cancellation_data = {'old_booking': {},'cancellation_fee': Decimal('0.00')}
    #cancellation_fee = Decimal('0.00')
    # number_of_cancellation_fees = 0

    campsite_booking = parkstay_models.CampsiteBooking.objects.filter(booking=booking)
    old_campsite_booking = parkstay_models.CampsiteBooking.objects.filter(booking_id=booking.old_booking)
    old_booking = parkstay_models.Booking.objects.get(id=booking.old_booking)
    old_arrival = old_booking.arrival

    for cb in old_campsite_booking:
        cb_date = cb.date.strftime('%Y-%m-%d')
        cancellation_data['old_booking'][cb_date] = {}
        cancellation_data['old_booking'][cb_date]['exists'] = False
        if cb.booking_policy:
            cancellation_data['old_booking'][cb_date]['booking_policy_id'] = cb.booking_policy.id
        else:
            cancellation_data['old_booking'][cb_date]['booking_policy_id'] = None
    
    for cb in campsite_booking:
        cb_date = cb.date.strftime('%Y-%m-%d')
        if cb_date in cancellation_data['old_booking']:
            cancellation_data['old_booking'][cb_date]['exists'] = True

    print ("CHANGE FEES")
    for cb in old_campsite_booking:
        cb_date = cb.date.strftime('%Y-%m-%d')
        print (cb_date)
        cancellation_data = booking_policy_cancellation_rules(cancellation_data,cb_date,cb,old_arrival, old_booking)
        #if cancellation_data['old_booking'][cb_date]['exists'] is False:
        #     number_of_cancellation_fees = number_of_cancellation_fees + 1
        #     pg = parkstay_models.BookingPolicy.objects.get(id=cb.booking_policy.id)

        #     policy_type = 'normal'
        #     if pg.peak_policy_enabled is True:
        #            pp = parkstay_models.PeakPeriod.objects.filter(peak_group=pg.peak_group, start_date__lte=cb.date, end_date__gte=cb.date, active=True)
        #            if pp.count(): 
        #                policy_type='peak'
    
        #     if policy_type == 'peak':
        #           if pg.peak_policy_type == 0:
        #               if pg.peak_arrival_limit_enabled is True:
        #                    #datetime.now().date()
        #                    peak_arrival_time_calc = old_arrival - timedelta(days=pg.peak_arrival_time)
        #                    if today_dt > peak_arrival_time_calc:
        #                           cancellation_fee = cancellation_fee + pg.peak_amount
        #                    else
        #                           pass
        #               else:
        #                    cancellation_fee = cancellation_fee + pg.peak_amount
        #     else:
        #           if pg.policy_type == 0:
        #               if pg.arrival_limit_enabled is True:
        #                   arrival_time_calc = old_arrival - timedelta(days=pg.arrival_time)
        #                   if today_dt >  arrival_time_calc :
        #                       cancellation_fee = cancellation_fee + pg.amount
        #                   else:
        #                       pass
        #               else:
        #                    cancellation_fee = cancellation_fee + pg.amount

    #invoice_lines.append({
    #     'ledger_description': 'Cancellation Fee',
    #     "quantity": 1,
    #     "price_incl_tax": str(cancellation_fee),
    #     "oracle_code": booking.campsite_oracle_code,
    #     "line_status" : 1 
    #     })
    #cancellation_data['cancellation_fee'] = cancellation_fee
    return cancellation_data 

def booking_policy_cancellation_rules(cancellation_data,cb_date,cb, old_arrival, old_booking):
    today_dt = datetime.now().date()
    today_datetime = datetime.now(timezone_dt.utc) 
    total_seconds = (today_datetime - old_booking.created).total_seconds()
    booking_grace_time = total_seconds/60

    cancellation_fee = Decimal('0.00')
    grace_period = 0
    if 'cancellation_fee' in cancellation_data:
        cancellation_fee = cancellation_data['cancellation_fee']

    number_of_cancellation_fees = 0
    if cancellation_data['old_booking'][cb_date]['exists'] is False:
         number_of_cancellation_fees = number_of_cancellation_fees + 1
         pg = parkstay_models.BookingPolicy.objects.get(id=cb.booking_policy.id)
         policy_type = 'normal'
         if pg.peak_policy_enabled is True:
                pp = parkstay_models.PeakPeriod.objects.filter(peak_group=pg.peak_group, start_date__lte=cb.date, end_date__gte=cb.date, active=True)
                if pp.count():
                    policy_type='peak'
         
         if policy_type == 'peak':
               grace_period = pg.peak_grace_time
               if booking_grace_time > pg.peak_grace_time:
                   if pg.peak_policy_type == 0:
                       if pg.peak_arrival_limit_enabled is True:
                            #datetime.now().date()
                            peak_arrival_time_calc = cb.date - timedelta(days=pg.peak_arrival_time)
                            if today_dt >= peak_arrival_time_calc:
                                   cancellation_fee = cancellation_fee + pg.peak_amount
                            else:
                                   pass
                       else:
                            cancellation_fee = cancellation_fee + pg.peak_amount
         else:
               grace_period = pg.peak_grace_time
               if booking_grace_time > pg.grace_time:
                   if pg.policy_type == 0:
                       
                       if pg.arrival_limit_enabled is True:
                           arrival_time_calc = cb.date - timedelta(days=pg.arrival_time)
                           if today_dt >= arrival_time_calc:
                               cancellation_fee = cancellation_fee + pg.amount
                           else:
                               pass
                       else:
                            cancellation_fee = cancellation_fee + pg.amount
    cancellation_data['grace_period'] = grace_period
    cancellation_data['cancellation_fee'] = cancellation_fee
    return cancellation_data


def price_or_lineitemsv2old_booking(request, booking, invoice_lines):
    # reverse booking charges from old booking
    total_price = Decimal(0)
    old_booking = None
    line_status = 3
    campsite_booking = parkstay_models.CampsiteBooking.objects.filter(booking=booking)
    num_days = int((booking.departure - booking.arrival).days)

    total_amount_adult = Decimal('0.00')
    total_amount_child = Decimal('0.00')
    total_amount_infant = Decimal('0.00')
    total_amount_concession = Decimal('0.00')

    for cb in campsite_booking:
        total_amount_adult = total_amount_adult + cb.amount_adult
        total_amount_child = total_amount_child + cb.amount_child
        total_amount_infant = total_amount_infant + cb.amount_infant
        total_amount_concession = total_amount_concession + cb.amount_concession


    if booking.details['num_adult'] > 0:
       invoice_lines.append({
            'ledger_description': 'Adjustment - Camping fee ({}) {} - {} night(s)'.format(booking.details['num_adult'],'adult', num_days),
            "quantity": 1, #booking.details['num_adult'],
            "price_incl_tax": str(total_amount_adult - total_amount_adult - total_amount_adult),
            "price_excl_tax": str(calculate_excl_gst(total_amount_adult - total_amount_adult - total_amount_adult)), 
            "oracle_code": booking.campsite_oracle_code,
            "line_status" : line_status
            })

    if booking.details['num_child'] > 0:
       invoice_lines.append({
            'ledger_description': 'Adjustment - Camping fee ({}) {} - {} night(s)'.format(booking.details['num_child'],'child', num_days),
            "quantity": 1, #booking.details['num_child'],
            "price_incl_tax": str(total_amount_child - total_amount_child- total_amount_child),
            "price_excl_tax": str(calculate_excl_gst(total_amount_child - total_amount_child- total_amount_child)),
            "oracle_code": booking.campsite_oracle_code,
            "line_status" : line_status
            })


    if booking.details['num_infant'] > 0:
       invoice_lines.append({
            'ledger_description': 'Adjustment - Camping fee ({}) {} - {} night(s)'.format(booking.details['num_infant'], 'infant', num_days),
            "quantity": 1, #booking.details['num_infant'],
            "price_incl_tax": str(total_amount_infant - total_amount_infant - total_amount_infant),
            "price_excl_tax": str(calculate_excl_gst(total_amount_infant - total_amount_infant - total_amount_infant)),
            "oracle_code": booking.campsite_oracle_code,
            "line_status" : line_status
            })


    if booking.details['num_concession'] > 0:
       invoice_lines.append({
            'ledger_description': 'Adjustment - Camping fee ({}) {} - {} night(s)'.format(booking.details['num_concession'],'concession', num_days),
            "quantity": 1, #booking.details['num_concession'],
            "price_incl_tax": str(total_amount_concession - total_amount_concession - total_amount_concession),
            "price_excl_tax": str(calculate_excl_gst(total_amount_concession - total_amount_concession - total_amount_concession)),
            "oracle_code": booking.campsite_oracle_code,
            "line_status" : line_status
            })

    additional_booking = parkstay_models.AdditionalBooking.objects.filter(booking=booking, identifier='vehicles')
    for ab in additional_booking:

        if ab.gst:
            invoice_lines.append({
                'ledger_description': "Adjustment - "+ab.fee_description,
                "quantity": 1,
                "price_incl_tax": str(ab.amount - ab.amount - ab.amount),
                "price_excl_tax": str(calculate_excl_gst(ab.amount - ab.amount - ab.amount)),
                "oracle_code": ab.oracle_code,
                "line_status" : line_status
                })
        else:
            invoice_lines.append({
                'ledger_description': "Adjustment - "+ab.fee_description,
                "quantity": 1,
                "price_incl_tax": str(ab.amount - ab.amount - ab.amount),
                "price_excl_tax": str(ab.amount - ab.amount - ab.amount ),
                "oracle_code": ab.oracle_code,
                "line_status" : line_status
                })

    return invoice_lines


def price_or_lineitemsv2(request, booking):
    total_price = Decimal(0)
    invoice_lines = []
    old_booking = None
    # changed line items
    if booking.old_booking:
        old_booking = parkstay_models.Booking.objects.get(id=int(booking.old_booking))
        invoice_lines = price_or_lineitemsv2old_booking(request,old_booking, invoice_lines)
        #invoice_lines = booking_cancellation_fees(request,booking, invoice_lines)
    # new line items 
    line_status = 1
    campsite_booking = parkstay_models.CampsiteBooking.objects.filter(booking=booking)
    num_days = int((booking.departure - booking.arrival).days) 
    
    total_amount_adult = Decimal('0.00')
    total_amount_child = Decimal('0.00')
    total_amount_infant = Decimal('0.00') 
    total_amount_concession = Decimal('0.00')

    for cb in campsite_booking:
        total_amount_adult = total_amount_adult + cb.amount_adult
        total_amount_child = total_amount_child + cb.amount_child
        total_amount_infant = total_amount_infant + cb.amount_infant
        total_amount_concession = total_amount_concession + cb.amount_concession

        
    if booking.details['num_adult'] > 0:
       invoice_lines.append({
            'ledger_description': 'Camping fee ({}) {} - {} night(s)'.format(booking.details['num_adult'], 'adult', num_days),
            "quantity": 1, #booking.details['num_adult'],
            "price_incl_tax": str(total_amount_adult),
            "price_excl_tax": str(calculate_excl_gst(total_amount_adult)),
            "oracle_code": booking.campsite_oracle_code,
            "line_status" : line_status

            })

    if booking.details['num_child'] > 0:
       invoice_lines.append({
            'ledger_description': 'Camping fee ({}) {} - {} night(s)'.format(booking.details['num_child'],'child', num_days),
            "quantity": 1, #booking.details['num_child'],
            "price_incl_tax": str(total_amount_child),
            "price_excl_tax": str(calculate_excl_gst(total_amount_child)),
            "oracle_code": booking.campsite_oracle_code,
            "line_status" : line_status
            })


    if booking.details['num_infant'] > 0:
       invoice_lines.append({
            'ledger_description': 'Camping fee ({}) {} - {} night(s)'.format(booking.details['num_infant'],'infant', num_days),
            "quantity": 1, #booking.details['num_infant'],
            "price_incl_tax": str(total_amount_infant),
            "price_excl_tax": str(calculate_excl_gst(total_amount_infant)),
            "oracle_code": booking.campsite_oracle_code,
            "line_status" : line_status
            })


    if booking.details['num_concession'] > 0:
       invoice_lines.append({
            'ledger_description': 'Camping fee ({}) {} - {} night(s)'.format(booking.details['num_concession'],'concession', num_days),
            "quantity": 1, #booking.details['num_concession'],
            "price_incl_tax": str(total_amount_concession),
            "price_excl_tax": str(calculate_excl_gst(total_amount_concession)),
            "oracle_code": booking.campsite_oracle_code,
            "line_status" : line_status
            })

    additional_booking = parkstay_models.AdditionalBooking.objects.filter(booking=booking)
    for ab in additional_booking:
        
        
        if ab.gst is False:
            invoice_lines.append({
                'ledger_description': ab.fee_description,
                "quantity": 1,
                "price_incl_tax": str(ab.amount),
                "price_excl_tax": str(ab.amount),
                "oracle_code": ab.oracle_code,
                "line_status" : line_status
            })
        else:             
            invoice_lines.append({
                'ledger_description': ab.fee_description,
                "quantity": 1,
                "price_incl_tax": str(ab.amount),
                "price_excl_tax": str(calculate_excl_gst(ab.amount)),
                "oracle_code": ab.oracle_code,
                "line_status" : line_status
                })

    return invoice_lines

    



def price_or_lineitems(request, booking, campsite_list, lines=True, old_booking=None):
    total_price = Decimal(0)
    rate_list = {}
    invoice_lines = []
    if not lines and not old_booking:
        raise Exception('An old booking is required if lines is set to false')

    # Create line items for customers
    daily_rates = [get_campsite_current_rate(request, c, booking.arrival.strftime('%Y-%m-%d'), booking.departure.strftime('%Y-%m-%d')) for c in campsite_list]
    if not daily_rates:
        raise Exception('There was an error while trying to get the daily rates.')
    for rates in daily_rates:
        for c in rates:
            # This line is used to initialize th rate_list, it updates the blank rate_list with the initially found values (triggered only once)
            if c['rate']['campsite'] not in rate_list.keys():
                rate_list[c['rate']['campsite']] = {c['rate']['id']: {'start': c['date'], 'end': c['date'], 'adult': c['rate']['adult'], 'concession': c['rate']['concession'], 'child': c['rate']['child'], 'infant': c['rate']['infant'], 'booking_policy_id': c['booking_policy']}}
            else:
                # This line is triggered when there are multiple rates,it updates rates_list with the other rate (i.e updates the others rates found into rate_list)
                if c['rate']['id'] not in rate_list[c['rate']['campsite']].keys():
                    rate_list[c['rate']['campsite']][c['rate']['id']] = {'start':c['date'],'end':c['date'],'adult':c['rate']['adult'],'concession':c['rate']['concession'],'child':c['rate']['child'],'infant':c['rate']['infant'], 'booking_policy_id': c['booking_policy']}
                else:
                    # This line is triggered when the rate for a particular date does not change compared to the previous day,only end date is updated in rate_list
                    rate_list[c['rate']['campsite']][c['rate']['id']]['end'] = c['date']

    if len(campsite_list) > 1:  # check if this is a multibook
        # Get the cheapest campsite (based on adult rate) to be used
        # for the whole booking period, using the first rate as default
        # Set initial campsite and rate to first in rate_list
        first_ratelist_item = rate_list[next(iter(rate_list))]
        multibook_rate = next(iter(first_ratelist_item.values()))
        multibook_rate_adult = Decimal(multibook_rate['adult'])
        multibook_campsite = next(iter(rate_list))
        multibook_index = 1
        for campsite, ratelist in rate_list.items():
            for index, rate in ratelist.items():
                if Decimal(rate['adult']) < multibook_rate_adult:
                    multibook_rate = rate
                    multibook_rate_adult = Decimal(multibook_rate['adult'])
                    multibook_campsite = campsite
                    multibook_index = index
        rate_list = {multibook_campsite: {multibook_index: multibook_rate}}

    # Get Guest Details
    guests = {}
    guests_json_keys  = ['num_adult','num_child','num_infant','num_concession']
    for k, v in booking.details.items():
        if k in guests_json_keys:
            guests[k.split('num_')[1]] = v
            
    for guest_type, guest_count in guests.items():
        if int(guest_count) > 0:
            for campsite_id, price_periods in rate_list.items():
                for index, rate in price_periods.items():
                    # for each price period, add the cost per night
                    price = Decimal(0)
                    end = datetime.strptime(rate['end'], "%Y-%m-%d").date()
                    start = datetime.strptime(rate['start'], "%Y-%m-%d").date()
                    num_days = int((end - start).days) + 1
                    campsite = Campsite.objects.get(id=campsite_id)
                    if lines:
                        price = str((num_days * Decimal(rate[guest_type])))
                        if not booking.campground.oracle_code:
                            raise Exception('The campground selected does not have an Oracle code attached to it.')
                        end_date = end + timedelta(days=1)
                        invoice_lines.append({
                            'ledger_description': 'Camping fee {} - {} night(s)'.format(guest_type, num_days),
                            "quantity": guest_count,
                            "price_incl_tax": price,
                            "price_excl_tax": str(calculate_excl_gst(Decimal(price))),
                            "oracle_code": booking.campground.oracle_code})
                    else:
                        price = (num_days * Decimal(rate[guest_type])) * guest_count
                        total_price += price
    # Create line items for vehicles
    if lines:
        vehicles = booking.regos.all()
    else:
        vehicles = old_booking.regos.all()
    if vehicles:
        if booking.campground.park.entry_fee_required:
            # Update the booking vehicle regos with the park entry requirement
            vehicles.update(park_entry_fee=True)
            if not booking.campground.park.oracle_code:
                raise Exception('A park entry Oracle code has not been set for the park that the campground belongs to.')
        park_entry_rate = get_park_entry_rate(request, booking.arrival.strftime('%Y-%m-%d'))
        vehicle_dict = {
            'vehicle': vehicles.filter(entry_fee=True, type='vehicle'),
            'motorbike': vehicles.filter(entry_fee=True, type='motorbike'),
            'concession': vehicles.filter(entry_fee=True, type='concession')
        }

        for k, v in vehicle_dict.items():
            if v.count() > 0:
                if lines:
                    price = park_entry_rate[k]
                    regos = ', '.join([x[0] for x in v.values_list('rego')])
                    invoice_lines.append({
                        'ledger_description': 'Park entry fee - {}'.format(k),
                        'quantity': v.count(),
                        'price_incl_tax': price,
                        'price_excl_tax': str(calculate_excl_gst(Decimal(price))),
                        'oracle_code': booking.campground.park.oracle_code
                    })
                else:
                    price = Decimal(park_entry_rate[k]) * v.count()
                    total_price += price

    # Create line item for Override price
    if booking.override_price is not None:
        if booking.override_reason is not None:
            reason = booking.override_reason
            invoice_lines.append({
                'ledger_description': '{} - {}'.format(reason.text, booking.override_reason_info),
                'quantity': 1,
                'price_incl_tax': str(total_price - booking.discount),
                'price_excl_tax' : str(calculate_excl_gst(total_price - booking.discount)),
                'oracle_code': booking.campground.oracle_code
            })

    if lines:
        return invoice_lines
    else:
        return total_price


def check_date_diff(old_booking, new_booking):
    if old_booking.arrival == new_booking.arrival and old_booking.departure == new_booking.departure:
        return 4  # same days
    elif old_booking.arrival == new_booking.arrival:
        old_booking_days = int((old_booking.departure - old_booking.arrival).days)
        new_days = int((new_booking.departure - new_booking.arrival).days)
        if new_days > old_booking_days:
            return 1  # additional days
        else:
            return 2  # reduced days
    elif old_booking.departure == new_booking.departure:
        old_booking_days = int((old_booking.departure - old_booking.arrival).days)
        new_days = int((new_booking.departure - new_booking.arrival).days)
        if new_days > old_booking_days:
            return 1  # additional days
        else:
            return 2  # reduced days
    else:
        return 3  # different days


def get_diff_days(old_booking, new_booking, additional=True):
    if additional:
        return int((new_booking.departure - old_booking.departure).days)
    return int((old_booking.departure - new_booking.departure).days)


def create_temp_bookingupdate(request, arrival, departure, booking_details, old_booking, total_price):
    # delete all the campsites in the old moving so as to transfer them to the new booking
    old_booking.campsites.all().delete()

    booking = create_booking_by_site(request, 
                                     booking_details['campsites'],
                                     start_date=arrival,
                                     end_date=departure,
                                     num_adult=booking_details['num_adult'],
                                     num_concession=booking_details['num_concession'],
                                     num_child=booking_details['num_child'],
                                     num_infant=booking_details['num_infant'],
                                     num_vehicle=booking_details['num_vehicle'],
                                     num_campervan=booking_details['num_campervan'],
                                     num_motorcycle=booking_details['num_motorcycle'],
                                     num_trailer=booking_details['num_trailer'],
                                     cost_total=total_price,
                                     customer=old_booking.customer,
                                     override_price=old_booking.override_price,
                                     overridden_by=request.user,
                                     updating_booking=True,
                                     override_checks=True,
                                     old_booking=old_booking
                                     )
    # Move all the vehicles to the new booking
    for r in old_booking.regos.all():
        r.booking = booking
        r.save()

    lines = price_or_lineitems(request, booking, booking.campsite_id_list)
    booking_arrival = booking.arrival.strftime('%d-%m-%Y')
    booking_departure = booking.departure.strftime('%d-%m-%Y')
    reservation = u'Reservation for {} confirmation PS{}'.format(
        u'{} {}'.format(booking.customer.first_name, booking.customer.last_name), old_booking.id)
    # Proceed to generate invoice

    checkout_response = checkout(request, booking, lines, invoice_text=reservation, internal=True)

    # FIXME: replace with session check
    invoice = None
    if 'invoice=' in checkout_response.url:
        invoice = checkout_response.url.split('invoice=', 1)[1]
    else:
        for h in reversed(checkout_response.history):
            if 'invoice=' in h.url:
                invoice = h.url.split('invoice=', 1)[1]
                break

    # create the new invoice
    new_invoice = internal_create_booking_invoice(booking, invoice)

    # Check if the booking is a legacy booking and doesn't have an invoice
    if old_booking.legacy_id and old_booking.invoices.count() < 1:
        # Create a cash transaction in order to fix the outstnding invoice payment
        ## JASON CASH
        #CashTransaction.objects.create(
        #    invoice=Invoice.objects.get(reference=new_invoice.invoice_reference),
        #    amount=old_booking.cost_total,
        #    type='move_in',
        #    source='cash',
        #    details='Transfer of funds from migrated booking',
        #    movement_reference='Migrated Booking Funds'
        #)
        # Update payment details for the new invoice
        update_payments(new_invoice.invoice_reference)

    # Attach new invoices to old booking
    for i in old_booking.invoices.all():
        inv = Invoice.objects.get(reference=i.invoice_reference)
        inv.voided = True
        # transfer to the new invoice
        inv.move_funds(inv.transferable_amount, Invoice.objects.get(reference=new_invoice.invoice_reference), 'Transfer of funds from {}'.format(inv.reference))
        inv.save()
    # Change the booking for the selected invoice
    new_invoice.booking = old_booking
    new_invoice.save()

    return booking


def update_booking(request, old_booking, booking_details):
    same_dates = False
    same_campsites = False
    same_campground = False
    same_details = False
    same_vehicles = True

    with transaction.atomic():
        try:
            set_session_booking(request.session, old_booking)
            new_details = {}
            new_details.update(old_booking.details)
            # Update the guests
            new_details['num_adult'] = booking_details['num_adult']
            new_details['num_concession'] = booking_details['num_concession']
            new_details['num_child'] = booking_details['num_child']
            new_details['num_infant'] = booking_details['num_infant']
            booking = Booking(
                arrival=booking_details['start_date'],
                departure=booking_details['end_date'],
                details=new_details,
                customer=old_booking.customer,
                campground=Campground.objects.get(id=booking_details['campground']))
            # Check that the departure is not less than the arrival
            if booking.departure < booking.arrival:
                raise Exception('The departure date cannot be before the arrival date')
            today = datetime.now().date()
            if today > old_booking.departure:
                raise ValidationError('You cannot change a booking past the departure date.')

            # Check if it is the same campground
            if old_booking.campground.id == booking.campground.id:
                same_campground = True
            # Check if dates are the same
            if (old_booking.arrival == booking.arrival) and (old_booking.departure == booking.departure):
                same_dates = True
            # Check if the campsite is the same
            if sorted(old_booking.campsite_id_list) == sorted(booking_details['campsites']):
                same_campsites = True
            # Check if the details have changed
            if new_details == old_booking.details:
                same_details = True
            # Check if the vehicles have changed
            current_regos = old_booking.regos.all()
            current_vehicle_regos = sorted([r.rego for r in current_regos])

            # Add history
            new_history = old_booking._generate_history(user=request.user)

            if 'regos' in booking_details:
                new_regos = booking_details['regos']
                sent_regos = [r['rego'] for r in new_regos]
                regos_serializers = []
                update_regos_serializers = []

                for n in new_regos:
                    if n['rego'] not in current_vehicle_regos:
                        n['booking'] = old_booking.id
                        regos_serializers.append(BookingRegoSerializer(data=n))
                        same_vehicles = False
                    else:
                        booking_rego = BookingVehicleRego.objects.get(booking=old_booking, rego=n['rego'])
                        n['booking'] = old_booking.id
                        if booking_rego.type != n['type'] or booking_rego.entry_fee != n['entry_fee']:
                            update_regos_serializers.append(BookingRegoSerializer(booking_rego, data=n))
                # Create the new regos if they are there
                if regos_serializers:
                    for r in regos_serializers:
                        r.is_valid(raise_exception=True)
                        r.save()
                # Update the new regos if they are there
                if update_regos_serializers:
                    for r in update_regos_serializers:
                        r.is_valid(raise_exception=True)
                        r.save()
                    same_vehicles = False

                # Check if there are regos in place that need to be removed
                stale_regos = []
                for r in current_regos:
                    if r.rego not in sent_regos:
                        stale_regos.append(r.id)
                # delete stale regos
                if stale_regos:
                    same_vehicles = False
                    BookingVehicleRego.objects.filter(id__in=stale_regos).delete()
            else:
                same_vehicles = False
                if current_regos:
                    current_regos.delete()

            if same_campsites and same_dates and same_vehicles and same_details:
                # new_history.delete()
                # return old_booking

                if new_history:
                    new_history.delete()
                    return old_booking
                else:
                    return old_booking

            # Check difference of dates in booking
            old_booking_days = int((old_booking.departure - old_booking.arrival).days)
            new_days = int((booking_details['end_date'] - booking_details['start_date']).days)
            date_diff = check_date_diff(old_booking, booking)

            total_price = price_or_lineitems(request, booking, booking_details['campsites'], lines=False, old_booking=old_booking)
            price_diff = True
            if old_booking.cost_total != total_price:
                price_diff = True
            if price_diff:
                #old_booking.is_canceled = True
                #old_booking.save()
                
                booking = create_temp_bookingupdate(request, booking.arrival, booking.departure, booking_details, old_booking, total_price)
                # Attach campsite booking objects to old booking
                for c in booking.campsites.all():
                    c.booking = old_booking
                    c.save()
                # Move all the vehicles to the in new booking to the old booking
                for r in booking.regos.all():
                    r.booking = old_booking
                    r.save()
                old_booking.cost_total = booking.cost_total
                old_booking.departure = booking.departure
                old_booking.arrival = booking.arrival
                old_booking.details.update(booking.details)
                if not same_campground:
                    old_booking.campground = booking.campground
                old_booking.save()
                booking.delete()
            delete_session_booking(request.session)
            send_booking_invoice(old_booking)
            old_booking.confirmation_sent = False
            old_booking.save()

            # send out the confirmation email if the booking is paid or over paid
            #if old_booking.status == 'Paid' or old_booking.status == 'Over Paid':
                #send_booking_confirmation(old_booking, request)
                #send_booking_confirmation(old_booking)
            return old_booking
        except BaseException:
            delete_session_booking(request.session)
            print(traceback.print_exc())
            raise


def create_or_update_booking(request, booking_details, updating=False, override_checks=False):
    booking = None
    if not updating:
        booking = create_booking_by_site(request,
                                         booking_details['campsites'],
                                         start_date=booking_details['start_date'],
                                         end_date=booking_details['end_date'],
                                         num_adult=booking_details['num_adult'],
                                         num_concession=booking_details['num_concession'],
                                         num_child=booking_details['num_child'],
                                         num_infant=booking_details['num_infant'],
                                         num_vehicle=booking_details['num_vehicle'],
                                         num_campervan=booking_details['num_campervan'],
                                         num_motorcycle=booking_details['num_motorcycle'],
                                         num_trailer=booking_details['num_trailer'],
                                         cost_total=booking_details['cost_total'],
                                         override_price=booking_details['override_price'],
                                         override_reason=booking_details['override_reason'],
                                         override_reason_info=booking_details['override_reason_info'],
                                         send_invoice=booking_details['send_invoice'],
                                         overridden_by=booking_details['overridden_by'],
                                         customer=booking_details['customer'],
                                         override_checks=override_checks,
                                         do_not_send_invoice=booking_details['do_not_send_invoice'],
                                         )

        booking.details['first_name'] = booking_details['first_name']
        booking.details['last_name'] = booking_details['last_name']
        booking.details['phone'] = booking_details['phone']
        booking.details['country'] = booking_details['country']
        booking.details['postcode'] = booking_details['postcode']

        # Add booking regos
        if 'regos' in booking_details:
            regos = booking_details['regos']
            for r in regos:
                r['booking'] = booking.id
            regos_serializers = [BookingRegoSerializer(data=r) for r in regos]
            for r in regos_serializers:
                r.is_valid(raise_exception=True)
                r.save()
        booking.save()
    return booking

def clean_none_to_empty(value):
     if value is None:
         return ''
     return value

def checkout(request, booking, lines, invoice_text=None, vouchers=[], internal=False):
    old_booking = '' 
    if booking.old_booking:
        old_booking = 'PB-'+str(booking.old_booking)

    no_payment = False
    if request.user.is_authenticated:
        if request.user.is_staff is True:
            if parkstay_models.ParkstayPermission.objects.filter(email=request.user.email,permission_group=4).count() > 0:
                    np_post =  request.POST.get('no_payment','false')
                    if np_post == 'true':
                         no_payment = True

    basket_params = {
        'products': lines,
        'vouchers': vouchers,
        'system': settings.PS_PAYMENT_SYSTEM_ID,
        'custom_basket': True,
        'booking_reference': 'PB-'+str(booking.id),
        'booking_reference_link': old_booking,
        'no_payment': no_payment,
        'tax_override': True
    }
    basket_user_id = booking.customer.id

    basket_hash = create_basket_session(request,basket_user_id, basket_params)
    
    checkouthash = request.session.get('checkouthash','')
        
    checkout_params = {
        'system': settings.PS_PAYMENT_SYSTEM_ID,
        'fallback_url': request.build_absolute_uri('/'),
        'return_url': request.build_absolute_uri(reverse('public_booking_success'))+'?checkouthash='+checkouthash,
        'return_preload_url': settings.PARKSTAY_EXTERNAL_URL+'/api/complete_booking/'+booking.booking_hash+'/'+str(booking.id)+'/',
        #'return_preload_url': request.build_absolute_uri(reverse('public_booking_success')),
        'force_redirect': True,
        'proxy': True if internal else False,
        'invoice_text': invoice_text,
        # 'invoice_name' : "SYSTEM TEST CUSTOM NAME",
        'session_type' : 'ledger_api',
        'basket_owner' : booking.customer.id 
        #'amount_override': float('1.00')
    }

    #if not internal:
    #    checkout_params['check_url'] = request.build_absolute_uri('/api/booking/{}/booking_checkout_status.json'.format(booking.id))
    if internal or request.user.is_anonymous:
        checkout_params['basket_owner'] = booking.customer.id

    #create_checkout_session(request, checkout_params)
    create_checkout_session(request,checkout_params)

    if internal:
        response = place_order_submission(request)
    else:
        response = HttpResponse("<script> window.location='"+reverse('ledgergw-payment-details')+"';</script> <a href='"+reverse('ledgergw-payment-details')+"'> Redirecting please wait: "+reverse('ledgergw-payment-details')+"</a>")

    return response


def internal_create_booking_invoice(booking, reference):
    try:
        Invoice.objects.get(reference=reference)
    except Invoice.DoesNotExist:
        raise Exception("There was a problem attaching an invoice for this booking")
    book_inv = BookingInvoice.objects.create(booking=booking, invoice_reference=reference)
    return book_inv


def internal_booking(request, booking_details, internal=True, updating=False):
    json_booking = request.data
    booking = None
    try:
        booking = create_or_update_booking(request, booking_details, updating, override_checks=internal)
        with transaction.atomic():
            set_session_booking(request.session, booking)
            # Get line items
            booking_arrival = booking.arrival.strftime('%d-%m-%Y')
            booking_departure = booking.departure.strftime('%d-%m-%Y')
            reservation = u"Reservation for {} confirmation PS{}".format(u'{} {}'.format(booking.customer.first_name, booking.customer.last_name), booking.id)
            lines = price_or_lineitems(request, booking, booking.campsite_id_list)

            # Proceed to generate invoice
            checkout_response = checkout(request, booking, lines, invoice_text=reservation, internal=True)
            # Change the type of booking
            booking.booking_type = 0
            booking.save()

            # FIXME: replace with session check
            invoice = None
            if 'invoice=' in checkout_response.url:
                invoice = checkout_response.url.split('invoice=', 1)[1]
            else:
                for h in reversed(checkout_response.history):
                    if 'invoice=' in h.url:
                        invoice = h.url.split('invoice=', 1)[1]
                        break

            internal_create_booking_invoice(booking, invoice)
            delete_session_booking(request.session)
            if booking.send_invoice:
                send_booking_invoice(booking)
            return booking

    except BaseException:
        if booking:
            booking.delete()
        raise


def set_session_booking(session, booking):
    session['ps_booking'] = booking.id
    session.modified = True


def get_session_booking(session):
    if 'ps_booking' in session:
        booking_id = session['ps_booking']
    else:
        raise Exception('Booking not in Session')

    try:
        return Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        raise Exception('Booking not found for booking_id {}'.format(booking_id))


def delete_session_booking(session):
    if 'ps_booking' in session:
        del session['ps_booking']
        session.modified = True


def bind_booking(booking, basket):
    if booking.booking_type == 3:
        logger.info(u'bind_booking start {}'.format(booking.id))
        order = Order.objects.get(basket_id=basket[0].id)
        invoice = Invoice.objects.get(order_number=order.number)
        invoice_ref = invoice.reference
        book_inv, created = BookingInvoice.objects.get_or_create(booking=booking, invoice_reference=invoice_ref)
        logger.info(u'{} finished temporary booking {}, creating new BookingInvoice with reference {}'.format(u'User {} with id {}'.format(booking.customer.get_full_name(), booking.customer.id) if booking.customer else u'An anonymous user', booking.id, invoice_ref))
        try:
            inv = Invoice.objects.get(reference=invoice_ref)
        except Invoice.DoesNotExist:
            logger.error(u'{} tried making a booking with an incorrect invoice'.format(u'User {} with id {}'.format(booking.customer.get_full_name(), booking.customer.id) if booking.customer else u'An anonymous user'))
            raise BindBookingException

        if inv.system not in [settings.PS_PAYMENT_SYSTEM_ID.replace("S","0")]:
            logger.error(u'{} tried making a booking with an invoice from another system with reference number {}'.format(u'User {} with id {}'.format(booking.customer.get_full_name(), booking.customer.id) if booking.customer else u'An anonymous user', inv.reference))
            raise BindBookingException
        #try:
        #    b = BookingInvoice.objects.get(invoice_reference=invoice_ref)
        #    logger.error(u'{} tried making a booking with an already used invoice with reference number {}'.format(u'User {} with id {}'.format(booking.customer.get_full_name(), booking.customer.id) if booking.customer else u'An anonymous user', inv.reference))
        #    raise BindBookingException
        #except BookingInvoice.DoesNotExist:
        #    logger.info(u'{} finished temporary booking {}, creating new BookingInvoice with reference {}'.format(u'User {} with id {}'.format(booking.customer.get_full_name(), booking.customer.id) if booking.customer else u'An anonymous user', booking.id, invoice_ref))
            # FIXME: replace with server side notify_url callback
            #book_inv, created = BookingInvoice.objects.get_or_create(booking=booking, invoice_reference=invoice_ref)
            # set booking to be permanent fixture
        
        logger.info(u'preparing to complete booking {}'.format(booking.id))
        booking.booking_type = 1  # internet booking
        booking.expiry_time = None
        booking.save()
        parkstay_models.BookingLog.objects.create(booking=booking,message="Booking Completed")
        if booking.old_booking:
            if booking.old_booking > 0:
                logger.info(u'cancelling old booking started {}'.format(booking.old_booking))
                old_booking = Booking.objects.get(id=int(booking.old_booking))
                old_booking.is_canceled = True
                if booking.created_by is not None:
                     logger.info(u'created by {}'.format(booking.created_by))
                     old_booking.canceled_by = EmailUser.objects.get(id=int(booking.created_by))
                old_booking.cancelation_time = timezone.now()
                old_booking.cancellation_reason = "Booking Changed Online"
                old_booking.save()
                logger.info(u'cancelling old booking completed {}'.format(booking.old_booking))

                # start - send signal to availability cache to rebuild
                cb = parkstay_models.CampsiteBooking.objects.filter(booking=old_booking)
                for c in cb:
                    try:
                        ac = parkstay_models.AvailabilityCache.objects.filter(date=c.date, campground=c.campsite.campground)
                        if ac.count() > 0:
                            for a in ac:
                                a.stale=True
                                a.save()
                        else:
                            parkstay_models.AvailabilityCache.objects.create(date=c.date,campground=c.campsite.campground,stale=True)
                    except Exception as e:
                        print (e)
                        logger.info(u'error updating availablity cache {}'.format(old_booking.id))
                        print ("Error Updating campsite availablity for campsitebooking.id "+str(c.id))
                logger.info(u'availablity cache flagged for update {}'.format(old_booking.id))
                # end - send signal to availability cache to rebuild




        logger.info(u'booking completed {}'.format(booking.id))

        cb = parkstay_models.CampsiteBooking.objects.filter(booking=booking)
        for c in cb:
            try:
                ac = parkstay_models.AvailabilityCache.objects.filter(date=c.date, campground=c.campsite.campground)
                if ac.count() > 0:

                    for a in ac:
                       a.stale=True
                       a.save()
                else:
                    parkstay_models.AvailabilityCache.objects.create(date=c.date,campground=c.campsite.campground,stale=True)
            except Exception as e:
                print (e)
                logger.info(u'error updating availablity cache {}'.format(booking.id))
                print ("Error Updating campsite availablity for campsitebooking.id "+str(c.id))
        logger.info(u'availablity cache flagged for update {}'.format(booking.id))




            #delete_session_booking(request.session)
            #request.session['ps_last_booking'] = booking.id

            # send out the invoice before the confirmation is sent
            #send_booking_invoice(booking)
            # for fully paid bookings, fire off confirmation email
            #if booking.paid:
            # because it slow the success page 
            #t = threading.Thread(target=send_booking_confirmation_email,args=[booking.id,],daemon=False)
            #t.start()
            #send_booking_confirmation(booking, request)

def send_booking_confirmation_email(booking_id):
    booking = Booking.objects.get(id=int(booking_id))
    if booking.paid:
        send_booking_confirmation(booking_id)
 



def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def oracle_integration(date, override):
    system = settings.PS_PAYMENT_SYSTEM_ID.replace("S","0") 
    oracle_codes = oracle_parser(date, system, 'Parkstay', override)

def get_ledger_totals():
    ledger_totals = {"total_failed": 0}
    try: 
       data_file = settings.BASE_DIR+"/datasets/ledger-totals.json"
       f = open(settings.BASE_DIR+"/datasets/ledger-totals.json", "r")
       dumped_data = f.read()
       f.close()
       ledger_import_totals = json.loads(dumped_data)
       ledger_totals["total_failed"] = ledger_import_totals['refund_total']
    except:
       print ("error opening ledger totals")

    return ledger_totals

    #f = open(data_file, "w")
    #f.write(json.dumps(ledger_totals, indent=4))
    #f.close()


def get_release_date_for_campground(campground_id):
    from parkstay import utils_cache
    release_date = None
    today = date.today()
    release_date_obj = utils_cache.get_campground_release_date()
    release_period = {"release_date": None,"booking_open_date": None}
        
    campground = Campground.objects.get(id=campground_id)    
    nowtime = datetime.now()        
    release_time = campground.release_time.strftime("%H:%M:%S")

    # Check if campground has specific open periods
    for rd in release_date_obj['release_period']:
        if rd['campground']:
            if int(rd['campground']) == int(campground_id):
                rd_release_date = datetime.strptime(rd['release_date'], "%Y-%m-%d").date()
                rd_booking_open_date= datetime.strptime(rd['booking_open_date'], "%Y-%m-%d").date()
                if today >= rd_booking_open_date:
                    campground_opentime = datetime.strptime(rd['booking_open_date']+' '+release_time, '%Y-%m-%d %H:%M:%S')                
                    if nowtime >= campground_opentime:
                        release_period["release_date"] = rd_release_date
                        release_period["booking_open_date"] = rd_booking_open_date

    if release_period["release_date"] is None:
        for rd in release_date_obj['release_period']:
            if rd['campground'] == None:
                rd_release_date = datetime.strptime(rd['release_date'], "%Y-%m-%d").date()
                rd_booking_open_date = datetime.strptime(rd['booking_open_date'], "%Y-%m-%d").date()

                if today > rd_booking_open_date: 
                    release_period["release_date"] = rd_release_date
                    release_period["booking_open_date"] = rd_booking_open_date                    

                if today == rd_booking_open_date: 
                    nowtime_local_string = nowtime.strftime("%Y-%m-%d %H:%M:%S")
                    nowtime_local = datetime.strptime(nowtime_local_string, '%Y-%m-%d %H:%M:%S')  
                    campground_opentime = datetime.strptime(rd['booking_open_date']+' '+release_time, '%Y-%m-%d %H:%M:%S')    

                    if nowtime_local >= campground_opentime:                    
                        release_period["release_date"] = rd_release_date
                        release_period["booking_open_date"] = rd_booking_open_date

    return release_period
