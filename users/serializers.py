from rest_framework import serializers
from django.utils import timezone, dateparse

dateparse.parse_date

from .models import User, CREATOR_TYPE_CHOICES


class UpdateProfileSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(min_length=3, read_only=True)
    display_photo = serializers.ImageField(
        allow_empty_file=False, required=False)
    display_name = serializers.CharField(min_length=2, max_length=65, required=False)
    summary = serializers.CharField(required=False)
    job_description = serializers.CharField(required=False)
    job_name = serializers.CharField(min_length=2, max_length=255, required=False)
    city = serializers.CharField(max_length=255, required=False)
    country = serializers.CharField(max_length=255, required=False)
    job_type = serializers.ChoiceField(choices=CREATOR_TYPE_CHOICES, required=False)

    class Meta:
        model = User
        fields = ['email', 'display_photo', 'display_name', 'city', 'country',
                  'summary', 'job_description', 'job_name', 'job_type',
                  ]

    def validate(self, attrs):
        email = attrs.get('email', '')
        display_name = str(attrs.get('display_name', ''))
        summary = str(attrs.get('summary', ''))
        job_description = str(attrs.get('job_description', ''))
        job_name = str(attrs.get('job_name', ''))
        city = str(attrs.get('city', ''))
        country = str(attrs.get('country', ''))
        job_type = str(attrs.get('job_type', ''))

        if city and len(city) < 3:
            raise serializers.ValidationError("city must contain at least 3 characters")

        if country and len(country) < 3:
            raise serializers.ValidationError("country must contain at least 3 characters")

        return attrs

    def update(self, instance: User, validated_data):

        updatable_fields =  {}

        for key in validated_data:
            updatable_fields[key] = validated_data.get(key)

        instance.save()
        User.objects.filter(id=instance.id).update(**updatable_fields)

        return instance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
