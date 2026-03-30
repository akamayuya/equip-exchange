from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from accounts.models import Company, PaymentMethod, User
from products.models import Product

from .models import Trade


class TradeCreateTests(TestCase):
	def setUp(self):
		self.seller_company = Company.objects.create(name="Seller Co", corporate_number="2000000000001", address="東京都", is_verified=True)
		self.buyer_company = Company.objects.create(name="Buyer Co", corporate_number="2000000000002", address="大阪府", is_verified=True)
		self.second_buyer_company = Company.objects.create(name="Buyer Co 2", corporate_number="2000000000003", address="福岡県", is_verified=True)

		self.seller = User.objects.create_user(username="seller", password="pass12345", company=self.seller_company)
		self.buyer = User.objects.create_user(username="buyer", password="pass12345", company=self.buyer_company)
		self.second_buyer = User.objects.create_user(username="buyer2", password="pass12345", company=self.second_buyer_company)

		self.product = Product.objects.create(
			name="テスト機材",
			description="説明",
			price=100000,
			condition="A",
			location="渋谷区",
			seller=self.seller,
		)

		self.payment_method = PaymentMethod.objects.create(
			user=self.buyer,
			cardholder_name="TARO YAMADA",
			brand="visa",
			last4="4242",
			exp_month=12,
			exp_year=2030,
			token="token-buyer",
			is_default=True,
		)
		self.second_payment_method = PaymentMethod.objects.create(
			user=self.second_buyer,
			cardholder_name="HANAKO YAMADA",
			brand="mastercard",
			last4="5454",
			exp_month=11,
			exp_year=2031,
			token="token-buyer-2",
			is_default=True,
		)

	def test_view_prevents_second_active_trade(self):
		self.client.force_login(self.buyer)
		first_response = self.client.post(
			reverse("trade_create", args=[self.product.pk]),
			{"payment_method": self.payment_method.pk},
		)

		self.assertEqual(first_response.status_code, 302)
		self.assertEqual(Trade.objects.filter(product=self.product, status__in=Trade.ACTIVE_STATUSES).count(), 1)

		self.client.force_login(self.second_buyer)
		second_response = self.client.post(
			reverse("trade_create", args=[self.product.pk]),
			{"payment_method": self.second_payment_method.pk},
		)

		self.assertEqual(second_response.status_code, 302)
		self.assertEqual(Trade.objects.filter(product=self.product, status__in=Trade.ACTIVE_STATUSES).count(), 1)

	def test_model_constraint_prevents_duplicate_active_trade(self):
		Trade.objects.create(product=self.product, buyer=self.buyer, seller=self.seller, price=100000, status="paid")

		with self.assertRaises(IntegrityError):
			Trade.objects.create(product=self.product, buyer=self.second_buyer, seller=self.seller, price=100000, status="paid")
