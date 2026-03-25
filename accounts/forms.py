from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class LoginForm(forms.Form):
    username = forms.CharField(label="ニックネーム", max_length=150)
    password = forms.CharField(label="パスワード", widget=forms.PasswordInput)


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
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.company_name = self.cleaned_data["company_name"]
        user.corporate_number = self.cleaned_data["corporate_number"]
        user.address = self.cleaned_data["address"]
        user.is_verified = False
        if commit:
            user.save()
        return user