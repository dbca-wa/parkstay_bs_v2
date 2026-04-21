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

class Command(BaseCommand):
    help = 'Bulk booking refund cancellation'

    # def add_arguments(self, parser):
        # Positional arguments
        #parser.add_argument('days_back', nargs='+', type=int)
        # parser.add_argument('file',)

    def handle(self, *args, **options):
        print ("RUNNING")
        
        rfc = parkstay_models.BulkRefundCancel.objects.filter(bulk_status__in=[0,1],paused=False)
        for r in rfc:
            if r.bulk_status == 0:
                r.bulk_status = 1
                r.save()
            factory = RequestFactory()
            request = factory.get('/', data={'debug': 'true'})
            request.user = EmailUser.objects.get(id=r.created_by)
            print(request.user.is_authenticated)
            bfcl = parkstay_models.BulkRefundCancelList.objects.filter(bulk_refund_cancel=r, processed=False).order_by('pk')[:100]
            for b in bfcl:
                # print (b.booking_reference)
                b_obj = parkstay_models.BulkRefundCancelList.objects.get(id=b.id)
                     

                booking_reference = re.sub(r'\D', '', b.booking_reference)
                print (booking_reference)
                if parkstay_models.Booking.objects.filter(id=booking_reference).count() > 0:
                    booking = parkstay_models.Booking.objects.get(id=booking_reference)
                    print (booking)
                else:
                    print ("Booking Not Found")
                    b_obj.message = "ERROR: Booking Not Found"
                    b_obj.processed = True       
                    b_obj.completed = datetime.now()                       
                    b_obj.save()
                    continue

                if b.cancel_type == 0:
                    booking.is_canceled = True
                    booking.canceled_by = EmailUser.objects.get(id=r.created_by)
                    booking.cancelation_time = timezone.now()
                    booking.cancellation_reason = "Booking Cancelled (Bulk)"
                    booking.save()       
                            
                    b_obj.cancel_type = 1
                    b_obj.save()                        

                            

                      


                if b.refund_type == 0 or b.refund_type == 1:
                    # Attemping to refund
                    booking_totals = utils.booking_total_to_refund(booking)
                    totalbooking = booking_totals['refund_total']
                    campsitebooking = booking_totals['campsitebooking']
                    cancellation_data = booking_totals['cancellation_data']
                   
                    ## PLACE IN UTILS
                    lines = []
                    lines = utils.price_or_lineitemsv2old_booking(None,booking, lines)
                    #cancellation_data =  utils.booking_change_fees(booking)
                    cancellation_data = utils.booking_cancellation_fees(booking)
                    
                    fees_for_cancellation = float('0.00')
                    
                    if b.refund_type == 1:
                        lines.append({'ledger_description':'Booking Cancellation Fee',"quantity":1,"price_incl_tax":str(cancellation_data['cancellation_fee']),"oracle_code":booking.campsite_oracle_code, 'line_status': 1})
                        fees_for_cancellation = float(cancellation_data['cancellation_fee'])
                    else:
                        # Full Refund
                        # no cancellation fees
                        pass

           
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
                            extra_data['fees_for_cancellation'] = round(Decimal(fees_for_cancellation),2)

                            if b.refund_type == 1:
                                b_obj.refund_type = 3
                                b_obj.save()
                            if b.refund_type == 0:
                                b_obj.refund_type = 2
                                b_obj.save()                                



                    except Exception as e:
                        if b.refund_type == 1:
                            b_obj.refund_type = 5
                            b_obj.message = b_obj.message + "\nERROR: Refund Failed ({})".format(str(e))
                            b_obj.save()
                        if b.refund_type == 0:
                            b_obj.refund_type = 4
                            b_obj.message = b_obj.message + "\nERROR: Refund Failed ({})".format(str(e))
                            b_obj.save()         
                                         
                        print (e)

                if b.email_type == 0:
                    if booking.is_canceled is True:
                        try:
                            extra_data = {}
                            total_refunded = Decimal('0.00')
                            for order_line in lines:
                                total_refunded = total_refunded + Decimal(order_line['price_incl_tax'])
                            total_refunded = total_refunded - total_refunded - total_refunded 
                            #extra_data['totalbooking'] = round(Decimal(totalbooking),2)
                            extra_data['totalbooking'] = round(total_refunded,2)
                            extra_data['fees_for_cancellation'] = round(Decimal(fees_for_cancellation),2)

                            emails.send_booking_cancelation(booking, extra_data)
                            b_obj.email_type = 1
                            b_obj.save()   
                        except Exception as e:
                            b_obj.email_type = 3
                            b_obj.message = "ERROR: Sending cancellation email ({})".format(str(e))
                
                            b_obj.save()


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
                b_obj.processed = True       
                b_obj.completed = datetime.now()      
                b_obj.save()


            bfcl_total = parkstay_models.BulkRefundCancelList.objects.filter(bulk_refund_cancel=r, processed=False).count()
            if bfcl_total == 0:
                r.bulk_status = 2
                r.save()                

        # Send email with success and failed refunds 
        
        # context = {
        #  "booking_cancellation":booking_cancelled,
        #  "booking_errors": booking_errors 
        # }
        # email_list = []
        # for email_to in settings.NOTIFICATION_EMAIL.split(","):
            #    email_list.append(email_to)
        # print ("SENDING EMAIL")
        # print (settings.EMAIL_FROM)
        # print (booking_cancelled)
        # emails.sendHtmlEmail(tuple(email_list),"[PARKSTAY] Bulk cancellation script",context,'ps/email/bulk_cancel.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
        return "Completed"

