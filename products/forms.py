from django import forms

from .models import Product, ProductComment


class ProductForm(forms.ModelForm):

    ADDRESS_FIELDS = ("postal_code", "prefecture", "city", "town", "block", "address_line", "location")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "condition",
        ]
        labels = {
            "name": "商品名",
            "description": "説明",
            "price": "価格（円）",
            "condition": "状態",
        }

    def save(self, commit=True):
        product = super().save(commit=False)
        product.location = ""
        product.postal_code = None
        product.prefecture = None
        product.city = None
        product.town = None
        product.block = None
        product.address_line = None
        if commit:
            product.save()
        return product


class ProductCommentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["body"].widget.attrs.setdefault("class", "form-control")

    class Meta:
        model = ProductComment
        fields = ["body", "reply_to"]
        labels = {
            "body": "コメント",
        }
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "商品について質問やコメントを入力してください",
                }
            ),
            "reply_to": forms.HiddenInput(),
        }
