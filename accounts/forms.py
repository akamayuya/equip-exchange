import secrets
import unicodedata

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import Company, PaymentMethod, User


class LoginForm(forms.Form):
    username = forms.CharField(label="ニックネーム", max_length=150)
    password = forms.CharField(label="パスワード", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "ニックネーム"})
        self.fields["password"].widget.attrs.update({"class": "form-control", "placeholder": "パスワード"})


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="メールアドレス", required=True)
    company_name = forms.CharField(label="会社名", max_length=255)
    corporate_number = forms.CharField(label="法人番号", max_length=50)
    address = forms.CharField(label="所在地", max_length=255)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "company_name",
            "corporate_number",
            "address",
        )
        labels = {
            "username": "ニックネーム",
        }
        help_texts = {
            "username": "取引画面や商品ページなど、外部に表示される名前です。",
        }

    def save(self, commit=True):
        with transaction.atomic():
            company = Company.objects.create(
                name=self.cleaned_data["company_name"],
                corporate_number=self.cleaned_data["corporate_number"],
                address=self.cleaned_data["address"],
                is_verified=False,
            )

            user = super().save(commit=False)
            user.email = self.cleaned_data["email"]
            user.company = company
            user.is_company_admin = True
            if commit:
                user.save()
        return user

    def clean_company_name(self):
        return self.cleaned_data["company_name"].strip()

    def clean_corporate_number(self):
        corporate_number = unicodedata.normalize("NFKC", self.cleaned_data["corporate_number"]).strip()
        if Company.objects.filter(corporate_number=corporate_number).exists():
            raise forms.ValidationError("この法人番号は既に登録されています。")
        return corporate_number

    def clean_address(self):
        return self.cleaned_data["address"].strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_placeholders = {
            "username": "公開されるニックネーム",
            "email": "メールアドレス",
            "company_name": "会社名",
            "corporate_number": "法人番号",
            "address": "会社所在地",
            "password1": "パスワード",
            "password2": "確認用パスワード",
        }
        for name, field in self.fields.items():
            css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            field.widget.attrs.setdefault("class", css_class)
            if name in field_placeholders and css_class == "form-control":
                field.widget.attrs.setdefault("placeholder", field_placeholders[name])


class PaymentMethodForm(forms.Form):
    cardholder_name = forms.CharField(label="カード名義", max_length=255)
    brand = forms.ChoiceField(label="カードブランド", choices=PaymentMethod.BRAND_CHOICES)
    card_number = forms.CharField(
        label="カード番号",
        max_length=19,
        widget=forms.TextInput(attrs={"placeholder": "4111 1111 1111 1111"}),
        help_text="カード番号は保存されず、下4桁のみを保持します。",
    )
    exp_month = forms.IntegerField(label="有効期限(月)", min_value=1, max_value=12)
    exp_year = forms.IntegerField(label="有効期限(年)", min_value=2026, max_value=2100)
    set_as_default = forms.BooleanField(label="デフォルトカードにする", required=False, initial=True)

    def clean_card_number(self):
        number = "".join(filter(str.isdigit, self.cleaned_data["card_number"]))
        if len(number) < 12 or len(number) > 19:
            raise forms.ValidationError("カード番号の形式が正しくありません。")
        return number

    def save(self, user):
        set_as_default = self.cleaned_data["set_as_default"]
        has_existing = user.payment_methods.exists()

        if set_as_default:
            user.payment_methods.update(is_default=False)

        return PaymentMethod.objects.create(
            user=user,
            cardholder_name=self.cleaned_data["cardholder_name"],
            brand=self.cleaned_data["brand"],
            last4=self.cleaned_data["card_number"][-4:],
            exp_month=self.cleaned_data["exp_month"],
            exp_year=self.cleaned_data["exp_year"],
            token=secrets.token_hex(24),
            is_default=set_as_default or not has_existing,
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            field.widget.attrs.setdefault("class", css_class)
        self.fields["cardholder_name"].widget.attrs.setdefault("placeholder", "例: YAMADA TARO")
        self.fields["exp_month"].widget.attrs.setdefault("placeholder", "例: 12")
        self.fields["exp_year"].widget.attrs.setdefault("placeholder", "例: 2028")