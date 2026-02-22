from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("api.urls")),
    path("api/", include("stocks.urls")),
    path("api/internal/", include("stocks.internal_urls")),
]
