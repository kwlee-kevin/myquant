import hmac
import os

from django.db import transaction
from django.db.models import Count
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StockMaster
from .serializers import (
    StockDetailSerializer,
    StockListSerializer,
    UpsertRequestSerializer,
)


class StockListView(APIView):
    allowed_ordering = {
        "code",
        "-code",
        "name_kr",
        "-name_kr",
        "updated_at",
        "-updated_at",
    }

    def get(self, request):
        op = request.query_params.get("op", "and")
        if op not in {"and", "or"}:
            return Response({"detail": "Invalid op"}, status=status.HTTP_400_BAD_REQUEST)

        ordering = request.query_params.get("ordering", "code")
        if ordering not in self.allowed_ordering:
            return Response({"detail": "Invalid ordering"}, status=status.HTTP_400_BAD_REQUEST)

        page_raw = request.query_params.get("page", "1")
        page_size_raw = request.query_params.get("page_size", "20")
        try:
            page = int(page_raw)
            page_size = int(page_size_raw)
        except ValueError:
            return Response({"detail": "Invalid page or page_size"}, status=status.HTTP_400_BAD_REQUEST)

        if page < 1 or page_size < 1 or page_size > 100:
            return Response({"detail": "Invalid page or page_size"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = StockMaster.objects.only(
            "code",
            "name_kr",
            "name_en",
            "market",
            "category_l1",
            "category_l2",
            "is_active",
            "updated_at",
        )

        keywords = request.query_params.get("keywords", "").strip()
        tokens = [token for token in keywords.split() if token]
        if tokens:
            if op == "and":
                keyword_filter = Q()
                for token in tokens:
                    token_filter = (
                        Q(code__icontains=token)
                        | Q(name_kr__icontains=token)
                        | Q(name_en__icontains=token)
                    )
                    keyword_filter &= token_filter
            else:
                keyword_filter = Q()
                for token in tokens:
                    token_filter = (
                        Q(code__icontains=token)
                        | Q(name_kr__icontains=token)
                        | Q(name_en__icontains=token)
                    )
                    keyword_filter |= token_filter
            queryset = queryset.filter(keyword_filter)

        categories = [value for value in request.query_params.getlist("categories") if value]
        if categories:
            queryset = queryset.filter(
                Q(category_l1__in=categories) | Q(category_l2__in=categories)
            )

        markets = [value for value in request.query_params.getlist("markets") if value]
        if markets:
            queryset = queryset.filter(market__in=markets)

        if ordering in {"code", "-code"}:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by(ordering, "code")
        count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        serializer = StockListSerializer(queryset[start:end], many=True)

        return Response(
            {
                "count": count,
                "page": page,
                "page_size": page_size,
                "results": serializer.data,
            }
        )


class StockDetailView(APIView):
    def get(self, request, code):
        stock = get_object_or_404(StockMaster, code=code)
        serializer = StockDetailSerializer(stock)
        return Response(serializer.data)


class StockStatsView(APIView):
    def get(self, request):
        by_market_rows = (
            StockMaster.objects.values("market")
            .annotate(count=Count("code"))
            .order_by("market")
        )
        by_market = {row["market"]: row["count"] for row in by_market_rows}

        top_category_l1 = list(
            StockMaster.objects.exclude(category_l1__isnull=True)
            .exclude(category_l1="")
            .values("category_l1")
            .annotate(count=Count("code"))
            .order_by("-count", "category_l1")[:20]
        )

        return Response(
            {
                "by_market": by_market,
                "top_category_l1": top_category_l1,
            }
        )


class InternalStocksUpsertView(APIView):
    @staticmethod
    def _is_authorized(request) -> bool:
        provided_key = request.headers.get("X-Bridge-Key", "")
        expected_key = os.getenv("BRIDGE_API_KEY", "")
        if not provided_key or not expected_key:
            return False
        return hmac.compare_digest(provided_key, expected_key)

    def post(self, request):
        if not self._is_authorized(request):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = UpsertRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items = serializer.validated_data["items"]

        inserted = 0
        updated = 0
        unchanged = 0

        with transaction.atomic():
            for item in items:
                code = item["code"].upper()
                defaults = {key: value for key, value in item.items() if key != "code"}
                stock = StockMaster.objects.filter(code=code).first()

                if stock is None:
                    StockMaster.objects.create(code=code, **defaults)
                    inserted += 1
                else:
                    changed = any(getattr(stock, key) != value for key, value in defaults.items())
                    if changed:
                        for key, value in defaults.items():
                            setattr(stock, key, value)
                        stock.save()
                        updated += 1
                    else:
                        unchanged += 1

        return Response(
            {
                "received": len(items),
                "inserted": inserted,
                "updated": updated,
                "unchanged": unchanged,
            }
        )
