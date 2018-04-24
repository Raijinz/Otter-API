from django.urls import path, re_path
from . import views

UUID_REGEX = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
OTP_TYPE_REGEX = '(hotp|totp)'

verify_otp = views.PyOTPViewset.as_view({'post': 'verify_otp', })
generate_hotp = views.PyOTPViewset.as_view({'post': 'generate_hotp', })
generate_totp = views.PyOTPViewset.as_view({'post': 'generate_totp', })
generate_hotp_provision_uri = views.PyOTPViewset.as_view({'post': 'generate_hotp_provision_uri', })
generate_totp_provision_uri = views.PyOTPViewset.as_view({'post': 'generate_totp_provision_uri', })
register_push = views.FCMViewset.as_view({'post': 'register_push', })
send_push = views.FCMViewset.as_view({'post': 'send_push', })

urlpatterns = [
    path('generate-otp/hotp/', generate_hotp, name='generate-hotp'),
    path('generate-otp/totp/', generate_totp, name='generate-totp'),
    path('generate-otp/hotp/provision-uri/', generate_hotp_provision_uri, name='generate-hotp-provision-uri'),
    path('generate-otp/totp/provision-uri/', generate_totp_provision_uri, name='generate-totp-provision-uri'),
    re_path(r'^verify-otp/(?P<otp_type>(hotp|totp))/(?P<uuid>{uuid})/$'
            .format(otp_type=OTP_TYPE_REGEX, uuid=UUID_REGEX), verify_otp, name='verify-otp'),
    re_path(r'^register-push/(?P<uuid>{uuid})/$'.format(uuid=UUID_REGEX), register_push, name='register-push'),
    re_path(r'^send-push/(?P<uuid>{uuid})/$'.format(uuid=UUID_REGEX), send_push, name='send-push'),
]
