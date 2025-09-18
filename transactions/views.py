from asyncio import Event
from rest_framework import (views, permissions)
from rest_framework.response import Response
from django.db import transaction


from .serializers import (
    ConsumerTransactionLogsListSerializer,
    CreatorTransactionLogsListSerializer, 
    TransactionLogSerializer)
from .models import TransactionLog
from utils.paystack import chargeCard, generateTransactionReference
from notifications.models import Notifications

class ConsumerTransactionLogsListView(views.APIView):

    serializer_class = ConsumerTransactionLogsListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):

        tx_logs = TransactionLog.objects.filter(payed_by=request.user).order_by("-created_at")

        serializer = self.serializer_class(tx_logs, many=True)

        return Response(serializer.data, status=200)



class CreatorTransactionLogsListView(views.APIView):

    serializer_class = CreatorTransactionLogsListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        tx_logs = TransactionLog.objects.filter(user=request.user).order_by("-created_at")

        serializer = self.serializer_class(tx_logs, many=True)

        return Response(serializer.data, status=200)



class PurchaseEventAPIView(views.APIView):

    serializer_class = TransactionLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            bulkLogs, notificationsList = [], []
            event = serializer.validated_data['event']

            ## generate referenceId
            referenceId = generateTransactionReference()

            # Queue Transaction
            payment_service_response = chargeCard()

            ## create Transaction Logs for owner
            bulkLogs.append(
                TransactionLog(**{
                    "event_name": event.title,
                    "reference": referenceId,
                    "event": event,
                    "user": event.user,
                    "payed_by": request.user,
                    "quantity": serializer.validated_data['quantity'],
                    "amount": event.price * 100,
                    "currency": event.currency,
                    "fee": payment_service_response.get('fee'),
                    **payment_service_response
                }))

            ## save notifications object
            payment_status = payment_service_response.get('status')
            notification_message = f'{payment_status} transaction for event {event.id}'
            notificationsList.extend([
                {"user": request.user, "message": notification_message}, ##notify consumer
                {"user": event.user, "message": notification_message} ##notify creator
                ])

            transactionLogs = TransactionLog.objects.create(bulkLogs)

            ## send notifications
            Notifications.new_bulk_entry(notificationsList)

            serializer = self.serializer_class(transactionLogs, many=True)

        return Response(serializer.data, status=200)



