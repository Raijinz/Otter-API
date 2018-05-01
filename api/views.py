from rest_framework import viewsets, status
from rest_framework.response import Response
import requests
from . import models, serializers


class PyOTPViewset(viewsets.GenericViewSet):
    """
    PyOTP Generic Viewset, every PyOTP HTTP request is handled by this class
    """
    queryset = models.PyOTP.objects.all()
    lookup_field = 'uuid'
    otp_type = None

    def get_serializer_class(self):
        if self.action == 'generate_hotp':
            return serializers.HOTPSerializer
        elif self.action == 'generate_totp':
            return serializers.TOTPSerializer
        elif self.action == 'generate_hotp_provision_uri':
            return serializers.HOTPProvisionURISerializer
        elif self.action == 'generate_totp_provision_uri':
            return serializers.TOTPProvisionURISerializer
        elif self.action == 'verify_otp':
            return serializers.VerifyOTPSerializer
        return serializers.NoneSerializer

    def _validate(self, serializer, data):
        """

        :param serializer: Corresponding Serializer
        :param data: Request data
        :return: Save serializer instance
        """
        serializer_instance = serializer(data=data)
        serializer_instance.is_valid(raise_exception=True)

        return serializer_instance.save()

    def generate_hotp(self, request):
        """
        Generate HOTP view
        :param request: Request
        :return: HOTP JSON Response
        """
        serializer = self.get_serializer_class()
        serializer = self._validate(serializer, request.data)

        return Response(serializer, status=status.HTTP_201_CREATED)

    def generate_totp(self, request):
        """
        Generate TOTP view
        :param request: Request
        :return: TOTP JSON Response
        """
        serializer = self.get_serializer_class()
        serializer = self._validate(serializer, request.data)

        return Response(serializer, status=status.HTTP_201_CREATED)

    def generate_hotp_provision_uri(self, request):
        """
        Generate HOTP URI view
        :param request: Request
        :return: HOTP + URI Response
        """
        serializer = self.get_serializer_class()
        serializer = self._validate(serializer, request.data)

        return Response(serializer, status=status.HTTP_201_CREATED)

    def generate_totp_provision_uri(self, request):
        """
        Generate TOTP URI view
        :param request: Request
        :return: TOTP + URI Resposne
        """
        serializer = self.get_serializer_class()
        serializer = self._validate(serializer, request.data)

        return Response(serializer, status=status.HTTP_201_CREATED)

    def verify_otp(self, request, otp_type, uuid):
        """
        OTP Verification view
        :param request: Request
        :param otp_type: HOTP/TOTP
        :param uuid: PyOTP instance UUID
        :return: 200 OK/400 Bad Request
        """
        obj = self.get_object()
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        valid_otp = serializer.verify_otp(serializer.data.get('otp'), obj, otp_type)
        if not valid_otp:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class FCMViewset(viewsets.GenericViewSet):
    """
    FCM Viewset, every FCM HTTP request is handled by this class
    """
    def get_serializer_class(self):
        if self.action == 'send_push':
            return serializers.FCMSendSerializer
        elif self.action == 'register_push':
            return serializers.FCMRegisterSerializer
        elif self.action == 'verify_push':
            return serializers.FCMVerifySerializer
        elif self.action == 'mobile_push':
            return serializers.FCMMobileSerializer
        return serializers.NoneSerializer

    def register_push(self, request, uuid):
        """

        :param request:
        :param uuid:
        :return:
        """
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.register_push(serializer.data.get('username'), uuid)
        if not result:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    def send_push(self, request, uuid):
        """

        :param request:
        :param uuid:
        :return:
        """
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.send_push(uuid)
        if result is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(data=result, status=status.HTTP_200_OK)

    def verify_push(self, request):
        """

        :param request:
        :param refer:
        :return:
        """
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.verify_push(serializer.data.get('username'), serializer.data.get('refer_code'), serializer.data.get('accept'))
        if not result:
            self.callback(result)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self.callback(result)
        return Response(status=status.HTTP_200_OK)

    def mobile_push(self, request):
        """

        :param request:
        :return:
        """
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.mobilelink(serializer.data.get('username'), serializer.data.get('registration_id'))
        if not result:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    def callback(self, result):
        if result is False:
            requests.post('http://161.246.5.9', data={'http_code': 400})
        else:
            requests.post('http://161.246.5.9', data={'http_code': 200})
