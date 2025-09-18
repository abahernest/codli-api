from multiprocessing import Event
from rest_framework import serializers

from .models import TransactionLog


class TransactionLogSerializer (serializers.ModelSerializer):

    event_id = serializers.CharField(write_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)
    quantity = serializers.IntegerField(write_only=True)
    # firstname = serializers.CharField(write_only=True, required=False)
    # lastname = serializers.CharField(write_only=True, required=False)
    # email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = TransactionLog
        fields = '__all__'

    def validate(self, attrs):
        event_id = attrs.get('event_id', '')
        amount = attrs.get('amount', 0)
        quantity = attrs.get('quantity', 0)
        # firstname = attrs.get('firstname', '')
        # lastname = attrs.get('lastname', '')
        # email = attrs.get('email', '')

        if not event_id or event_id == '':
            raise serializers.ValidationError("event_id is required")
        
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise serializers.ValidationError("event not found")

        if amount <= 0:
            raise serializers.ValidationError("amount must be greater than zero")

        if quantity <= 0:
            raise serializers.ValidationError("quantity must be greater than zero")
        
        # if not email or email == '':
        #     raise serializers.ValidationError("email is required")
        
        # if not firstname or firstname == '':
        #     raise serializers.ValidationError("firstname is required")
        
        # if not lastname or lastname == '':
        #     raise serializers.ValidationError("lastname is required")
        
        # user = User.objects.filter(email=email).first()
        # if not user:
        #     user = User.objects.create_user(
        #         email=email,
        #         display_name=f'{firstname} {lastname}',
        #         password=User.objects.make_random_password()
        #     )
        
        attrs['event'] = event
        # attrs['user'] = event.user

        return attrs

class CreatorTransactionLogsListSerializer (serializers.ModelSerializer):

    class Meta:
        model = TransactionLog
        fields = ["reference", "event_name", "event",
         "status", "amount", "quantity", "created_at"]


class ConsumerTransactionLogsListSerializer (serializers.ModelSerializer):

    class Meta:
        model = TransactionLog
        fields = ["reference", "event_name", "event",
                  "status", "amount", "quantity", "created_at"]



