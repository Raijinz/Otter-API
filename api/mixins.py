import pyotp
from django.contrib.auth.models import User
from fcm_django.models import FCMDevice
from .models import PyOTP


class OTPMixin(object):
    """
    Mixin for PyOTP model
    """
    provision_uri = False

    def _get_random_base32_string(self):
        """
        Generate Random Base32 String
        :return: Random Base32 String
        """
        return pyotp.random_base32()

    def _insert_into_db(self, user=None, secret=None, count=None, interval=None, data={}):
        """
        Insert new PyOTP object into DB
        :param secret: OTP secret
        :param count: HOTP count
        :param interval: TOTP interval
        :param data: Provisioning URI data
        :return: PyOTP model object
        """
        fields = {
            'secret': secret,
            'count': count,
            'interval': interval,
            'user': user,
        }

        # If provision setting is True, save all remaining data into DB
        if self.provision_uri is True:
            fields.update(**data)

        return PyOTP.objects.create(**fields)

    def _create_response(self, otp, instance, otp_type_obj, data):
        """
        Create Response
        :param otp:
        :param instance:
        :param otp_type_obj:
        :param data:
        :return: JSON Response
        """
        response = {
            'otp_uuid': str(instance.uuid),
            'otp': otp,
        }

        # Generate provision URI if setting is True
        if self.provision_uri is True:
            provisioning_uri = otp_type_obj.provisioning_uri(**data)
            response = {
                'otp_uuid': str(instance.uuid),
                'provisioning_uri': provisioning_uri,
            }

        return response

    def _generate_hotp(self, count, provision_uri=False, data={}):
        """
        Generates counter-based OTPs
        :param count: HOTP count
        :param provision_uri: Provision URI setting
        :param data: Provision URI data
        :return: HOTP JSON Response
        """
        self.provision_uri = provision_uri
        base32string = self._get_random_base32_string()
        hotp = pyotp.HOTP(base32string)
        otp = hotp.at(count)

        # Save data into DB
        obj = self._insert_into_db(secret=base32string, count=count, data=data)
        return self._create_response(otp, obj, hotp, data)

    def _generate_totp(self, interval, provision_uri=False, data={}):
        """
        Generates time-based OTPs
        :param interval: TOTP interval
        :param provision_uri: Provision URI setting
        :param data: Provision URI data
        :return: TOTP JSON Response
        """
        self.provision_uri = provision_uri
        base32string = self._get_random_base32_string()
        totp = pyotp.TOTP(base32string, interval=interval)
        otp = totp.now()

        # Save data into DB
        obj = self._insert_into_db(secret=base32string, interval=interval, data=data)
        return self._create_response(otp, obj, totp, data)


class FCMMixin(object):
    """
    Mixin for FCM model
    """
    def _update_user(self, username, uuid):
        """

        :param user:
        :param uuid:
        :return:
        """
        user = PyOTP.objects.get(uuid=uuid)
        user.user = User.objects.get(username=username)
        return user.save()

    def _find_user_device(self, uuid):
        """
        Find the User's FCM device
        :param uuid: UUID
        :return: FCMDevice of that User
        """
        user = PyOTP.objects.get(uuid=uuid)
        device = FCMDevice.objects.get(user=user.user)
        return device
