from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, PaymentMethodForm, SignUpForm
from .models import PaymentMethod, User


def signup(request):
    if request.user.is_authenticated:
        return redirect("product_list")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error("corporate_number", "この法人番号は既に登録されています。")
            else:
                messages.success(request, "登録が完了しました。管理者の承認後にログインできます。")
                return redirect("login")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("product_list")

    next_url = request.GET.get("next") or request.POST.get("next") or settings.LOGIN_REDIRECT_URL

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(next_url)

            pending_user = User.objects.filter(username=username).first()
            company = pending_user.company if pending_user else None
            is_pending = pending_user and (company is None or not company.is_verified)
            if pending_user and pending_user.check_password(password) and is_pending:
                messages.error(request, "アカウントは審査中です。承認後にログインできます。")
            else:
                messages.error(request, "ユーザー名またはパスワードが正しくありません。")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form, "next": next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "ログアウトしました。")
    return redirect("login")

@login_required
def mypage(request):
    user = request.user
    company = user.company
    # 自分の出品
    my_products = user.products.all().order_by("-created_at")
    # 自分の購入取引
    my_purchases = user.purchases.select_related("product", "seller").order_by("-created_at")
    # 自分の販売取引
    my_sales = user.sales.select_related("product", "buyer").order_by("-created_at")
    payment_methods = user.payment_methods.all()

    return render(request, "accounts/mypage.html", {
        "my_products": my_products,
        "my_purchases": my_purchases,
        "my_sales": my_sales,
        "payment_methods": payment_methods,
        "company": company,
        "company_is_verified": company.is_verified if company else False,
    })


@login_required
def payment_method_create(request):
    if request.method == "POST":
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, "支払い方法を登録しました。")
            return redirect("mypage")
    else:
        form = PaymentMethodForm()

    return render(request, "accounts/payment_method_form.html", {"form": form})


@login_required
def payment_method_set_default(request, pk):
    payment_method = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
    request.user.payment_methods.update(is_default=False)
    payment_method.is_default = True
    payment_method.save(update_fields=["is_default"])
    messages.success(request, "デフォルトカードを更新しました。")
    return redirect("mypage")
