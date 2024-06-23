from django.urls import path

from .views import (
    PayPalCancelView,
    PayPalReturnView,
    PlanListView,
    SubscriptionView,
    TransactionDetailView,
    TransactionListView,
)

url_patterns = [
    path("plans/", PlanListView.as_view(), name="plan-list"),
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path(
        "transactions/<int:pk>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
    path("paypal/subscribe/", SubscriptionView.as_view(), name="subscription"),
    path(
        "paypal/subscribe/cancel-payment/",
        PayPalCancelView.as_view(),
        name="paypal-cancel",
    ),
    path("paypal/subscribe/success/", PayPalReturnView.as_view(), name="paypal-return"),
]
