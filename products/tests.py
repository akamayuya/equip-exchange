from django.test import TestCase
from django.urls import reverse

from accounts.models import Company, User

from .forms import ProductForm
from .geocoding import get_product_map_address
from .models import Product


class ProductFormTests(TestCase):
	def test_product_form_excludes_address_fields(self):
		form = ProductForm()

		self.assertEqual(list(form.fields.keys()), ["name", "description", "price", "condition"])


class ProductAddressConsistencyTests(TestCase):
	def setUp(self):
		self.company = Company.objects.create(
			name="法人A",
			corporate_number="3000000000100",
			address="東京都港区1-2-3",
			is_verified=True,
		)
		self.user = User.objects.create_user(
			username="seller-a",
			password="pass12345",
			company=self.company,
		)

	def test_map_address_uses_company_address_only(self):
		product = Product.objects.create(
			name="テスト商品",
			description="説明",
			price=1000,
			condition="A",
			location="旧住所",
			prefecture="神奈川県",
			city="横浜市",
			town="中区",
			block="1-2-3",
			seller=self.user,
		)

		self.assertEqual(get_product_map_address(product), "東京都港区1-2-3")

	def test_product_create_requires_company_address(self):
		self.company.address = ""
		self.company.save(update_fields=["address"])
		self.client.force_login(self.user)

		response = self.client.post(
			reverse("product_create"),
			{
				"name": "新商品",
				"description": "説明",
				"price": 1200,
				"condition": "A",
			},
		)

		self.assertContains(response, "商品を登録するには、先に法人情報へ会社所在地を登録してください。")
		self.assertFalse(Product.objects.filter(name="新商品").exists())
