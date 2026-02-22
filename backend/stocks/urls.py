from django.urls import path

from .views import StockDetailView, StockListView, StockStatsView

urlpatterns = [
    path("stocks", StockListView.as_view(), name="stock-list"),
    path("stocks/stats", StockStatsView.as_view(), name="stock-stats"),
    path("stocks/<str:code>", StockDetailView.as_view(), name="stock-detail"),
]
