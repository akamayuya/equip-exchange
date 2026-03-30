from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

admin.site.site_header = "Equip Exchange 管理画面"
admin.site.site_title = "Equip Exchange 管理"
admin.site.index_title = "サイト管理"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="product_list", permanent=False)),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("products/", include("products.urls")),
    path("trades/", include("trades.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
