from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stocks", "0003_perf_indexes"),
    ]

    operations = [
        migrations.AddField(
            model_name="stockmaster",
            name="market_code_raw",
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AddField(
            model_name="stockmaster",
            name="mrkt_tp_raw",
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AddField(
            model_name="stockmaster",
            name="security_type",
            field=models.CharField(
                choices=[
                    ("COMMON_STOCK", "COMMON_STOCK"),
                    ("ETN", "ETN"),
                    ("ETN_LOSS_LIMIT", "ETN_LOSS_LIMIT"),
                    ("GOLD_SPOT", "GOLD_SPOT"),
                    ("ETN_VOLATILITY", "ETN_VOLATILITY"),
                    ("INFRA_FUND", "INFRA_FUND"),
                    ("ELW", "ELW"),
                    ("MUTUAL_FUND", "MUTUAL_FUND"),
                    ("WARRANT", "WARRANT"),
                    ("REIT", "REIT"),
                    ("WARRANT_CERT", "WARRANT_CERT"),
                    ("ETF", "ETF"),
                    ("HIGH_YIELD_FUND", "HIGH_YIELD_FUND"),
                ],
                default="COMMON_STOCK",
                max_length=24,
            ),
        ),
        migrations.AlterField(
            model_name="stockmaster",
            name="market",
            field=models.CharField(
                choices=[("KOSPI", "KOSPI"), ("KOSDAQ", "KOSDAQ"), ("KONEX", "KONEX")],
                max_length=16,
            ),
        ),
        migrations.AddIndex(
            model_name="stockmaster",
            index=models.Index(fields=["security_type"], name="idx_stock_master_security_type"),
        ),
    ]
