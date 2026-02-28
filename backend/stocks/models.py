from django.contrib.postgres.indexes import GinIndex
from django.db import models


class StockMaster(models.Model):
    class Market(models.TextChoices):
        KOSPI = "KOSPI", "KOSPI"
        KOSDAQ = "KOSDAQ", "KOSDAQ"
        KONEX = "KONEX", "KONEX"

    class SecurityType(models.TextChoices):
        COMMON_STOCK = "COMMON_STOCK", "COMMON_STOCK"
        ETN = "ETN", "ETN"
        ETN_LOSS_LIMIT = "ETN_LOSS_LIMIT", "ETN_LOSS_LIMIT"
        GOLD_SPOT = "GOLD_SPOT", "GOLD_SPOT"
        ETN_VOLATILITY = "ETN_VOLATILITY", "ETN_VOLATILITY"
        INFRA_FUND = "INFRA_FUND", "INFRA_FUND"
        ELW = "ELW", "ELW"
        MUTUAL_FUND = "MUTUAL_FUND", "MUTUAL_FUND"
        WARRANT = "WARRANT", "WARRANT"
        REIT = "REIT", "REIT"
        WARRANT_CERT = "WARRANT_CERT", "WARRANT_CERT"
        ETF = "ETF", "ETF"
        HIGH_YIELD_FUND = "HIGH_YIELD_FUND", "HIGH_YIELD_FUND"

    code = models.CharField(max_length=12, primary_key=True)
    name_kr = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120, null=True, blank=True)
    market = models.CharField(max_length=16, choices=Market.choices)
    security_type = models.CharField(
        max_length=24,
        choices=SecurityType.choices,
        default=SecurityType.COMMON_STOCK,
    )
    mrkt_tp_raw = models.CharField(max_length=8, null=True, blank=True)
    market_code_raw = models.CharField(max_length=8, null=True, blank=True)
    category_l1 = models.CharField(max_length=64, null=True, blank=True)
    category_l2 = models.CharField(max_length=64, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    listed_date = models.DateField(null=True, blank=True)
    delisted_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stock_master"
        indexes = [
            models.Index(fields=["market"], name="idx_stock_master_market"),
            models.Index(fields=["security_type"], name="idx_stock_master_security_type"),
            models.Index(fields=["category_l1"], name="idx_stock_master_category_l1"),
            models.Index(fields=["is_active"], name="idx_stock_master_is_active"),
            models.Index(fields=["updated_at"], name="idx_stock_master_updated_at"),
            models.Index(
                fields=["market", "category_l1"],
                name="idx_stock_master_market_category_l1",
            ),
            GinIndex(
                fields=["name_kr"],
                name="idx_stock_master_name_kr_trgm",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                fields=["name_en"],
                name="idx_stock_master_name_en_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ]
