from django.contrib.postgres.indexes import GinIndex
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stocks", "0001_enable_pg_trgm"),
    ]

    operations = [
        migrations.CreateModel(
            name="StockMaster",
            fields=[
                ("code", models.CharField(max_length=12, primary_key=True, serialize=False)),
                ("name_kr", models.CharField(max_length=120)),
                ("name_en", models.CharField(blank=True, max_length=120, null=True)),
                ("market", models.CharField(max_length=16)),
                ("category_l1", models.CharField(blank=True, max_length=64, null=True)),
                ("category_l2", models.CharField(blank=True, max_length=64, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("listed_date", models.DateField(blank=True, null=True)),
                ("delisted_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "stock_master",
            },
        ),
        migrations.AddIndex(
            model_name="stockmaster",
            index=models.Index(fields=["market"], name="idx_stock_master_market"),
        ),
        migrations.AddIndex(
            model_name="stockmaster",
            index=models.Index(fields=["category_l1"], name="idx_stock_master_category_l1"),
        ),
        migrations.AddIndex(
            model_name="stockmaster",
            index=models.Index(fields=["is_active"], name="idx_stock_master_is_active"),
        ),
        migrations.AddIndex(
            model_name="stockmaster",
            index=models.Index(fields=["-updated_at"], name="idx_stock_master_updated_at_desc"),
        ),
        migrations.AddIndex(
            model_name="stockmaster",
            index=GinIndex(
                fields=["name_kr"],
                name="idx_stock_master_name_kr_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="stockmaster",
            index=GinIndex(
                fields=["name_en"],
                name="idx_stock_master_name_en_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
    ]
