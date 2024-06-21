from itertools import product
from django.db import models
from django.core.validators import RegexValidator
from user_authentication.models import User
from django.utils import timezone


class Product(models.Model):
    name = models.CharField(max_length=300, unique=True)
    description = models.TextField()
    paypal_product_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class Plan(models.Model):
    PLAN_TIERS = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]
    BILLING_FREQUENCIES = [
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=PLAN_TIERS, unique=True)
    description = models.TextField()
    billing_cycle = models.CharField(max_length=50, choices=BILLING_FREQUENCIES)
    price = models.DecimalField(max_digits=30, decimal_places=2)
    setup_fee = models.DecimalField(max_digits=30, decimal_places=2)
    paypal_plan_id = models.CharField(max_length=50, blank=True, null=True)
    currency = models.CharField(max_length=3, default="USD")

    def __str__(self):
        return f"{self.name.title()} ({self.billing_cycle.upper()})"


class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    number = models.CharField(max_length=19, unique=True)
    security_code = models.CharField(max_length=4)
    expiry_date = models.DateField()
    state_province = models.CharField(max_length=300)
    city_town = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=60)
    country_code = models.CharField(
        max_length=2, validators=[RegexValidator(r"^([A-Z]{2}|C2)$")]
    )


class Subscription(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("paypal", "PayPal"),
        ("credit_card", "Credit Card"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, blank=True, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    paypal_subscription_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name.title()} ({self.start_date})"


class TemporarySubscriptionData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    system_setup_data = models.JSONField()
    quantity = models.IntegerField(default=1)
    paypal_subscription_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Tnx ID: {self.transaction_id} - {self.user.email} - {self.amount} {self.subscription.plan.currency.upper()}"
