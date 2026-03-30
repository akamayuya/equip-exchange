from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.hashers import identify_hasher
from django.test import TestCase

from .admin import UserAdminCreationForm, UserAdminForm
from .forms import SignUpForm
from .models import Company


class SignUpFormTests(TestCase):
	def test_rejects_duplicate_corporate_number(self):
		Company.objects.create(name="既存法人", corporate_number="1234567890123", address="東京都")

		form = SignUpForm(
			data={
				"username": "new-user",
				"email": "new@example.com",
				"company_name": "新規法人",
				"corporate_number": "1234567890123",
				"address": "大阪府",
				"password1": "StrongPassword123!",
				"password2": "StrongPassword123!",
			}
		)

		self.assertFalse(form.is_valid())
		self.assertIn("corporate_number", form.errors)


class UserAdminFormTests(TestCase):
	def setUp(self):
		self.company = Company.objects.create(name="法人A", corporate_number="9999999999999", address="東京都")

	def test_admin_creation_form_hashes_password(self):
		form = UserAdminCreationForm(
			data={
				"username": "admin-created-user",
				"email": "admin-created@example.com",
				"company": self.company.pk,
				"is_company_admin": True,
				"password1": "StrongPassword123!",
				"password2": "StrongPassword123!",
			}
		)

		self.assertTrue(form.is_valid(), form.errors)
		user = form.save()

		self.assertTrue(user.check_password("StrongPassword123!"))
		self.assertNotEqual(user.password, "StrongPassword123!")
		identify_hasher(user.password)

	def test_admin_change_form_uses_read_only_password_field(self):
		user = self.company.users.create_user(username="member-user", password="StrongPassword123!")
		form = UserAdminForm(instance=user)

		self.assertIsInstance(form.fields["password"], ReadOnlyPasswordHashField)
