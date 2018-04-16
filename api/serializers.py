import pyotp
from rest_framework import serializers
from . import mixins


class NoneSerializer(serializers.Serializer):
    pass


class HOTPSerializer(mixins.OTPMixin, serializers.Serializer):
    """
    HOTP Serializer
    """
    count = serializers.IntegerField(required=True, help_text="OTP Counter.")

    def create(self, validated_data):
        """
        Create HOTP PyOTP JSON Response
        :param validated_data: Valid data
        :return: HOTP Response
        """
        count = validated_data.pop('count')
        return self._generate_hotp(count, data=validated_data)


class TOTPSerializer(mixins.OTPMixin, serializers.Serializer):
    """
    TOTP Serializer
    """
    timeout = serializers.IntegerField(required=True, help_text="OTP Validity-Time (in seconds).")

    def create(self, validated_data):
        """
        Create TOTP PyOTP JSON Response
        :param validated_data: Valid data
        :return: TOTP Response
        """
        interval = validated_data.pop('timeout')
        return self._generate_totp(interval, data=validated_data)


class ProvisionURISerializer(serializers.Serializer):
    """
    Provisioning URI Serializer
    """
    name = serializers.CharField(required=True, help_text="Name of the account")
    issuer_name = serializers.CharField(help_text="Name of the OTP issuer")


class HOTPProvisionURISerializer(HOTPSerializer, ProvisionURISerializer):
    """
    HOTP + Provision URI Serializer
    """
    initial_count = serializers.CharField(default=0, help_text="Starting counter value. (Default = 0)")

    def create(self, validated_data):
        """
        Create HOTP Provision URI JSON Response
        :param validated_data: Valid data
        :return: HOTP + URI Response
        """
        count = validated_data.pop('count')
        return self._generate_hotp(count, provision_uri=True, data=validated_data)


class TOTPProvisionURISerializer(TOTPSerializer, ProvisionURISerializer):
    """
    TOTP + Provision URI Serializer
    """
    def create(self, validated_data):
        """
        Create TOTP Provision URI JSON Response
        :param validated_data: Valid data
        :return: TOTP + URI Response
        """
        interval = validated_data.pop('timeout')
        return self._generate_totp(interval, provision_uri=True, data=validated_data)


class VerifyOTPSerializer(serializers.Serializer):
    """
    OTP Verification Serializer
    """
    otp = serializers.CharField(required=True)

    def verify_otp(self, otp, obj, otp_type):
        """
        Verify OTP with provided corresponding type (HOTP/TOTP).
        :param otp: OTP to verify against
        :param obj: PyOTP model object
        :param otp_type: HOTP/TOTP
        :return: Verification result boolean (Accept/Reject)
        """
        if otp_type == 'hotp' and obj.count:
            hotp = pyotp.HOTP(obj.secret)
            return hotp.verify(otp, obj.count)
        elif otp_type == 'totp' and obj.interval:
            totp = pyotp.TOTP(obj.secret, interval=obj.interval)
            return totp.verify(otp)
        return False
