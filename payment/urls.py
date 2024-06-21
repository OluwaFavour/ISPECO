from django.urls import path

from .views import (
    PayPalCancelView,
    PayPalReturnView,
    PlanCreateView,
    PlanListView,
    PlanUpdateView,
    ProductDetailUpdateDeleteView,
    ProductListCreateView,
    SubscriptionView,
    TransactionDetailView,
    TransactionListView,
)

url_patterns = [
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path(
        "products/<int:pk>/",
        ProductDetailUpdateDeleteView.as_view(),
        name="product-detail-update-delete",
    ),
    path("plans/", PlanListView.as_view(), name="plan-list"),
    path("plans/create/", PlanCreateView.as_view(), name="plan-create"),
    path("plans/<int:pk>/", PlanUpdateView.as_view(), name="plan-update"),
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
