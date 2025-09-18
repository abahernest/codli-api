import uuid
from django.db import models
from django.utils import timezone
from users.models import User
from django.contrib.postgres.fields import ArrayField


EVENT_STATUS_CHOICES = [
    ('DRAFTS', 'drafts'),
    ('ACTIVE', 'active'),
    ('ARCHIVED', 'archived'),
    ('DELETED', 'deleted')
]
COMPLETION_STATUS_CHOICES = [
    ('IN-PROGRESS', 'construction in progress'),
    ('COMPLETED', 'contruction completed'),
]
EVENT_CATEGORY_CHOICES = [
    ('MUSIC', 'Music events'),
    ('ART', 'Art events'),
    ('MOVIES', 'Movie events'),
    ('COMEDY', 'Comedy events'),
    ('SPORTS', 'Sports events'),
    ('FASHION', 'Fashion events'),
    ('TECH', 'Tech events'),
    ('EDUCATION', 'Educational events'),
    ('BUSINESS', 'Business events'),
    ('OTHER', 'Other events'),
]

EVENT_PAYMENT_PLAN_CHOICES = [
    ('FREE', 'Free event'),
    ('PAID', 'Paid event'),
    ('DONATION', 'Donation based event'),
]
CURRENCY_CHOICES = [
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'),
    ('NGN', 'Nigerian Naira'),
    ('GBP', 'British Pound'),
    ('KES', 'Kenyan Shilling'),
]

def get_default_image_upload_path(instance, filename):
    name = "events"
    date = str(timezone.now().date())
    return f'{name}/default_images/{date}/{filename}'

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=256, blank=False)
    description = models.TextField(blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    status = models.CharField(
        choices=EVENT_STATUS_CHOICES,
        max_length=255, 
        default=EVENT_STATUS_CHOICES[0][0] )
    category = models.CharField(
        choices=EVENT_CATEGORY_CHOICES,
        max_length=255, 
        null=True)

    address = models.CharField(max_length=255, blank=False)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=False)
    country = models.CharField(max_length=50, blank=False)

    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    default_image = models.ImageField(upload_to=get_default_image_upload_path, null=True)

    price = models.PositiveBigIntegerField(default=0)
    currency = models.CharField(
        choices=CURRENCY_CHOICES,
        max_length=10, 
        default=CURRENCY_CHOICES[0][0])
    payment_plan = models.CharField(
        choices=EVENT_PAYMENT_PLAN_CHOICES,
        max_length=255, 
        default=EVENT_PAYMENT_PLAN_CHOICES[0][0])
    ticket_link = models.URLField(max_length=500, null=True, blank=True)
    total_tickets = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'


class Review(models.Model):
    rating  = models.IntegerField(null=True)
    review  = models.TextField()
    reviewer = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'