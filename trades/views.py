from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Message, Trade


@login_required
def trade_create(request, product_pk):
    Product = apps.get_model("products", "Product")
    product = get_object_or_404(Product, pk=product_pk)

    # 自分の商品は購入不可
    if product.seller == request.user:
        return redirect("product_detail", pk=product_pk)

    if product.is_sold:
        latest_trade = product.trades.order_by("-created_at").first()
        if latest_trade and request.user in [latest_trade.buyer, latest_trade.seller]:
            return redirect("trade_detail", pk=latest_trade.pk)
        return redirect("product_detail", pk=product_pk)

    # 既に取引中の場合はスキップ
    existing = Trade.objects.filter(
        product=product, status__in=["pending", "paid", "shipped"]
    ).first()
    if existing:
        return redirect("trade_detail", pk=existing.pk)

    if request.method == "POST":
        trade = Trade.objects.create(
            product=product,
            buyer=request.user,
            seller=product.seller,
            price=product.price,
        )
        product.is_sold = True
        product.save(update_fields=["is_sold"])
        return redirect("product_detail", pk=product.pk)

    return render(request, "trades/trade_confirm.html", {"product": product})


@login_required
def trade_detail(request, pk):
    trade = get_object_or_404(Trade, pk=pk)

    # 購入者または出品者のみ閲覧可
    if request.user not in [trade.buyer, trade.seller]:
        return redirect("product_list")

    return render(request, "trades/trade_detail.html", {"trade": trade})


@login_required
def trade_update_status(request, pk):
    trade = get_object_or_404(Trade, pk=pk)

    if request.method == "POST":
        new_status = request.POST.get("status")
        allowed = []

        # 購入者は支払い済みに変更可
        if request.user == trade.buyer and trade.status == "pending":
            allowed = ["paid"]
        # 出品者は支払い確認後に発送済みに変更可
        elif request.user == trade.seller and trade.status == "paid":
            allowed = ["shipped"]
        # 購入者は「取引完了」に変更可
        elif request.user == trade.buyer and trade.status == "shipped":
            allowed = ["completed"]

        if new_status in allowed:
            trade.status = new_status
            trade.save()

    return redirect("trade_detail", pk=pk)


@login_required
def chat(request, pk):
    trade = get_object_or_404(Trade, pk=pk)

    # 購入者または出品者のみ閲覧可
    if request.user not in [trade.buyer, trade.seller]:
        return redirect("product_list")

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            Message.objects.create(
                trade=trade,
                sender=request.user,
                body=body,
            )
        return redirect("chat", pk=pk)

    messages = trade.messages.select_related("sender").all()
    return render(
        request,
        "trades/chat.html",
        {
            "trade": trade,
            "messages": messages,
        },
    )


@login_required
def chat_messages_api(request, pk):
    """5秒ポーリング用API: 最新メッセージをJSONで返す"""
    trade = get_object_or_404(Trade, pk=pk)

    if request.user not in [trade.buyer, trade.seller]:
        return JsonResponse({"error": "forbidden"}, status=403)

    # after パラメータ以降のメッセージのみ返す
    after_id = request.GET.get("after", 0)
    messages = trade.messages.filter(id__gt=after_id).select_related("sender").values(
        "id", "sender__username", "body", "created_at"
    )

    data = [
        {
            "id": m["id"],
            "sender": m["sender__username"],
            "body": m["body"],
            "created_at": m["created_at"].strftime("%Y/%m/%d %H:%M"),
        }
        for m in messages
    ]
    return JsonResponse({"messages": data})
