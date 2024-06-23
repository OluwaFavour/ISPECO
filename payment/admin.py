from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .forms import ProductAddForm, ProductAdminForm, PlanAddForm, PlanAdminForm

from .models import Plan, Subscription, Transaction, Product, Card

admin.site.register(Subscription)
admin.site.register(Transaction)
admin.site.register(Card)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    add_form = ProductAddForm
    list_display = ("name", "description", "paypal_product_id")
    search_fields = ("name",)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    form = PlanAdminForm
    add_form = PlanAddForm
    list_display = ("name", "description", "product", "paypal_plan_id")
    search_fields = ("name",)
