from django.shortcuts import redirect, render

from .forms import ProductForm
from .models import Product


def product_list(request):
    products = Product.objects.all()
    return render(request, "products/product_list.html", {"products": products})


def product_create(request):

    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()

            return redirect("product_list")

    else:
        form = ProductForm()

    return render(request, "products/product_create.html", {"form": form})
