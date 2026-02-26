from rest_framework import serializers

from .models import StockMaster


class StockListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMaster
        fields = [
            "code",
            "name_kr",
            "name_en",
            "market",
            "category_l1",
            "category_l2",
            "is_active",
            "updated_at",
        ]


class StockDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMaster
        fields = [
            "code",
            "name_kr",
            "name_en",
            "market",
            "category_l1",
            "category_l2",
            "is_active",
            "listed_date",
            "delisted_date",
            "created_at",
            "updated_at",
        ]


class UpsertItemSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=12)
    name_kr = serializers.CharField(max_length=120)
    name_en = serializers.CharField(
        max_length=120, allow_null=True, required=False, allow_blank=True
    )
    market = serializers.CharField(max_length=16)
    category_l1 = serializers.CharField(
        max_length=64, allow_null=True, required=False, allow_blank=True
    )
    category_l2 = serializers.CharField(
        max_length=64, allow_null=True, required=False, allow_blank=True
    )
    is_active = serializers.BooleanField(required=False, default=True)
    listed_date = serializers.DateField(required=False, allow_null=True)
    delisted_date = serializers.DateField(required=False, allow_null=True)


class UpsertRequestSerializer(serializers.Serializer):
    items = UpsertItemSerializer(many=True)
