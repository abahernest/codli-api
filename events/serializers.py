import json
from rest_framework import serializers
from rest_framework.exceptions import ParseError


from .models import (CURRENCY_CHOICES, EVENT_CATEGORY_CHOICES, EVENT_PAYMENT_PLAN_CHOICES, EVENT_STATUS_CHOICES, Event, Review)
from users.models import User
from utils.constants import (
    ALLOWABLE_NUMBER_OF_DOCUMENTS, ALLOWABLE_NUMBER_OF_IMAGES, ALLOWABLE_DOCUMENT_TYPES)
from utils.date import (greater_than_today)



class NewEventSerializer (serializers.ModelSerializer):

    def validate_file_size(value):
        max_size = 8388608
        if value.size > max_size:
            raise serializers.ValidationError('Maximum file size is 8MB')

    default_image = serializers.ImageField(
        allow_empty_file=False,
        max_length=256,
        validators=[validate_file_size],
        required=False,
    )

    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    price = serializers.IntegerField(required=False)
    status = serializers.ChoiceField(required=False, choices=EVENT_STATUS_CHOICES)
    currency = serializers.ChoiceField(required=False, choices=CURRENCY_CHOICES)
    payment_plan = serializers.ChoiceField(required=False, choices=EVENT_PAYMENT_PLAN_CHOICES)
    total_tickets = serializers.IntegerField(required=False)

    category = serializers.ChoiceField(required=False, choices=EVENT_CATEGORY_CHOICES)

    class Meta:
        model = Event
        # fields = '__all__'
        fields = ['id','title', 'description', 'status', 'category', 'address', 'city',
        'state','country', 'start_date', 'end_date', 'price', 'currency', 'payment_plan', 'total_tickets',
        'default_image', 'total_tickets', 
        ]
        read_only_fields=['id' ]

    def validate(self, attrs):
        category = attrs.get('category','')
        start_date = attrs.get('start_date','')
        end_date = attrs.get('end_date','')
        currency = attrs.get('currency','')
        payment_plan = attrs.get('payment_plan','')

        ## using form inputs parses the string in an array
        if category and category not in [choice[0] for choice in EVENT_CATEGORY_CHOICES]:
            raise serializers.ValidationError("invalid category")
        if currency and currency not in [choice[0] for choice in CURRENCY_CHOICES]:
            raise serializers.ValidationError("invalid currency")
        if payment_plan and payment_plan not in [choice[0] for choice in EVENT_PAYMENT_PLAN_CHOICES]:
            raise serializers.ValidationError("invalid payment_plan")
        if start_date and not greater_than_today(start_date):
            raise serializers.ValidationError("start_date must be a future date")
        if end_date and start_date and end_date <= start_date:
            raise serializers.ValidationError("end_date must be greater than start_date")

        return attrs
            
    def create(self, validated_data):
        return Event.objects.create(**validated_data)


    def update(self, instance, validated_data):

        updatable_fields = {}
        for key in validated_data: 
            updatable_fields[key] = validated_data.get(key)

        return Event.objects.filter(id=instance.id).update(**updatable_fields)


class EventSerializer (serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'


class SimilarEventListSerializer (serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['id', 'title', 'created_at', 'city', 'state', 'country', 'payment_plan',
                  'status', 'category', 'price', 'currency', 'start_date', 'end_date']

class EventTableSerializer (serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['id', 'title', 'created_at', 'city', 'state', 'country', 'payment_plan',
                  'status', 'category', 'price', 'currency', 'start_date', 'end_date']

class EventListingSerializer (serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['id', 'title', 'created_at', 'city', 'state', 'country', 'payment_plan',
                  'status', 'category', 'price', 'currency', 'start_date', 'end_date']
        

class ReviewersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'display_photo', 'display_name']


class ReviewsSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(max_value=5, min_value=1, required=False)
    review = serializers.CharField(required=False)
    reviewer = ReviewersSerializer(required=False)

    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Review
        fields = ['rating', 'review', 'reviewer', 'created_at']

    def validate(self, attrs):
        rating = attrs.get('rating')
        review = attrs.get('review')

        if not rating and not review:
            raise serializers.ValidationError(
                "must provide 'review' or 'rating'.")

        return attrs

    def create(self, validated_data) -> Review:
        return Review.objects.create(
            **validated_data
        )