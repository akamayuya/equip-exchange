import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Product, ProductImage


def product_list(request):
    products = Product.objects.all()
    return render(request, "products/product_list.html", {"products": products})


@login_required
def product_create(request):

    if request.method == "POST":

        form = ProductForm(request.POST)

        if form.is_valid():

            product = form.save(commit=False)
            product.seller = request.user

            # 修正: 建物名を含まない geocode_address() を使用する
            address = (
                product.geocode_address()
                if hasattr(product, "geocode_address")
                else product.location
            )

            # ★デバッグ: ターミナルで確認
            print(f"[GEOCODE] address送信値: '{address}'")

            # Nominatimから日本の住所に強い国土地理院APIへ変更
            url = "https://msearch.gsi.go.jp/address-search/AddressSearch"
            params = {"q": address}

            try:
                response = requests.get(url, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()
                # ★デバッグ: APIレスポンス確認
                print(f"[GEOCODE] APIレスポンス: {data}")
            except Exception as e:
                print(f"[GEOCODE] APIエラー: {e}")
                data = []

            if data and isinstance(data, list):
                # 国土地理院APIは coordinates に [longitude, latitude] の順で格納される
                coords = data[0].get("geometry", {}).get("coordinates")
                print(f"[GEOCODE] coords: {coords}")
                if coords and len(coords) == 2:
                    try:
                        product.longitude = float(coords[0])
                        product.latitude = float(coords[1])
                        print(
                            f"[GEOCODE] 保存する緯度経度: lat={product.latitude}, lng={product.longitude}"
                        )
                    except (TypeError, ValueError):
                        product.latitude = None
                        product.longitude = None
            else:
                print("[GEOCODE] データなし（空リスト）")

            product.save()

            # 画像
            images = request.FILES.getlist("images")
            for image in images:
                ProductImage.objects.create(product=product, image=image)

            return redirect("product_list")

    else:
        form = ProductForm()

    return render(request, "products/product_create.html", {"form": form})


def product_detail(request, pk):

    product = get_object_or_404(Product, pk=pk)

    return render(request, "products/product_detail.html", {"product": product})


@login_required
def product_edit(request, pk):

    product = get_object_or_404(Product, pk=pk)

    # 出品者以外は編集不可
    if product.seller != request.user:
        return redirect("product_list")

    if request.method == "POST":

        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            # 変更を保存する前に緯度経度を再取得
            product = form.save(commit=False)

            # 修正: 建物名を含まない geocode_address() を使用する
            address = (
                product.geocode_address()
                if hasattr(product, "geocode_address")
                else product.location
            )

            # ★デバッグ: ターミナルで確認
            print(f"[GEOCODE] address送信値: '{address}'")

            # Nominatimから日本の住所に強い国土地理院APIへ変更
            url = "https://msearch.gsi.go.jp/address-search/AddressSearch"
            params = {"q": address}

            try:
                response = requests.get(url, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()
                # ★デバッグ: APIレスポンス確認
                print(f"[GEOCODE] APIレスポンス: {data}")
            except Exception as e:
                print(f"[GEOCODE] APIエラー: {e}")
                data = []

            if data and isinstance(data, list):
                coords = data[0].get("geometry", {}).get("coordinates")
                print(f"[GEOCODE] coords: {coords}")
                if coords and len(coords) == 2:
                    try:
                        product.longitude = float(coords[0])
                        product.latitude = float(coords[1])
                        print(
                            f"[GEOCODE] 保存する緯度経度: lat={product.latitude}, lng={product.longitude}"
                        )
                    except (TypeError, ValueError):
                        product.latitude = None
                        product.longitude = None
            else:
                print("[GEOCODE] データなし（空リスト）")

            product.save()
            return redirect("product_detail", pk=product.pk)

    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "products/product_edit.html",
        {
            "form": form,
            "product": product,
        },
    )


@login_required
def product_delete(request, pk):

    product = get_object_or_404(Product, pk=pk)

    # 出品者のみ削除可能
    if product.seller != request.user:
        return redirect("product_list")

    if request.method == "POST":
        product.delete()
        return redirect("product_list")

    return render(request, "products/product_delete.html", {"product": product})


def product_map(request):

    products = Product.objects.filter(
        is_sold=False, latitude__isnull=False, longitude__isnull=False
    )

    return render(request, "products/product_map.html", {"products": products})
