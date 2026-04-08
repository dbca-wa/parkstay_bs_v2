from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from parkstay.models import Booking, BookingInvoice, BookingLog
from ledger_api_client.utils import create_basket_session, create_checkout_session, place_order_submission, use_existing_basket, use_existing_basket_from_invoice, process_api_refund
from parkstay import emails
from parkstay import models as parkstay_models
from parkstay import utils
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from django.test import RequestFactory

from datetime import timedelta, date, datetime
from decimal import Decimal as D
from decimal import Decimal
import itertools
import re
import hashlib
import sys

class Command(BaseCommand):
    help = 'Bulk booking refund cancellation from CSV'

    def add_arguments(self, parser):
        parser.add_argument('file',)
        parser.add_argument('email',)

    def handle(self, *args, **options):
        print ("RUNNING")
        
        booking_cancelled = []
        booking_refunded = []
        booking_errors = []

        file_path = options['file']
        email = options['email']
        print (email)
        try:
            user = EmailUser.objects.get(email=email) 
        except Exception as e:
            print (e)
            sys.exit(1)
        print (file_path)
        f = open(file_path)
        for line in f:
            line = line.strip('\n')
            booking_reference = line
            print(line+":")
            refund_success = False 
      
            factory = RequestFactory()
            request = factory.get('/', data={'debug': 'true'})
            request.user = EmailUser.objects.get(id=user.id)
            print(request.user.is_authenticated)
                   
            booking_reference = re.sub(r'\D', '', line)
            print (booking_reference)
            if parkstay_models.Booking.objects.filter(id=booking_reference).count() > 0:
                booking = parkstay_models.Booking.objects.get(id=booking_reference)
                print (booking)
            else:
                print ("Booking Not Found")
                booking_errors.append({'booking_reference': booking_reference, "message": "Booking Not Found"})
                continue
            if booking.is_canceled is True:
                
                booking_errors.append({'booking_reference': booking_reference, "message": "Already Cancelled"})
            else:
                booking.is_canceled = True
                booking.canceled_by = request.user
                booking.cancelation_time = timezone.now()
                booking.cancellation_reason = "Booking Cancelled (Bulk)"
                booking.save()       
                BookingLog.objects.create(booking=booking,message="Booking Cancelled (Bulk Cancellation)")    
                booking_cancelled.append({'booking_id': booking.id,'booking_customer': booking.customer, "booking_cancelled" : True })        
                                    

    
           
            # Attemping to refund
            booking_totals = utils.booking_total_to_refund(booking)
            totalbooking = booking_totals['refund_total']
            campsitebooking = booking_totals['campsitebooking']
            cancellation_data = booking_totals['cancellation_data']
            
            ## PLACE IN UTILS
            lines = []
            lines = utils.price_or_lineitemsv2old_booking(None,booking, lines)
            #cancellation_data =  utils.booking_change_fees(booking)
    
            basket_params = {
                'products': lines,
                'vouchers': [],
                'system': settings.PS_PAYMENT_SYSTEM_ID,
                'custom_basket': True,
                'booking_reference': settings.BOOKING_PREFIX+'-'+str(booking.id),
                'booking_reference_link': settings.BOOKING_PREFIX+'-'+str(booking.id)

            }
            checkouthash =  hashlib.sha256(str(booking.pk).encode('utf-8')).hexdigest()
            # request.session['checkouthash'] = checkouthash

            return_url = settings.PARKSTAY_EXTERNAL_URL+"/booking/cancellation-success/?checkouthash="+checkouthash
            return_preload_url = settings.PARKSTAY_EXTERNAL_URL+"/booking/return-cancelled/"

            try:
                jsondata = process_api_refund(request, basket_params, booking.customer.id, return_url, return_preload_url)
                if jsondata['message'] == 'success':
                    for ir in jsondata['data']['invoice_reference']:
                        BookingInvoice.objects.get_or_create(booking=booking, invoice_reference=ir)
                    extra_data = {}
                    total_refunded = Decimal('0.00')
                    for order_line in lines:
                        total_refunded = total_refunded + Decimal(order_line['price_incl_tax'])
                    total_refunded = total_refunded - total_refunded - total_refunded 
                    #extra_data['totalbooking'] = round(Decimal(totalbooking),2)
                    extra_data['totalbooking'] = round(total_refunded,2)
                    # extra_data['fees_for_cancellation'] = round(Decimal(fees_for_cancellation),2)                            
                    booking_refunded.append({'booking_id': booking.id, 'amount': str(totalbooking), 'booking_customer': booking.customer.email, 'refund_success': True})
                    try:
                        emails.send_booking_cancelation(booking, extra_data)    
                    except Exception as e:                
                        booking_errors.append({'booking_reference': booking_reference, "message": "ERROR: Sending cancellation email"})
                        print ("ERROR: Sending cancellation email")                              
                           

            except Exception as e:
                booking_refunded.append({'booking_id': booking.id, 'amount': str(totalbooking), 'booking_customer': booking.customer.email, 'refund_success': False})  
                booking_errors.append({'booking_reference': booking_reference, "message": "ERROR: Refund Error and Cancel Email Not Sent"})               
                print ("ERROR: Refund Failed")                                        
                print (e)

                

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
                    print (u'error updating availablity cache {}'.format(booking.id))
                    print ("Error Updating campsite availablity for campsitebooking.id "+str(c.id))
            print (u'availablity cache flagged for update {}'.format(booking.id))
            
        # Send email with success and failed refunds 
        
        context = {
            "booking_cancellation" : booking_cancelled,            
            "booking_refunded" : booking_refunded,
            "booking_errors": booking_errors
        }

        email_list = []
        for email_to in settings.NOTIFICATION_EMAIL.split(","):
            email_list.append(email_to)
        print ("SENDING EMAIL")
        print (settings.EMAIL_FROM)
        print (booking_cancelled)
        emails.sendHtmlEmail(tuple(email_list),"[PARKSTAY] Bulk Refund Cancellation script",context,'ps/email/bulk_refund_cancel.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
        return "Completed"

