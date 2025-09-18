import json
from rest_framework import (views, permissions, parsers)
from rest_framework.response import Response
from django.db import transaction
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db.models import Q

from .serializers import (EventListingSerializer, EventSerializer, EventTableSerializer, NewEventSerializer,
                          ReviewsSerializer, SimilarEventListSerializer)
from .models import EVENT_STATUS_CHOICES, Event, Review
from notifications.models import Notifications
from utils.pagination import CustomPagination
from utils.constants import (MAXIMUM_SIMILAR_PROPERTIES)
from utils.date import (convert_datetime_to_readable_date)

class NewEventAPIView(views.APIView):

    serializer_class = NewEventSerializer
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        serializer = self.serializer_class(data= request.data)
        serializer.is_valid(raise_exception=True)


        with transaction.atomic():
            event=serializer.save(user = request.user)
            event = Event.objects.filter(id=event.id).values()[0]

            ## notify agent
            notificationMessage = f'New Event Added. {event["title"]}'
            Notifications.new_entry(user= request.user, message=notificationMessage)

        return Response(event, status=200)


class EventListView(ReadOnlyModelViewSet):

    filter_backends = [SearchFilter]
    serializer_class = EventTableSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['title']
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.request.user.id
        return Event.objects.filter(
            user=user_id
        ).order_by('-created_at')


class EventListingViewset(ReadOnlyModelViewSet):

    filter_backends = [SearchFilter]
    serializer_class = EventListingSerializer
    search_fields = ['title']
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Event.objects.filter(
            status=EVENT_STATUS_CHOICES[1][0],            
        )

        country = self.request.query_params.get('country')
        if country is not None:
            queryset = queryset.filter(country__icontains=country)

        state = self.request.query_params.get('state')
        if state is not None:
            queryset = queryset.filter(state__icontains=state)

        status = self.request.query_params.get('status')
        if status is not None:
            queryset = queryset.filter(status__iexact=status)

        category = self.request.query_params.get('category')
        if category is not None:
            queryset = queryset.filter(category__iexact=category)

        payment_plan = self.request.query_params.get('payment_plan')
        if payment_plan is not None:
            queryset = queryset.filter(payment_plan__iexact=payment_plan)
        


        queryset = queryset.order_by('-created_at')
        return queryset


class SimilarEventView(views.APIView):

    serializer_class = SimilarEventListSerializer
    pagination_class = CustomPagination

    def get(self, request, event_id):

        events = Event.objects.filter(id=event_id)
        if len(events) < 1:
            return Response({
                'status_code': 400,
                'error': 'No event with that ID',
                'payload': ['No event with that ID']}, status=400)

        events = Event.objects.filter(
            ~Q(id=event_id),
            name__icontains=events[0].nameame,
            status=EVENT_STATUS_CHOICES[1][0]
        )[:MAXIMUM_SIMILAR_PROPERTIES]

        serializer = self.serializer_class(events, many=True)

        return Response(serializer.data, status=200)


class EventDetailView(views.APIView):

    serializer_class = EventSerializer

    def get(self, request, event_id):

        events = Event.objects.filter(id=event_id)
        if len(events) < 1:
            return Response({
                'status_code': 400,
                'error': 'No event with that ID',
                'payload': ['No event with that ID']}, status=400)

        event = events[0]

        serializer = self.serializer_class(event)

        output = serializer.data
        number_of_listed_events = Event.objects.filter(
            user=event.user, status=EVENT_STATUS_CHOICES[1][0]).count()

        output['user'] = {
            'id': event.user.id,
            'display_name': event.user.display_name,
            'display_photo': event.user.display_photo.url if event.user.display_photo else None,
            'country': event.user.country,
            'email': event.user.email,
            'job_name': event.user.job_name,
            'listed_events': number_of_listed_events
        }

        return Response(output, status=200)


class UpdateEventAPIView(views.APIView):

    serializer_class = NewEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, event_id):

        events = Event.objects.filter(id=event_id)
        if len(events) < 1:
            return Response({
                'status_code': 400,
                'error': 'No event with that ID',
                'payload': ['No event with that ID']}, status=400)

        event = events[0]
        if event.user != request.user:
            return Response({
                'status_code': 400,
                'error': 'This resource belongs to another user',
                'payload': ['This resource belongs to another user']}, status=400)

        serializer = self.serializer_class(event, data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()
            event = Event.objects.filter(id=event.id).values()[0]

        return Response(event, status=200)


class ReviewListView(views.APIView):

    serializer_class = ReviewsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, company_id):

        reviews = Review.objects.filter(company=company_id)

        serializer = self.serializer_class(reviews, many=True)

        return Response(serializer.data, status=200)


class ReviewCreateView(views.APIView):

    serializer_class = ReviewsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, company_id):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save(reviewer = request.user)

        return Response(serializer.data, status=200)
