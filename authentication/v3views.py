import jwt
from django.conf import settings
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
from rest_framework import authentication
from rest_framework import (
    generics,
    status,
)
from rest_framework.exceptions import NotFound
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.models import (
    User, UserProfile, UserDevices)
from authentication.permissions import (
    IsClientAdmin,
    IsProfileOwner,
    IsOwnerOrAdmin)
from authentication.renderer import UserJSONRenderer, ClientJSONRenderer
from django.core.exceptions import ObjectDoesNotExist
from authentication.v3serializers import (
    RegistrationSerializer,
    BlackListSerializer, ProfileSerializer, LoginSerializer)
from django.core.cache import cache
from django.contrib.auth import authenticate
# from utils import BaseUtils
from utils.permissions import IsViewerOrReadOnly, IsReviewer, IsAdmin
from utils.emailer import Emailer
from utils.util import generateOTP
from subscription.manager import SubscriptionSessionManager

class ValidateOTPAPIView(generics.GenericAPIView):

    session_manager = SubscriptionSessionManager()

    def post(self, request):
        email = request.data["email"]
        existing_otp = cache.get(email)
        if existing_otp == str(request.data["otp"]):
            user = User.objects.get(username=email)
            auth_token = user.token
            session_allowed = self.session_manager.get(user, request.data.get('device_name'), request.data.get('device_model'), request.data.get('device_type'), request.data.get('mac_address'), request.data.get('location', None))
            if session_allowed == True:
                resp_data = {
                    "data" : {
                        "user": {
                            "email": email,
                            "token": auth_token
                        },
                        "message": "otp matched",
                        "status": "success"
                    }
                }
                cache.delete(email)
                return Response(resp_data, status=status.HTTP_200_OK)
            resp_failure = {
                "data" : {
                    "messsage": "active session limit exhausted for user",
                    "status": "failed"
                }
            }
            return Response(resp_failure, status=status.HTTP_403_FORBIDDEN)  
        resp_data = {
            "data" : {
                "message": "otp didn't matched, please check your email",
                "status": "failed"
            }
        }
        return Response(resp_data, status=status.HTTP_401_UNAUTHORIZED)

class VerifyAccountAPIView(generics.GenericAPIView):

    def post(self, request):
        email = request.data["email"]
        existing_otp = cache.get(email)
        if existing_otp == str(request.data["otp"]):
            user = User.objects.get(username=email)
            user.is_verified = True
            user.save()
            resp_data = {
                "data" : {
                    "user": {
                         "email": email,
                    },
                    "message": "Email Id verified successfully",
                    "status": "success"
                }
            }
            cache.delete(email)
            return Response(resp_data, status=status.HTTP_200_OK)
        resp_data = {
            "data" : {
                "message": "otp didn't matched, please check your email",
                "status": "failed"
            }
        }
        return Response(resp_data, status=status.HTTP_401_UNAUTHORIZED)

class RegistrationAPIView(generics.GenericAPIView):
    """Register new users."""
    serializer_class = RegistrationSerializer
    renderer_classes = (UserJSONRenderer,)
    emailer = Emailer()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        message = [
            request,
            user_data["email"]
        ]
        otp = generateOTP()
        cache.set(user_data["email"], otp, None)
        self.emailer.send_verify_email(user_data["email"], otp)
        response = {
            "data": {
                "user": dict(user_data),
                "message": "Account created successfully, Please verify your email Id",
                "status": "success"
            }
        }
        return Response(response, status=status.HTTP_201_CREATED)        

class LoginAPIView(generics.GenericAPIView):
    """login a user via email"""
    serializer_class = LoginSerializer
    renderer_classes = (UserJSONRenderer,)
    emailer = Emailer()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.data
        otp = cache.get(user_data["email"])
        if otp is None:
            otp = generateOTP()
            cache.set(user_data["email"], otp, None)
        self.emailer.send_otp_email(user_data["email"], otp)
        response = {
            "data": {
                "user": dict(user_data),
                "message": "OTP has been send to your email account successfully",
                "status": "success"
            }
        }
        return Response(response, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    """logout user via email"""
    renderer_classes = (UserJSONRenderer,)
    permission_classes = (IsAuthenticated, IsProfileOwner)
    session_manager = SubscriptionSessionManager()

    def post(self, request):
        loggedOut = self.session_manager.put(request.data.get('mac_address', None))
        if not loggedOut:
            response = {
                "data": {
                    "message":"Please specify device Mac address to logout",
                    "status":"failed"
                }
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response = {
            "data": {
                "message": "You have successfully logged out",
                "status": "success"
            }
        }
        return Response(response, status=status.HTTP_200_OK)

class ForgotPasswordAPIView(generics.GenericAPIView):

    emailer = Emailer()

    def post(self, request):
        email = request.data["email"]
        otp = cache.get(email)
        if otp is None:
            otp = generateOTP()
            cache.set(email, otp, None)
        self.emailer.send_forgot_password_email(email, otp)
        response = {
            "data": {
                "message": "OTP has been send to your email account successfully",
                "status": "success"
            }
        }
        return Response(response, status=status.HTTP_200_OK)

class UpdatePasswordAPIView(generics.GenericAPIView):
    """ Update User password """

    def post(self, request):
        if len(request.data["new_password"]) < 6:
           resp = {"errors": {"password": ["Ensure this field has at least 6 characters."] } }
           return Response(resp, status = status.HTTP_400_BAD_REQUEST)
        if request.user.is_anonymous:
            email = request.data["email"]
            existing_otp = cache.get(email)
            if existing_otp == str(request.data["otp"]):
                user = User.objects.get(username=email)
                update_status = self.update_password(request.data, user)
                if update_status:
                    cache.delete(email)
                    response = { "data": { "message": "password updated successfully", "status": "success" } }
                    return Response(response, status=status.HTTP_200_OK)
            else:
                response = { "data": { "message": "Otp didn't matched", "status": "failure" } }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = authenticate(username=request.user.email, password=request.data['current_password'])
            if user is not None:
                update_status = self.update_password(request.data, request.user)
                if update_status:
                    response = { "data": { "message": "password updated successfully", "status": "success" } }
                    return Response(response, status=status.HTTP_200_OK)

        response = { "data": { "message": "password didn't matched", "status": "failure" } }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def update_password(self, data, currentUser):
        if data["new_password"] == data["confirm_password"]:
            currentUser.set_password(data["new_password"])
            currentUser.save()
            return True
        return False

class ProfileView(generics.GenericAPIView):
    """
    This View handles retreiving and updating of users profile
    """

    permission_classes = (IsAuthenticated, IsProfileOwner)
    serializer_class = ProfileSerializer

    def get(self, request):
        """
        Retreive a users profile without their security answer and question
        """
        user_object = User.objects.get(pk=request.user.pk)
        profile_data = {}
        try:
            profile = UserProfile.objects.get(user_id=request.user.pk)
            profile_data = model_to_dict(
                profile,
                fields=['recording_time','parental_lock','package'])
        except ObjectDoesNotExist:
            pass
        user_data = model_to_dict(
            user_object,
            fields=['id', 'email'])
        user_profile = { **user_data , **profile_data }
        # profile = UserProfile.objects.get(user=request.data)
        # print('user datasssss', profile)
        # profile_data = model_to_dict(
        #     user_data,
        #     exclude=['security_question', 'security_answer', 'is_deleted'])
        # profile_data['user'] = user_data
        # print('user datasssss', profile_data)
        data = {
            "data": {
                "profile": user_profile
            },
            "message": "Profile retreived successfully"
        }
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request):
        """
        Update a users  profile
        """
        profile = UserProfile.objects.get(user=request.user)
        self.check_object_permissions(request, profile)
        profile_data = request.data

        serializer = self.serializer_class(
            profile, data=profile_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        updated_profile = dict(serializer.data)
        response = {
            "data": {
                "profile": updated_profile,
                "message": "Profile updated successfully"
            }
        }
        return Response(response, status=status.HTTP_200_OK)
