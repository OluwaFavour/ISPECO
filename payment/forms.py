from django import forms
from .models import Product, Plan
from .utils import check_required_fields


class ProductAddForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["paypal_product_id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize form fields if needed

    def clean(self):
        cleaned_data = super().clean()
        required_fields = ["name", "description"]

        # Validate form data
        check_required_fields(self, required_fields)
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
        required_fields = [
            "product",
            "name",
            "description",
            "billing_cycle",
            "price",
            "setup_fee",
        ]

        # Validate form data
        check_required_fields(self, required_fields)

        name = cleaned_data.get("name")
        billing_cycle = cleaned_data.get("billing_cycle")

        if name and billing_cycle:
            if Plan.objects.filter(name=name, billing_cycle=billing_cycle).exists():
                self.add_error(
                    "name",
                    "Plan with this name and billing cycle already exists. Please provide a different name or billing cycle.",
                )
        return cleaned_data


class PlanAdminForm(forms.ModelForm):
    class Meta:
        model = Plan
        exclude = ["paypal_plan_id", "product", "currency", "billing_cycle", "price"]

    def clean(self):
        cleaned_data = super().clean()
        required_fields = ["name", "description", "setup_fee", "auto_renew"]

        # Validate form data
        check_required_fields(self, required_fields)
        return cleaned_data
