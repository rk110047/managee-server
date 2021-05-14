import datetime
from datetime import datetime as dt
from django.utils.timezone import now
import json
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import (
    generics,
    status,
)
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from liveTv.models import Categories,Channels
from liveTv.serializers import CategoriesSerializer, ChannelsSerializer
from utils.permissions import (
    CanEditCategory,
    IsClientAdmin,
    IsOwner,
    ReadOnly,
)
from userprofile.models import UserFavourites
from authentication.renderer import UserJSONRenderer

class CreateAndListCategoryView(generics.ListCreateAPIView):
    """Handle requests for creation of category"""

    serializer_class = CategoriesSerializer
    permission_classes = (IsClientAdmin | ReadOnly,)
    renderer_classes = (UserJSONRenderer,)

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.role == 'admin':
            return Categories.objects.all().order_by("serial_no")

        return Categories.active_objects.all_published().order_by("serial_no")

    def create(self, request, *args, **kwargs):

        request.POST._mutable = True
        payload = request.data
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            'data': {"category": serializer.data}
        }
        return Response(response, status=status.HTTP_201_CREATED)


class CreateAndListChannelsView(generics.GenericAPIView):
    """Handle requests for creation of category"""

    serializer_class = ChannelsSerializer
    permission_classes = (IsClientAdmin | ReadOnly,)
    renderer_classes = (UserJSONRenderer,)

    def get(self, request):
        user = self.request.user
        chfilter = self.request.query_params.get('name',None)
        # when the user is not logged in, ask him to log in
        channels = []
        if user.is_authenticated:
            if chfilter is not None:
                channels = Channels.objects.filter(name__contains=chfilter).order_by("ch_num")
            else:
                channels = Channels.objects.all().order_by("ch_num")
        else:
            return Channels.objects.none()
        channelList = ChannelsSerializer(channels, many=True, context={'request': request}).data
        userFav = UserFavourites.objects.filter(user=user).values_list('live_channels__id', flat=True)
        for ch in channelList:
            isCurrentFav = False
            for fav in userFav:
                if ch["id"] == fav:
                    isCurrentFav = True
                    ch["is_fav"] = True
            if not isCurrentFav:
                ch["is_fav"] = False
        return Response(channelList, status=status.HTTP_200_OK)

    def post(self, request):

        request.POST._mutable = True
        payload = request.data
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            'data': {"channel": serializer.data}
        }
        return Response(response, status=status.HTTP_201_CREATED)
