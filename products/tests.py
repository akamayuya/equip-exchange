from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

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


class ProductMapCompanyGroupingTests(TestCase):
	def setUp(self):
		self.company = Company.objects.create(
			name="法人A",
			corporate_number="3000000000200",
			address="東京都千代田区1-2-3",
			is_verified=True,
		)
		self.other_company = Company.objects.create(
			name="法人B",
			corporate_number="3000000000201",
			address="大阪府大阪市1-2-3",
			is_verified=True,
		)
		self.user = User.objects.create_user(username="seller-company-a", password="pass12345", company=self.company)
		self.other_user = User.objects.create_user(username="seller-company-b", password="pass12345", company=self.other_company)

		Product.objects.create(name="商品A-1", description="説明", price=1000, condition="A", seller=self.user)
		Product.objects.create(name="商品A-2", description="説明", price=2000, condition="B", seller=self.user)
		Product.objects.create(name="商品B-1", description="説明", price=3000, condition="C", seller=self.other_user)

	def test_product_list_filters_by_company(self):
		response = self.client.get(reverse("product_list"), {"company": self.company.pk})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["selected_company"], self.company)
		self.assertEqual(list(response.context["products"].values_list("name", flat=True)), ["商品A-2", "商品A-1"])

	def test_product_map_groups_products_by_company(self):
		with patch("products.views.get_product_map_coordinates") as mocked_coordinates:
			mocked_coordinates.side_effect = [(35.0, 139.0), (36.0, 140.0)]
			response = self.client.get(reverse("product_map"))

		self.assertEqual(response.status_code, 200)
		map_companies = response.context["map_companies"]
		self.assertEqual(len(map_companies), 2)

		company_marker = next(item for item in map_companies if item["company_id"] == self.company.pk)
		self.assertEqual(company_marker["company_name"], "法人A")
		self.assertEqual(company_marker["product_count"], 2)
		self.assertEqual(company_marker["latest_product_name"], "商品A-2")
