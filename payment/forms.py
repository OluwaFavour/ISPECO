from typing import Any
from django import forms
from .models import Product, Plan


class ProductAddForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["paypal_product_id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize form fields if needed

    def clean(self):
        cleaned_data = super().clean()
        # Validate form data
        if not cleaned_data.get("name"):
            self.add_error("name", "Name is required.")
        if not cleaned_data.get("description"):
            self.add_error("description", "Description is required.")
        if (
            cleaned_data.get("name")
            and Product.objects.filter(name=cleaned_data.get("name")).exists()
        ):
            self.add_error("name", "Product with this name already exists.")
        return cleaned_data


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["paypal_product_id", "name"]

    def clean(self):
        cleaned_data = super().clean()
        # Validate form data
        if not cleaned_data.get("description"):
            self.add_error("description", "Description is required.")

        instance = self.instance
        if instance and cleaned_data.get("description") == instance.description:
            self.add_error(
                "description",
                "Description is the same as the previous one. Please provide a different description.",
            )
        return cleaned_data


class PlanAddForm(forms.ModelForm):
    class Meta:
        model = Plan
        exclude = ["paypal_plan_id"]

    def clean(self):
        cleaned_data = super().clean()
        # Validate form data
        if not cleaned_data.get("product"):
            self.add_error("product", "Product is required.")
        if not cleaned_data.get("name"):
            self.add_error("name", "Name is required.")
        if not cleaned_data.get("description"):
            self.add_error("description", "Description is required.")
        if not cleaned_data.get("billing_cycle"):
            self.add_error("billing_cycle", "Billing cycle is required.")
        if not cleaned_data.get("price"):
            self.add_error("price", "Price is required.")
        if not cleaned_data.get("setup_fee"):
            self.add_error("setup_fee", "Setup fee is required.")
        if (
            cleaned_data.get("name")
            and Plan.objects.filter(name=cleaned_data.get("name")).exists()
        ):
            self.add_error("name", "Plan with this name already exists.")
        return cleaned_data


class PlanAdminForm(forms.ModelForm):
    class Meta:
        model = Plan
        exclude = ["paypal_plan_id", "product", "currency", "billing_cycle", "price"]

    def clean(self):
        cleaned_data = super().clean()
        # Validate form data
        if not cleaned_data.get("description"):
            self.add_error("description", "Description is required.")
        if not cleaned_data.get("setup_fee"):
            self.add_error("setup_fee", "Setup fee is required.")
        if not cleaned_data.get("auto_renew"):
            self.add_error("auto_renew", "Auto renew is required.")
        if not cleaned_data.get("name"):
            self.add_error("name", "Name is required.")
        return cleaned_data
