from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
from parkstay import views, api
from parkstay.admin import admin
from parkstay import view_file
from django.contrib.auth.views import LogoutView, LoginView

#from ledger.urls import urlpatterns as ledger_patterns
from ledger_api_client.urls import urlpatterns as ledger_patterns
from django_media_serv.urls import urlpatterns as media_serv_patterns
from django.urls import path

#from django_site_queue import urls as site_queue_urls

# API patterns
router = routers.DefaultRouter()
#router.register(r'campground_map', api.CampgroundMapViewSet)
router.register(r'campground_map_filter', api.CampgroundMapFilterViewSet)
router.register(r'availability', api.AvailabilityViewSet, 'availability')
router.register(r'availability_admin', api.AvailabilityAdminViewSet)
router.register(r'availability_ratis', api.AvailabilityRatisViewSet, 'availability_ratis')
router.register(r'campgrounds', api.CampgroundViewSet)
router.register(r'campsites', api.CampsiteViewSet)
router.register(r'campsite_bookings', api.CampsiteBookingViewSet)
router.register(r'promo_areas', api.PromoAreaViewSet)
router.register(r'parks', api.ParkViewSet)
router.register(r'parkentryrate', api.ParkEntryRateViewSet)
router.register(r'features', api.FeatureViewSet)
router.register(r'regions', api.RegionViewSet)
router.register(r'districts', api.DistrictViewSet)
router.register(r'campsite_classes', api.CampsiteClassViewSet)
router.register(r'booking', api.BookingViewSet)
router.register(r'campground_booking_ranges', api.CampgroundBookingRangeViewset)
router.register(r'campsite_booking_ranges', api.CampsiteBookingRangeViewset)
router.register(r'campsite_rate', api.CampsiteRateViewSet)
router.register(r'campsites_stay_history', api.CampsiteStayHistoryViewSet)
router.register(r'campground_stay_history', api.CampgroundStayHistoryViewSet)
router.register(r'rates', api.RateViewset)
router.register(r'closureReasons', api.ClosureReasonViewSet)
router.register(r'priceReasons', api.PriceReasonViewSet)
router.register(r'maxStayReasons', api.MaximumStayReasonViewSet)
#router.register(r'users', api.UsersViewSet)
router.register(r'contacts', api.ContactViewSet)
router.register(r'countries', api.CountryViewSet)
router.register(r'discountReasons', api.DiscountReasonViewset)

api_patterns = [
    url(r'^api/profile$', api.GetProfile.as_view(), name='get-profile'),
    #url(r'^api/profile/update_personal$', api.UpdateProfilePersonal.as_view(), name='update-profile-personal'),
    #url(r'^api/profile/update_contact$', api.UpdateProfileContact.as_view(), name='update-profile-contact'),
    #url(r'^api/profile/update_address$', api.UpdateProfileAddress.as_view(), name='update-profile-address'),
    url(r'^api/oracle_job$', api.OracleJob.as_view(), name='get-oracle'),
    url(r'^api/bulkPricing', api.BulkPricingView.as_view(), name='bulkpricing-api'),
    url(r'^api/campground_availabilty_view/', api.campground_availabilty_view, name='campground_availabilty_view'),
    url(r'^api/campsite_availablity_view/(?P<campground_id>[0-9]+)/', api.campsite_availablity_view, name='campsite_availablity_view'),
    url(r'^api/search_suggest', api.search_suggest, name='search_suggest'),
    url(r'^api/create_booking', api.create_booking, name='create_booking'),
    url(r'^api/complete_booking/(?P<booking_hash>[\w]+)/(?P<booking_id>[0-9]+)/', api.complete_booking, name='complete_booking'),
    url(r'^api/campground_map/$', api.campground_map_view, name='campground_map'),
    url(r'^api/places/', api.places, name='places'),
    url(r'^api/booking_pricing/$', api.get_booking_pricing, name='booking_pricing'),
    url(r'^api/booking_updates/$', api.booking_updates,  name='booking_updates'),
    url(r'^api/booking_vehicle_update/$', api.booking_vehicle_update,  name='update_booking_vehicle_info'),
    url(r'^api/get_booking_vehicle_info/(?P<booking_id>[0-9]+)/$', api.get_booking_vehicle_info, name='get_booking_vehicle_info'),
    url(r'^api/peak_groups/', api.peak_groups, name='peak_groups'),
    url(r'^api/save_peak_group/', api.save_peak_group, name='peak_group_save'),
    url(r'^api/save_peak_period/', api.save_peak_period, name='save_peak_period'),
    url(r'^api/save_booking_policy/', api.save_booking_policy, name='save_booking_policy'),
    url(r'^api/peak_periods/', api.peak_periods, name='peak_periods'),
    url(r'^api/booking_policy/', api.booking_policy, name='booking_policy'),
    url(r'^api/get_confirmation/(?P<booking_id>[0-9]+)/$', api.get_confirmation, name='get_confirmation'),
    url(r'^api/reports/booking_refunds$', api.BookingRefundsReportView.as_view(), name='booking-refunds-report'),
    url(r'^api/reports/bookings$', api.BookingReportView.as_view(), name='bookings-report'),
    url(r'^api/reports/booking_settlements$', api.BookingSettlementReportView.as_view(), name='booking-settlements-report'),
    url(r'^api/server-date$', api.GetServerDate.as_view(), name='get-server-date'),
    url(r'^api/test_server_api/', api.test_server_api, name='test_server_api'),
    url(r'^api/', include(router.urls))
]

# URL Patterns
urlpatterns = [
    path(r'admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
    #url(r'^login/', LoginView.as_view(),name='login'),
    #url(r'^logout/$', LogoutView.as_view(), {'next_page': '/'}, name='logout'),
    #url(r'^logout/$', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'),
    #url(r'^admin/', admin.site.urls, name='admin_urls'),
    url(r'', include(api_patterns)),
    #url(r'', include(site_queue_urls)),
    #url(r'^account/', views.ProfileView.as_view(), name='account'),
    url(r'^$', views.ParkstayRoutingView.as_view(), name='ps_home'),
    url(r'^$', views.ParkstayRoutingView.as_view(), name='home'),
    url(r'^login-success/$', views.LoginSuccess.as_view(), name='login-success'),
    url(r'^testing-server/$', views.TestView.as_view(), name='test_view'),
    url(r'^status/$', views.StatusView.as_view(), name='status_view'),
    url(r'^testing-server-with-auth/$', views.TestViewAuth.as_view(), name='test_view'),
    url(r'^search-availability/information/', views.SearchAvailablity.as_view(), name='search_availability_information'),
    url(r'^search-availability/campground/', views.SearchAvailablityByCampground.as_view(), name='search_availability_campground'),
    url(r'^campsites/(?P<ground_id>[0-9]+)/$', views.CampsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    #url(r'^availability/$', views.CampsiteAvailabilitySelector.as_view(), name='campsite_availaiblity_selector'),
    #url(r'^availability_admin/$', views.AvailabilityAdmin.as_view(), name='availability_admin'),
    #url(r'^ical/campground/(?P<ground_id>[0-9]+)/$', views.CampgroundFeed(), name='campground_calendar'),
    url(r'^dashboard/peak-periods/$', views.PeakPeriodGroup.as_view(), name='dash-peak-periods'),
    url(r'^dashboard/booking-policy/$', views.BookingPolicy.as_view(), name='dash-booking-policy'),
    url(r'^dashboard/campgrounds$', views.DashboardView.as_view(), name='dash-campgrounds'),
    url(r'^dashboard/campsite-types$', views.DashboardView.as_view(), name='dash-campsite-types'),
    url(r'^dashboard/bookings/edit/', views.DashboardView.as_view(), name='dash-bookings'),
    url(r'^dashboard/bookings$', views.DashboardView.as_view(), name='dash-bookings'),
    url(r'^dashboard/bulkpricing$', views.DashboardView.as_view(), name='dash-bulkpricing'),
    url(r'^dashboard/', views.DashboardView.as_view(), name='dash'),
    url(r'^booking/abort$', views.abort_booking_view, name='public_abort_booking'),
    url(r'^booking/cancel/(?P<booking_id>[0-9]+)/$', views.CancelBookingView.as_view(), name='cancel_booking'),
    url(r'^booking/change/(?P<booking_id>[0-9]+)/$', views.ChangeBookingView.as_view(), name='change_booking'),
    url(r'^booking/', views.MakeBookingsView.as_view(), name='public_make_booking'),
    url(r'^booking-history/(?P<pk>[0-9]+)/', views.ViewBookingHistory.as_view(), name='view_booking_history'),
    url(r'^mybookings/', views.MyBookingsView.as_view(), name='public_my_bookings'),
    url(r'^success/', views.BookingSuccessView.as_view(), name='public_booking_success'),
    url(r'^map/', views.MapView.as_view(), name='map'),
    url(r'^campground-image/(?P<height>[0-9]+)/(?P<width>[0-9]+)/', view_file.getFile, name='campground_image_resize'), 
    url(r'^campground-image-cropped-square/(?P<height>[0-9]+)/(?P<width>[0-9]+)/', view_file.getFileCroppedResized, name='campground_image_resize_cropped_square'),
] + ledger_patterns + media_serv_patterns

#if settings.DEBUG:  # Serve media locally in development.
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
