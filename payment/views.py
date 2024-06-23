from itertools import product
from locale import currency
from re import sub
from typing import Any, Dict
from django.shortcuts import redirect
from rest_framework import generics, status
from rest_framework import generics, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from camera_integration.models import Camera, CameraSetup
from user_authentication.models import User
from .models import (
    Card,
    Plan,
    Subscription,
    TemporarySubscriptionData,
    Transaction,
)
from .serializers import (
    PlanSerializer,
    SubscriptionInSerializer,
    SubscriptionOutSerializer,
    TransactionSerializer,
)
from .paypal_client import PayPalClient
from django.utils import timezone


class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class SubscriptionView(generics.GenericAPIView):
    serializer_class = SubscriptionInSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user = validated_data["user"]
        plan = validated_data["plan"]
        system_setup_data = validated_data["system_setup_data"]
        card = validated_data.get("card")
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
                quantity=quantity,
                paypal_subscription_id=paypal_subscription_id,
            )
            return redirect(approval_url)
        else:
            return Response({"message": "Subscription activated successfully"})

    def _process_payment(
        self,
        user: User,
        plan: Plan,
        system_setup_data,
        card,
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
                    quantity,
                    payment_method,
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
        self,
        user,
        plan,
        card,
        start_date,
        end_date,
        quantity,
        payment_method,
        paypal_subscription_id,
    ):
        return Subscription.objects.create(
            user=user,
            plan=plan,
            card=card,
            payer_email=None,
            start_date=start_date,
            end_date=end_date,
            number_of_cameras=quantity,
            payment_method=payment_method,
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


class SubscriptionDetailView(generics.RetrieveAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionOutSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


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

        paypal_client = PayPalClient()
        try:
            subscription_details = paypal_client.get_subscription(
                paypal_subscription_id
            )
            payer_email = subscription_details["subscriber"]["email_address"]
            subscription = self._create_subscription(temp_data, payer_email)
            self._create_transaction(temp_data, subscription)
            self._handle_system_setup(temp_data)

        except Exception as e:
            return Response(
                {"error": f"Failed to create subscription: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        temp_data.delete()
        return Response({"message": "Subscription activated successfully"})

    def _create_subscription(self, temp_data, payer_email):
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
            payer_email=payer_email,
            number_of_cameras=temp_data.quantity,
            payment_method="paypal",
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
