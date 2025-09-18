from django.urls import path
from .views import (PurchaseEventAPIView, CreatorTransactionLogsListView,
                    ConsumerTransactionLogsListView)

urlpatterns = [
    path('creator/', CreatorTransactionLogsListView.as_view(), name='creator_transactions_list'),
    path('consumer/', ConsumerTransactionLogsListView.as_view(), name='consumer_transactions_list'),
    path('event-purchase/', PurchaseEventAPIView.as_view(), name='purchase_event'),
]
