from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import views
from rest_framework.filters import SearchFilter
from rest_framework import (parsers,permissions,authentication)
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db import transaction
# from rest_framework.decorators import permission_classes
from django.db.models import Avg, Count

from .models import User
from .serializers import (UpdateProfileSerializer)
from utils.pagination import CustomPagination
from utils.constants import (NUMBER_OF_REVIEWS_TO_DISPLAY)
from authentication.permissions import IsCustomer, IsAgent


class Profile(views.APIView):

    serializer_class = UpdateProfileSerializer
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self,request):

        user_id = request.user.id
        user = User.objects.get(id=user_id)

        serializer = self.serializer_class(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()
            # user.refresh_from_db()
            user = User.objects.filter(id=user_id).values('id','display_name', 'email',
                                        'city', 'country', 'job_name', 'job_description',
                                        'summary', 'role', 'job_type', 'summary',
                                        'display_photo'
                                       )[0]

            return Response(user, status=200)


    def get(self,request):

        user_id = request.GET.get('user_id') if request.GET.get('user_id') else request.user.id
        user = User.objects.get(id=user_id)

        serializer = self.serializer_class(user)

        return Response(serializer.data, status=200)
