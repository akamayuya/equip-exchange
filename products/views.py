from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef, Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Company

from .forms import ProductCommentForm, ProductForm
from .geocoding import get_product_map_address, get_product_map_coordinates, populate_product_coordinates
from .models import Product, ProductComment, ProductImage


def _filter_products_by_query(queryset, query):
    if not query:
        return queryset

    return queryset.filter(
        Q(name__icontains=query)
        | Q(description__icontains=query)
        | Q(seller__username__icontains=query)
        | Q(seller__company__name__icontains=query)
        | Q(seller__company__address__icontains=query)
    )


def _company_address_error(user):
    company = getattr(user, "company", None)
    if company and company.address:
        return None
    return "商品を登録するには、先に法人情報へ会社所在地を登録してください。"


def product_list(request):
    Trade = apps.get_model("trades", "Trade")
    search_query = request.GET.get("q", "").strip()
    company_id = request.GET.get("company")
    selected_company = None
    products = Product.objects.select_related("seller", "seller__company").prefetch_related("images").annotate(
        has_active_trade=Exists(
            Trade.objects.filter(
                product=OuterRef("pk"),
                status__in=Trade.ACTIVE_STATUSES,
            )
        )
    )

    if company_id:
        selected_company = get_object_or_404(Company, pk=company_id)
        products = products.filter(seller__company=selected_company)

    products = _filter_products_by_query(
        products.order_by("is_sold", "-created_at"),
        search_query,
    )

    return render(
        request,
        "products/product_list.html",
        {
            "products": products,
            "search_query": search_query,
            "selected_company": selected_company,
        },
    )


@login_required
def product_create(request):
    company_address_error = _company_address_error(request.user)

    if request.method == "POST":

        form = ProductForm(request.POST)

        if company_address_error:
            form.add_error(None, company_address_error)

        if not company_address_error and form.is_valid():

            product = form.save(commit=False)
            product.seller = request.user

            populate_product_coordinates(product)

            product.save()

            # 画像
            images = request.FILES.getlist("images")
            for image in images:
                ProductImage.objects.create(product=product, image=image)

            return redirect("product_list")

    else:
        form = ProductForm()

    return render(
        request,
        "products/product_create.html",
        {"form": form, "company_address_error": company_address_error},
    )


def product_detail(request, pk):
    Trade = apps.get_model("trades", "Trade")
    product = get_object_or_404(Product.objects.select_related("seller", "seller__company"), pk=pk)

    existing_trade = None
    trade_messages = []

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next=/products/{product.pk}/")

        existing_trade = (
            product.trades.filter(
                status__in=Trade.ACTIVE_STATUSES,
                seller=request.user,
            ).first()
            or product.trades.filter(
                status__in=Trade.ACTIVE_STATUSES,
                buyer=request.user,
            ).first()
        )

        form_type = request.POST.get("form_type", "comment")
        if form_type == "trade_message" and existing_trade:
            body = request.POST.get("body", "").strip()
            if body:
                Message = apps.get_model("trades", "Message")
                Message.objects.create(
                    trade=existing_trade,
                    sender=request.user,
                    body=body,
                )
                messages.success(request, "取引チャットを送信しました。")
                return redirect("product_detail", pk=product.pk)
            messages.error(request, "メッセージを入力してください。")

        comment_form = ProductCommentForm(request.POST)
        if form_type == "comment" and comment_form.is_valid():
            comment = comment_form.save(commit=False)
            if comment.reply_to and comment.reply_to.product_id != product.pk:
                comment.reply_to = None
            comment.product = product
            comment.user = request.user
            comment.save()
            messages.success(request, "コメントを投稿しました。")
            return redirect("product_detail", pk=product.pk)
    else:
        comment_form = ProductCommentForm()

    if request.user.is_authenticated:
        existing_trade = (
            product.trades.filter(
                status__in=Trade.ACTIVE_STATUSES,
                seller=request.user,
            ).first()
            or product.trades.filter(
                status__in=Trade.ACTIVE_STATUSES,
                buyer=request.user,
            ).first()
        )
        if existing_trade:
            trade_messages = list(existing_trade.messages.select_related("sender"))

    comments = product.comments.select_related("user", "reply_to", "reply_to__user")

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "existing_trade": existing_trade,
            "trade_messages": trade_messages,
            "comments": comments,
            "comment_form": comment_form,
        },
    )


@login_required
def product_edit(request, pk):

    product = get_object_or_404(Product, pk=pk)

    # 出品者以外は編集不可
    if product.seller != request.user:
        return redirect("product_list")

    company_address_error = _company_address_error(request.user)

    if request.method == "POST":

        form = ProductForm(request.POST, instance=product)

        if company_address_error:
            form.add_error(None, company_address_error)

        if not company_address_error and form.is_valid():
            # 変更を保存する前に緯度経度を再取得
            product = form.save(commit=False)

            populate_product_coordinates(product)

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
            "company_address_error": company_address_error,
        },
    )


@login_required
def product_delete(request, pk):

    product = get_object_or_404(Product, pk=pk)

    # 出品者のみ削除可能
    if product.seller != request.user:
        return redirect("product_list")

    # 取引中・売却済みの商品は削除不可
    if product.is_sold:
        messages.error(request, "取引中または売却済みの商品は削除できません。")
        return redirect("product_detail", pk=pk)

    if request.method == "POST":
        product.delete()
        return redirect("product_list")

    return render(request, "products/product_delete.html", {"product": product})


def product_map(request):
    search_query = request.GET.get("q", "").strip()

    products = _filter_products_by_query(
        Product.objects.select_related("seller", "seller__company").filter(is_sold=False).order_by("seller__company_id", "-created_at", "-id"),
        search_query,
    )

    address_cache = {}
    company_markers = {}

    for product in products:
        company = getattr(product.seller, "company", None)
        if not company:
            continue

        map_address = get_product_map_address(product)
        if not map_address:
            continue

        coordinates = address_cache.get(map_address)
        if coordinates is None:
            coordinates = get_product_map_coordinates(product)
            address_cache[map_address] = coordinates

        if not coordinates:
            continue

        latitude, longitude = coordinates
        marker = company_markers.setdefault(
            company.pk,
            {
                "company_id": company.pk,
                "company_name": company.name or product.seller.username,
                "address": map_address,
                "latitude": latitude,
                "longitude": longitude,
                "product_count": 0,
                "latest_product_name": product.name,
            },
        )
        marker["product_count"] += 1

    map_companies = list(company_markers.values())

    return render(
        request,
        "products/product_map.html",
        {
            "map_companies": map_companies,
            "search_query": search_query,
        },
    )
