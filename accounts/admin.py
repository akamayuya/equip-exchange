from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import AdminUserCreationForm, ReadOnlyPasswordHashField, UserChangeForm
from django.contrib.auth.models import Permission
from django.utils.html import format_html

from .models import Company, PaymentMethod, User

# admin.site.register(User)


class UserAdminForm(UserChangeForm):
    grant_all_permissions = forms.BooleanField(
        label="個別権限をすべて選択する",
        required=False,
        help_text="チェックすると、保存時に利用可能な個別権限をすべて付与します。",
    )
    revoke_all_permissions = forms.BooleanField(
        label="個別権限をすべて外す",
        required=False,
        help_text="チェックすると、保存時に個別権限をすべて解除します。",
    )

    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        total_permissions = Permission.objects.count()
        current_permissions = self.instance.user_permissions.count() if self.instance.pk else 0
        self.fields["grant_all_permissions"].initial = total_permissions > 0 and current_permissions == total_permissions
        self.fields["revoke_all_permissions"].initial = total_permissions > 0 and current_permissions == 0


class UserAdminCreationForm(AdminUserCreationForm):
    class Meta(AdminUserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "company", "is_company_admin")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("company_name_label", "corporate_number", "member_count", "is_verified", "verification_status", "created_at")
    list_editable = ("is_verified",)
    list_filter = ("is_verified",)
    search_fields = ("name", "corporate_number", "address")
    readonly_fields = ("member_summary", "created_at")
    fieldsets = (
        ("法人情報", {"fields": ("name", "corporate_number", "address", "is_verified")}),
        ("所属ユーザー", {"fields": ("member_summary",)}),
        ("記録", {"fields": ("created_at",)}),
    )
    actions = ("approve_companies", "unapprove_companies")

    @admin.display(description="法人名", ordering="name")
    def company_name_label(self, obj):
        return obj.name

    @admin.display(description="所属人数")
    def member_count(self, obj):
        return obj.users.count()

    @admin.display(description="所属ユーザー")
    def member_summary(self, obj):
        usernames = list(obj.users.order_by("username").values_list("username", flat=True))
        if not usernames:
            return "所属ユーザーなし"
        return " / ".join(usernames)

    @admin.display(description="審査状況", ordering="is_verified")
    def verification_status(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="display:inline-block;padding:0.18rem 0.55rem;border-radius:999px;background:#dcfce7;color:#166534;font-weight:700;">{}</span>',
                "承認済み",
            )
        return format_html(
            '<span style="display:inline-block;padding:0.18rem 0.55rem;border-radius:999px;background:#fef3c7;color:#92400e;font-weight:700;">{}</span>',
            "審査中",
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    @admin.action(description="選択した法人を承認する")
    def approve_companies(self, request, queryset):
        updated_count = 0
        for company in queryset:
            company.is_verified = True
            self.save_model(request, company, form=None, change=True)
            updated_count += 1
        self.message_user(request, f"{updated_count} 件の法人を承認しました。")

    @admin.action(description="選択した法人を審査中に戻す")
    def unapprove_companies(self, request, queryset):
        updated_count = 0
        for company in queryset:
            company.is_verified = False
            self.save_model(request, company, form=None, change=True)
            updated_count += 1
        self.message_user(request, f"{updated_count} 件の法人を審査中に戻しました。")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    form = UserAdminForm
    add_form = UserAdminCreationForm
    list_display = ("nickname_label", "email", "company", "company_admin_status", "company_verification_status")
    list_filter = ("is_company_admin", "company__is_verified")
    search_fields = ("username", "email", "company__name", "company__corporate_number")
    filter_horizontal = ("groups", "user_permissions")
    fieldsets = (
        ("基本情報", {"fields": ("username", "password", "email", "first_name", "last_name")}),
        ("所属情報", {"fields": ("company", "is_company_admin")}),
        ("権限", {"fields": ("is_active", "is_staff", "is_superuser", "grant_all_permissions", "revoke_all_permissions", "groups", "user_permissions")}),
        ("重要な日時", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            "基本情報",
            {
                "classes": ("wide",),
                "fields": ("username", "email", "first_name", "last_name", "company", "is_company_admin", "password1", "password2"),
            },
        ),
        (
            "権限",
            {
                "classes": ("wide",),
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            },
        ),
    )

    @admin.display(description="ニックネーム", ordering="username")
    def nickname_label(self, obj):
        return obj.username

    @admin.display(description="法人管理者", ordering="is_company_admin")
    def company_admin_status(self, obj):
        return "はい" if obj.is_company_admin else "いいえ"

    @admin.display(description="審査状況")
    def company_verification_status(self, obj):
        if obj.company:
            if obj.company.is_verified:
                return format_html(
                    '<span style="display:inline-block;padding:0.18rem 0.55rem;border-radius:999px;background:#dcfce7;color:#166534;font-weight:700;">{}</span>',
                    "承認済み",
                )
            return format_html(
                '<span style="display:inline-block;padding:0.18rem 0.55rem;border-radius:999px;background:#fef3c7;color:#92400e;font-weight:700;">{}</span>',
                "審査中",
            )
        return "未所属"

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if form.cleaned_data.get("grant_all_permissions"):
            form.instance.user_permissions.set(Permission.objects.all())
        elif form.cleaned_data.get("revoke_all_permissions"):
            form.instance.user_permissions.clear()


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("user", "brand", "last4", "expiry_label", "default_status")
    list_filter = ("brand", "is_default")
    search_fields = ("user__username", "user__company__name", "last4")

    @admin.display(description="有効期限")
    def expiry_label(self, obj):
        return f"{obj.exp_month:02d}/{obj.exp_year}"

    @admin.display(description="デフォルト")
    def default_status(self, obj):
        return "はい" if obj.is_default else "いいえ"
