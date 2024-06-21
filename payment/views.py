from itertools import product
from locale import currency
from re import sub
from typing import Any, Dict
from django.shortcuts import redirect
from rest_framework import generics, status
from rest_framework import generics, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from camera_integration.models import Camera, CameraSetup
from user_authentication.models import User
from .models import (
    Card,
    Plan,
    Product,
    Subscription,
    TemporarySubscriptionData,
    Transaction,
)
from .serializers import (
    PlanSerializer,
    PlanUpdateSerializer,
    SubscriptionSerializer,
    TransactionSerializer,
    ProductSerializer,
)
from .paypal_client import PayPalClient
from django.utils import timezone


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        # Deserialize the incoming request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated data
        validated_data = serializer.validated_data
        name = validated_data.get("name")
        description = validated_data.get("description")

        # Initialize PayPal client and create product
        paypal_client = PayPalClient()
        try:
            paypal_product = paypal_client.create_product(
                name=name, description=description
            )
            paypal_product_id = paypal_product.get("id")
        except Exception as e:
            return Response(
                {"error": "Failed to create product in PayPal", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Create and save the Product instance
        product = Product.objects.create(
            name=name, description=description, paypal_product_id=paypal_product_id
        )

        # Serialize and return the created product
        serializer = self.get_serializer(product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(
            "PUT", detail="PUT method is not allowed. Use PATCH instead."
        )

    def partial_update(self, request, *args, **kwargs):
        instance: Product = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Check and update description
        description = validated_data.get("description")
        if description and description != instance.description:
            instance.description = description

            # Update the corresponding product in PayPal
            paypal_client = PayPalClient()
            try:
                paypal_client.update_product(
                    product_id=instance.paypal_product_id,
                    description=description,
                )
            except Exception as e:
                return Response(
                    {"error": "Failed to update product in PayPal", "details": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Save the instance if PayPal update was successful
            instance.save()

        # Serialize and return the updated instance
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class PlanCreateView(generics.CreateAPIView):
    serializer_class = PlanSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        name = validated_data.get("name")
        billing_cycle = validated_data.get("billing_cycle")
        price = validated_data.get("price")
        setup_fee = validated_data.get("setup_fee")
        currency = validated_data.get("currency")
        product = validated_data.get("product")
        description = validated_data.get("description")
        paypal_product_id = product.paypal_product_id
        paypal_client = PayPalClient()
        try:
            paypal_plan = paypal_client.create_plan(
                name=name,
                billing_cycle=billing_cycle,
                price=price,
                setup_fee=setup_fee,
                currency=currency,
                product_id=paypal_product_id,
                description=description,
            )
            paypal_plan_id = paypal_plan.get("id")
        except Exception as e:
            return Response(
                {"error": "Failed to create plan in PayPal", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        plan = Plan.objects.create(
            name=name,
            billing_cycle=billing_cycle,
            price=price,
            setup_fee=setup_fee,
            currency=currency,
            product=product,
            description=description,
            paypal_plan_id=paypal_plan_id,
        )

        serializer = self.get_serializer(plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PlanUpdateView(generics.UpdateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanUpdateSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(
            "PUT", detail="PUT method is not allowed. Use PATCH instead."
        )

    def partial_update(self, request, *args, **kwargs):
        instance: Plan = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        paypal_updates = {}
        fields_to_update = [
            "name",
            "setup_fee",
            "description",
            "auto_renew",
        ]

        for field in fields_to_update:
            if field in validated_data:
                if field == "auto_renew":
                    paypal_updates[field] = validated_data[field]
                elif validated_data[field] != getattr(instance, field):
                    setattr(instance, field, validated_data[field])
                    paypal_updates[field] = validated_data[field]

        try:
            if paypal_updates:
                paypal_client = PayPalClient()
                paypal_client.update_plan(
                    plan_id=instance.paypal_plan_id, **paypal_updates
                )

            instance.save()
            return Response(self.get_serializer(instance).data)

        except Exception as e:
            return Response(
                {"error": "Failed to update plan", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SubscriptionView(generics.GenericAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        subscriptions = Subscription.objects.filter(user=request.user)
        if subscriptions.exists():
            serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user = validated_data["user"]
        plan = validated_data["plan"]
        system_setup_data = validated_data["system_setup_data"]
        card = validated_data.get("card")
        auto_renew = validated_data["auto_renew"]
        quantity = validated_data["quantity"]
        payment_method = validated_data["payment_method"]

        return_url = self.request.build_absolute_uri("/api/payment/subscribe/success/")
        cancel_url = self.request.build_absolute_uri(
            "/api/payment/subscribe/cancel-payment/"
        )

        try:
            paypal_subscription_id, approval_url = self._process_payment(
                user,
                plan,
                system_setup_data,
                card,
                auto_renew,
                quantity,
                payment_method,
                return_url,
                cancel_url,
            )
        except Exception as e:
            return Response(
                {"error": "Failed to process payment", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if payment_method.upper() == "PAYPAL":
            # Save temporary subscription data
            TemporarySubscriptionData.objects.create(
                user=user,
                plan=plan,
                system_setup_data=system_setup_data,
                auto_renew=auto_renew,
                quantity=quantity,
                paypal_subscription_id=paypal_subscription_id,
            )
            return redirect(approval_url)
        else:
            return Response({"message": "Subscription activated successfully"})

    def _process_payment(
        self,
        user,
        plan,
        system_setup_data,
        card,
        auto_renew,
        quantity,
        payment_method,
        return_url,
        cancel_url,
    ):
        subscriber = {
            "given_name": user.full_name.split(" ")[0],
            "surname": user.full_name.split(" ")[1],
            "email_address": user.email,
        }

        if payment_method.upper() == "CREDIT_CARD" and card:
            subscriber["card"] = {
                "name": card["name"],
                "number": card["number"],
                "security_code": card["security_code"],
                "expiry": card["expiry_date"].strftime("%Y-%m"),
                "billing_address": {
                    "postal_code": card["postal_code"],
                    "country_code": card["country_code"],
                    "admin_area_1": card["state_province"],
                    "admin_area_2": card["city_town"],
                },
            }

        paypal_client = PayPalClient()
        paypal_subscription = paypal_client.create_subscription(
            plan_id=plan.paypal_plan_id,
            return_url=return_url,
            cancel_url=cancel_url,
            auto_renew=True,
            quantity=quantity,
            payment_method=payment_method,
            subscriber=subscriber,
        )

        paypal_subscription_id = paypal_subscription["id"]

        if paypal_subscription["status"] == "ACTIVE":
            start_date = timezone.now()
            end_date = start_date + timezone.timedelta(
                days=30 if plan.billing_cycle == "monthly" else 365
            )

            try:
                card = self._create_card(user, card)
                subscription = self._create_subscription(
                    user,
                    plan,
                    card,
                    start_date,
                    end_date,
                    auto_renew,
                    paypal_subscription_id,
                )
                self._create_transaction(
                    user, subscription, plan, quantity, paypal_subscription_id
                )
                self._handle_system_setup(user, system_setup_data)
            except Exception as e:
                raise Exception("Failed to create subscription") from e

        return paypal_subscription_id, next(
            link["href"]
            for link in paypal_subscription["links"]
            if link["rel"] == "approve"
        )

    def _create_card(self, user, card_data):
        return Card.objects.create(
            user=user,
            name=card_data["name"],
            number=card_data["number"],
            security_code=card_data["security_code"],
            expiry_date=card_data["expiry_date"],
            state_province=card_data["state_province"],
            city_town=card_data["city_town"],
            postal_code=card_data["postal_code"],
            country_code=card_data["country_code"],
        )

    def _create_subscription(
        self, user, plan, card, start_date, end_date, auto_renew, paypal_subscription_id
    ):
        return Subscription.objects.create(
            user=user,
            plan=plan,
            card=card,
            start_date=start_date,
            end_date=end_date,
            auto_renew=auto_renew,
            paypal_subscription_id=paypal_subscription_id,
        )

    def _create_transaction(self, user, subscription, plan, quantity, transaction_id):
        return Transaction.objects.create(
            user=user,
            subscription=subscription,
            amount=plan.price * quantity,
            setup_fee=plan.setup_fee,
            transaction_id=transaction_id,
        )

    def _handle_system_setup(self, user, system_setup_data):
        for cam in range(system_setup_data["number_of_cameras"]):
            camera = Camera.objects.create(
                user=user,
                industry_type=system_setup_data["industry_type"],
                camera_type=system_setup_data["camera_type"],
                environment=system_setup_data["environment"],
                resolution=system_setup_data["resolution"],
                brand=system_setup_data["brand"],
            )
            camera.stream_url = system_setup_data["url"]
            camera.save()
            CameraSetup.objects.create(
                camera=camera,
                address_line_1=system_setup_data["address_line_1"],
                address_line_2=system_setup_data["address_line_2"],
                city=system_setup_data["city"],
                zip_code=system_setup_data["zip_code"],
                state_province=system_setup_data["state_province"],
                country=system_setup_data["country"],
                date=system_setup_data["date"],
                time=system_setup_data["time"],
                installation_notes=system_setup_data["installation_notes"],
            )


# Paypal return and view
class PayPalReturnView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        paypal_subscription_id = request.GET.get("subscription_id")

        try:
            temp_data = TemporarySubscriptionData.objects.get(
                paypal_subscription_id=paypal_subscription_id
            )
        except TemporarySubscriptionData.DoesNotExist:
            return Response(
                {"error": "Subscription data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if self.request.user != temp_data.user:
            return Response(
                {"error": "You can only activate your own subscription"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            subscription = self._create_subscription(temp_data)
            self._create_transaction(temp_data, subscription)
            self._handle_system_setup(temp_data)

        except Exception as e:
            return Response(
                {"error": f"Failed to create subscription: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        temp_data.delete()
        return Response({"message": "Subscription activated successfully"})

    def _create_subscription(self, temp_data):
        plan = temp_data.plan
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(
            days=30 if plan.billing_cycle == "monthly" else 365
        )

        return Subscription.objects.create(
            user=temp_data.user,
            plan=plan,
            card=None,
            start_date=start_date,
            end_date=end_date,
            auto_renew=temp_data.auto_renew,
            paypal_subscription_id=temp_data.paypal_subscription_id,
        )

    def _create_transaction(self, temp_data, subscription):
        plan = temp_data.plan
        quantity = temp_data.quantity

        Transaction.objects.create(
            user=temp_data.user,
            subscription=subscription,
            amount=plan.price * quantity,
            setup_fee=plan.setup_fee,
            transaction_id=temp_data.paypal_subscription_id,
        )

    def _handle_system_setup(self, temp_data):
        system_setup_data = temp_data.system_setup_data

        for cam_data in system_setup_data["cameras"]:
            camera = Camera.objects.create(
                user=temp_data.user,
                industry_type=cam_data["industry_type"],
                camera_type=cam_data["camera_type"],
                environment=cam_data["environment"],
                resolution=cam_data["resolution"],
                brand=cam_data["brand"],
                stream_url=cam_data["url"],
            )
            CameraSetup.objects.create(
                camera=camera,
                address_line_1=cam_data["address_line_1"],
                address_line_2=cam_data["address_line_2"],
                city=cam_data["city"],
                zip_code=cam_data["zip_code"],
                state_province=cam_data["state_province"],
                country=cam_data["country"],
                date=cam_data["date"],
                time=cam_data["time"],
                installation_notes=cam_data["installation_notes"],
            )


class PayPalCancelView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        paypal_subscription_id = request.GET.get("subscription_id")

        try:
            temp_data = TemporarySubscriptionData.objects.get(
                paypal_subscription_id=paypal_subscription_id
            )
        except TemporarySubscriptionData.DoesNotExist:
            return Response(
                {"error": "Subscription data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if self.request.user != temp_data.user:
            return Response(
                {"error": "You can only cancel your own subscription"},
                status=status.HTTP_403_FORBIDDEN,
            )
        temp_data.delete()
        return Response({"message": "Subscription cancelled successfully"})


class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionDetailView(generics.RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
