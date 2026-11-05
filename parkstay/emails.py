from io import BytesIO
from django.conf import settings
from parkstay import pdf
from parkstay import models
from ledger_api_client.pdf import create_invoice_pdf_bytes
#from ledger.payments.pdf import create_invoice_pdf_bytes
from ledger_api_client.ledger_models import Invoice
#from ledger.payments.models import Invoice
#from ledger.emails.emails import EmailBase2 as EmailBase
from wagov_utils.components.utils.email import TemplateEmailBase as WAGovUtilsTemplateEmailBase
from django.template.loader import render_to_string, get_template
from django.core.exceptions import ValidationError
#from django.template import Context
from django.core.mail import EmailMessage, EmailMultiAlternatives
from email.mime.base import MIMEBase
from django.core.files.base import ContentFile
from parkstay import doctopdf
import hashlib
import datetime
import socket
import requests
import decouple
from email import encoders
default_campground_email = settings.EMAIL_FROM


# Every Parkstay email must be sent by wagov_utils TemplateEmailBase.send()
# (EMAIL_DELIVERY switch, logs/email.log, System-Environment header).
class TemplateEmailBase(WAGovUtilsTemplateEmailBase):
    subject = ''
    html_template = 'ps/email/base_email.html'
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = 'ps/email/base_email.txt'


def send_booking_invoice(booking):
    log_hash = int(hashlib.sha1(str(datetime.datetime.now()).encode('utf-8')).hexdigest(), 16) % (10 ** 8)
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your booking invoice for {}'.format(booking.campground.name)
    email_obj.html_template = 'ps/email/invoice.html'
    email_obj.txt_template = 'ps/email/invoice.txt'

    email = booking.customer.email

    context = {
        'booking': booking
    }
    filename = 'invoice-{}({}-{}).pdf'.format(booking.campground.name, booking.arrival, booking.departure)
    references = [b.invoice_reference for b in booking.invoices.all()]
    invoice = Invoice.objects.filter(reference__in=references).order_by('-created')[0]

    #invoice_pdf = create_invoice_pdf_bytes(filename, invoice)
    api_key = settings.LEDGER_API_KEY
    url = settings.LEDGER_API_URL+'/ledgergw/invoice-pdf/'+api_key+'/'+invoice.reference
    invoice_pdf = requests.get(url=url)
    #cfile = ContentFile(invoice_pdf.content, name=filename)
    campground_email = booking.campground.email if booking.campground.email else default_campground_email
    if invoice_pdf.status_code == 200:
       email_obj.send([email], from_address=default_campground_email, reply_to=campground_email, context=context, attachments=[(filename, invoice_pdf.content, 'application/pdf')])
       email_log(str(log_hash)+' : '+str(email) + ' - '+ email_obj.subject)
       booking.send_invoice = True
       booking.save()
    else:
       raise ValidationError('Error exporting invoice from ledger')



def send_booking_confirmation(booking_id, extra_data):
    print ("Sending Booking Confirmation for: "+str(booking_id))
    log_hash = int(hashlib.sha1(str(datetime.datetime.now()).encode('utf-8')).hexdigest(), 16) % (10 ** 8)
    booking = models.Booking.objects.get(id=booking_id)    
    #PARKSTAY_EXTERNAL_URL
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your Park Stay WA campsite booking {} at {}, {} is confirmed'.format(booking.confirmation_number, booking.campground.name, booking.campground.park.name)
    email_obj.html_template = 'ps/email/confirmation-booking.html'
    email_obj.txt_template = 'ps/email/confirmation.txt'

    if booking.old_booking:
        if booking.old_booking > 0:
            email_obj.subject = 'Your change to Park Stay WA campsite booking {} at {}, {} is confirmed'.format(booking.confirmation_number, booking.campground.name, booking.campground.park.name)
    #       email_obj.html_template = 'ps/email/confirmation-change-booking.html'
    #       email_obj.txt_template = 'ps/email/confirmation.txt'

    email = booking.customer.email

    cc = None
    bcc = [default_campground_email]

    campground_email = booking.campground.email if booking.campground.email else default_campground_email
    if campground_email != default_campground_email:
        cc = [campground_email]

    #my_bookings_url = request.build_absolute_uri('/mybookings/')
    my_bookings_url = settings.PARKS_EXTERNAL_BOOKING_URL+str('/mybookings/')
    booking_availability = settings.PARKS_EXTERNAL_BOOKING_URL+str('/availability/?site_id={}'.format(booking.campground.id))
    #booking_availability = request.build_absolute_uri('/availability/?site_id={}'.format(booking.campground.id))
    unpaid_vehicle = False
    mobile_number = booking.customer.mobile_number
    booking_number = booking.details.get('phone', None)
    phone_number = booking.customer.phone_number
    tel = None
    if booking_number:
        tel = booking_number
    elif mobile_number:
        tel = mobile_number
    else:
        tel = phone_number
    tel = tel if tel else ''

    for v in booking.vehicle_payment_status:
        if v.get('Paid') == 'No':
            unpaid_vehicle = True
            break

    check_in_time = booking.campground.check_in.strftime('%I:%M %p')
    if booking.campground.check_in.strftime('%I:%M %p') == '12:00 AM':
            check_in_time = "12 midnight"
    if booking.campground.check_in.strftime('%I:%M %p') == '12:00 PM':
            check_in_time = "12 noon"

    check_out_time = booking.campground.check_out.strftime('%I:%M %p')
    if booking.campground.check_out.strftime('%I:%M %p') == '12:00 AM':
        check_out_time = "12 midnight"
    if booking.campground.check_out.strftime('%I:%M %p')  == '12:00 PM':
        check_out_time = "12 noon"

    check_in_date_time = datetime.datetime.strptime(booking.arrival.strftime("%Y-%m-%d")+' '+booking.arrival.strftime('%I:%M %p'), '%Y-%m-%d %I:%M %p')
    grace_period_expire = booking.created + datetime.timedelta(minutes=extra_data['grace_period'])
    grace_period_expire_formatted = datetime.datetime.strptime(grace_period_expire.strftime('%Y-%m-%d %I:%M %p'),'%Y-%m-%d %I:%M %p')
    additional_info = booking.campground.additional_info if booking.campground.additional_info else ''

    #booking_cancellation_fees(booking)
    booking_invoices = models.BookingInvoice.objects.filter(booking=booking)

    grace_period_valid = True
    if grace_period_expire_formatted > check_in_date_time:
        grace_period_valid = False

    invoice_reference = ''
    if booking_invoices.count() > 0:
        invoice_reference = booking_invoices[0].invoice_reference
    context = {
        'booking': booking,
        'phone_number': tel,
        'campground_email': campground_email,
        'my_bookings': my_bookings_url,
        'availability': booking_availability,
        'unpaid_vehicle': unpaid_vehicle,
        'additional_info': additional_info,
        'check_in_date_time': check_in_date_time,
        'check_in_time' : check_in_time,
        'check_out_time' : check_out_time,
        'extra_data' : extra_data,
        'grace_period_expire' : grace_period_expire,
        'grace_period_valid' : grace_period_valid,
        'PARKSTAY_EXTERNAL_URL' : settings.PARKSTAY_EXTERNAL_URL,
        'invoice_reference' : invoice_reference
    }

    pdf_buffer = doctopdf.create_confirmation(booking)
    #att = BytesIO()
    #pdf.create_confirmation(att, booking)
    #att.seek(0)
    #covidfile = None
    #with open(settings.BASE_DIR+"/parkstay/static/parkstay/pdf/parkstay-covid.pdf") as opened:
    #     covidfile = opened.read()

    #email_obj.send([email], from_address=default_campground_email, reply_to=campground_email, context=context, cc=cc, bcc=bcc, attachments=[('confirmation-PB{}.pdf'.format(booking.id), pdf_buffer, 'application/pdf'),])
    #email_log(str(log_hash)+' : '+str(email) + ' - '+ email_obj.subject)
    print ("SENDING EMAIL")
    sendHtmlEmail([email],email_obj.subject,context,email_obj.html_template,cc,bcc,default_campground_email,'parkstayv2',attachments=[('confirmation-PB{}.pdf'.format(str(booking.id)), pdf_buffer, 'application/pdf')])

    booking.confirmation_sent = True
    booking.save()


def send_booking_cancelation(booking,extra_data):
    log_hash = int(hashlib.sha1(str(datetime.datetime.now()).encode('utf-8')).hexdigest(), 16) % (10 ** 8)
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your Park Stay WA campsite booking {} at {}, {} is cancelled'.format(booking.confirmation_number, booking.campground.name, booking.campground.park.name)
    email_obj.html_template = 'ps/email/confirmation-cancelled.html'
    email_obj.txt_template = 'ps/email/cancel.txt'

    email = booking.customer.email

    bcc = [default_campground_email]

    cc=None
    campground_email = booking.campground.email if booking.campground.email else default_campground_email
    if campground_email != default_campground_email:
        cc = [campground_email]


    campground_email = booking.campground.email if booking.campground.email else default_campground_email
    my_bookings_url = '{}/mybookings/'.format(settings.PARKSTAY_EXTERNAL_URL)
    context = {
        'booking': booking,
        'my_bookings': my_bookings_url,
        'campground_email': campground_email,
        'settings' : settings,
        'extra_data': extra_data
    }
    
    sendHtmlEmail([email],email_obj.subject,context,email_obj.html_template,cc,bcc,default_campground_email,'parkstayv2',attachments=[]) 
    #email_obj.send([email], from_address=default_campground_email, reply_to=campground_email, cc=[campground_email], bcc=bcc, context=context)
    #email_log(str(log_hash)+' : '+str(email) + ' - '+ email_obj.subject)


def send_booking_reminder(booking_id, extra_data):
    print ("Sending Booking Confirmation for: "+str(booking_id))
    booking = models.Booking.objects.get(id=booking_id)    
    #PARKSTAY_EXTERNAL_URL
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Reminder: it’s nearly time for your camping trip to {}, {}'.format(booking.campground.name, booking.campground.park.name)
    email_obj.html_template = 'ps/email/confirmation-reminder.html'
    email_obj.txt_template = 'ps/email/confirmation.txt'

    email = booking.customer.email

    cc = None
    bcc = [default_campground_email]

    campground_email = booking.campground.email if booking.campground.email else default_campground_email
    if campground_email != default_campground_email:
        cc = [campground_email]

    #my_bookings_url = request.build_absolute_uri('/mybookings/')
    my_bookings_url = settings.PARKS_EXTERNAL_BOOKING_URL+str('/mybookings/')
    booking_availability = settings.PARKS_EXTERNAL_BOOKING_URL+str('/availability/?site_id={}'.format(booking.campground.id))
    #booking_availability = request.build_absolute_uri('/availability/?site_id={}'.format(booking.campground.id))
    unpaid_vehicle = False
    mobile_number = booking.customer.mobile_number
    booking_number = booking.details.get('phone', None)
    phone_number = booking.customer.phone_number
    tel = None
    if booking_number:
        tel = booking_number
    elif mobile_number:
        tel = mobile_number
    else:
        tel = phone_number
    tel = tel if tel else ''

    for v in booking.vehicle_payment_status:
        if v.get('Paid') == 'No':
            unpaid_vehicle = True
            break

    check_in_time = booking.campground.check_in.strftime('%I:%M %p')
    if booking.campground.check_in.strftime('%I:%M %p') == '12:00 AM':
            check_in_time = "12 midnight"
    if booking.campground.check_in.strftime('%I:%M %p') == '12:00 PM':
            check_in_time = "12 noon"

    check_out_time = booking.campground.check_out.strftime('%I:%M %p')
    if booking.campground.check_out.strftime('%I:%M %p') == '12:00 AM':
        check_out_time = "12 midnight"
    if booking.campground.check_out.strftime('%I:%M %p')  == '12:00 PM':
        check_out_time = "12 noon"

    grace_period_expire = booking.created + datetime.timedelta(minutes=extra_data['grace_period'])
    additional_info = booking.campground.additional_info if booking.campground.additional_info else ''

    #booking_cancellation_fees(booking)
    booking_invoices = models.BookingInvoice.objects.filter(booking=booking)

    invoice_reference = ''
    if booking_invoices.count() > 0:
        invoice_reference = booking_invoices[0].invoice_reference

    context = {
        'booking': booking,
        'phone_number': tel,
        'campground_email': campground_email,
        'my_bookings': my_bookings_url,
        'availability': booking_availability,
        'unpaid_vehicle': unpaid_vehicle,
        'additional_info': additional_info,
        'check_in_time' : check_in_time,
        'check_out_time' : check_out_time,
        'extra_data' : extra_data,
        'grace_period_expire' : grace_period_expire,
        'PARKSTAY_EXTERNAL_URL' : settings.PARKSTAY_EXTERNAL_URL,
        'invoice_reference' : invoice_reference,
        'notification_type' : 'reminder'
    }

    print ("SENDING EMAIL")
    sendHtmlEmail([email],email_obj.subject,context,email_obj.html_template,None,bcc,default_campground_email,'parkstayv2',attachments=[])

    booking.reminder_email_sent = True
    booking.save()

def send_booking_lapse(booking):
    log_hash = int(hashlib.sha1(str(datetime.datetime.now()).encode('utf-8')).hexdigest(), 16) % (10 ** 8)
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your booking for {} has expired'.format(booking.campground.name)
    email_obj.html_template = 'ps/email/lapse.html'
    email_obj.txt_template = 'ps/email/lapse.txt'

    email = booking.customer.email
    campground_email = booking.campground.email if booking.campground.email else default_campground_email

    context = {
        'booking': booking,
        'settings': settings,
    }
    email_obj.send([email], from_address=default_campground_email, reply_to=campground_email, context=context)
    email_log(str(log_hash)+' :'+str(email) + ' - '+ email_obj.subject)

def email_log(line):
     dt = datetime.datetime.now()
     hostname = socket.gethostname()
     f= open(settings.BASE_DIR+"/logs/email.log","a+")
     f.write(str(dt.strftime('%Y-%m-%d %H:%M:%S'))+': '+hostname+': '+line+"\r\n")
     f.close()

def sendHtmlEmail(to,subject,context,template,cc,bcc,from_email,template_group,attachments=None):
    print ("start -- sendHtmlEmail")
    email_delivery = decouple.config('EMAIL_DELIVERY', default='off')
    override_email = decouple.config('OVERRIDE_EMAIL', default=None)
    email_instance = decouple.config('EMAIL_INSTANCE',default='DEV')
    logomime = None
    context['default_url'] = decouple.config('DEFAULT_HOST', default='')
    context['default_url_internal'] = decouple.config('DEFAULT_URL_INTERNAL', default='')
    log_hash = int(hashlib.sha1(str(datetime.datetime.now()).encode('utf-8')).hexdigest(), 16) % (10 ** 8)
    email_log(str(log_hash)+' '+subject+":"+str(to)+":"+template_group)
    if email_delivery != 'on':
        print ("EMAIL DELIVERY IS OFF NO EMAIL SENT -- email.py ")
        return False
    if template is None:
        raise ValidationError('Invalid Template')
    if to is None:
        raise ValidationError('Invalid Email')
    if subject is None:
        raise ValidationError('Invalid Subject')

    if from_email is None:
        if settings.DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL
        else:
            from_email = 'no-reply@dbca.wa.gov.au'

    context['version'] = settings.VERSION_NO
    # Custom Email Body Template
    context['body'] = get_template(template).render(context)
    # Main Email Template Style ( body template is populated in the center
    if template_group == 'system-oim':
        main_template = get_template('ps/email/base_email-oim.html').render(context)
    elif template_group == 'parkstayv2': 
        with open(settings.BASE_DIR+'/parkstay/static/ps/img/parkstay_bookings_logo.png','rb') as f:
            logomime = MIMEBase('image','png', filename='Parkstay Logo')
            logomime.add_header('Content-Disposition', 'attachment', filename='parkstaybooking.png')
            logomime.add_header('X-Attachment-Id', 'parkstay_logo')
            logomime.add_header('Content-ID', '<parkstay_logo>')
            logomime.set_payload(f.read())
            encoders.encode_base64(logomime)
            #parkstay/static/ps/img/parkstay_bookings_logo.png

        main_template = get_template('ps/email/base_email-parkstay.html').render(context)
    else:
        main_template = get_template('ps/email/base_email2.html').render(context)

    reply_to=None

    if attachments is None:
        attachments = []
    # Convert Documents to (filename, content, mime) attachment
    _attachments = []
    for attachment in attachments:
        #if isinstance(attachment, Document):
        #     filename = str(attachment)
        #     content = attachment.file.read()
        #     mime = mimetypes.guess_type(attachment.filename)[0]
        #     _attachments.append((filename, content, mime))
        #else:
             _attachments.append(attachment)

    if override_email is not None:
        to = override_email.split(",")
        if cc:
            cc = override_email.split(",")
        if bcc:
            bcc = override_email.split(",")

    if len(to) > 1:
        msg = EmailMultiAlternatives(subject, "Please open with a compatible html email client.", from_email=from_email, to=to, attachments=_attachments, cc=cc, bcc=bcc, reply_to=reply_to, headers={'System-Environment': email_instance})
        if logomime:
           msg.attach(logomime)

        msg.attach_alternative(main_template, 'text/html')

        #msg = EmailMessage(subject, main_template, to=[to_email],cc=cc, from_email=from_email)
        #msg.content_subtype = 'html'
        #if attachment1:
        #    for a in attachment1:
        #        msg.attach(a)
        try:
             email_log(str(log_hash)+' '+subject)
             msg.send()
             email_log(str(log_hash)+' Successfully sent to mail gateway')
        except Exception as e:
                email_log(str(log_hash)+' Error Sending - '+str(e))

    else:
          msg = EmailMultiAlternatives(subject, "Please open with a compatible html email client.", from_email=from_email, to=to, attachments=_attachments, cc=cc, bcc=bcc, reply_to=reply_to, headers={'System-Environment': email_instance})
          if logomime:
              msg.attach(logomime)

          msg.attach_alternative(main_template, 'text/html')

          #msg = EmailMessage(subject, main_template, to=to,cc=cc, from_email=from_email)
          #msg.content_subtype = 'html'
          #if attachment1:
          #    for a in attachment1:
          #        msg.attach(a)
          try:
               email_log(str(log_hash)+' '+subject)
               msg.send()
               email_log(str(log_hash)+' Successfully sent to mail gateway')
          except Exception as e:
               email_log(str(log_hash)+' Error Sending - '+str(e))


    return True


