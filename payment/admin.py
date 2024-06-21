from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Plan, Subscription, Transaction, Product, Card

admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(Transaction)
admin.site.register(Product)
admin.site.register(Card)
