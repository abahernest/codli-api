from django.urls import path
from .views import (EventListView, EventListingViewset, NewEventAPIView, 
                    ReviewCreateView, ReviewListView, SimilarEventView,
                    EventDetailView, UpdateEventAPIView
                    )

urlpatterns = [
    path(
        '', EventListView.as_view({'get': 'list'}), name='all_events'),
    path(
        'listings/', EventListingViewset.as_view({'get': 'list'}), name='event_listing'),
    path('new/', NewEventAPIView.as_view(), name='new_event'),
    path('single/<event_id>/', EventDetailView.as_view(), name='single_event'),
    path('update/<event_id>/', UpdateEventAPIView.as_view(), name='update_event'),
    path('similar_events/<event_id>/',
         SimilarEventView.as_view(), name='similar_event'),
    path('reviews/',
         ReviewListView.as_view(), name='review_list'),
    path('add-review/',
         ReviewCreateView.as_view(), name='add_review'),
]
