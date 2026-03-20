from django import forms

from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "condition",
            # 追加: 郵便番号・都道府県・市区町村・町名・番地・建物名
            "postal_code",
            "prefecture",
            "city",
            "town",
            "block",
            "address_line",
            # 既存の簡易表示用 location は残す（任意）
            "location",
        ]
        labels = {
            "name": "商品名",
            "description": "説明",
            "price": "価格（円）",
            "condition": "状態",
            "postal_code": "郵便番号",
            "prefecture": "都道府県",
            "city": "市区町村",
            "town": "町名",
            "block": "丁目・番地・号",
            "address_line": "建物名・部屋番号（任意）",
            "location": "表示用地域（任意）",
        }
        widgets = {
            "postal_code": forms.TextInput(attrs={"placeholder": "例: 230-0076"}),
            "prefecture": forms.TextInput(
                attrs={"placeholder": "例: 神奈川県（「県」まで入力）"}
            ),
            "city": forms.TextInput(attrs={"placeholder": "例: 横浜市磯子区"}),
            "town": forms.TextInput(attrs={"placeholder": "例: 馬場"}),
            "block": forms.TextInput(attrs={"placeholder": "例: 1-7-19"}),
            "address_line": forms.TextInput(
                attrs={"placeholder": "例: 202（任意、ジオコーディングには含めない）"}
            ),
            "location": forms.TextInput(attrs={"placeholder": "例: 神奈川県"}),
        }
