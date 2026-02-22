from django.urls import path

from .views import InternalStocksUpsertView

urlpatterns = [
    path("stocks:upsert", InternalStocksUpsertView.as_view(), name="stocks-upsert"),
]
