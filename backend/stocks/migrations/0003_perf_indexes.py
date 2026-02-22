from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stocks", "0002_create_stock_master"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="stockmaster",
            name="idx_stock_master_updated_at_desc",
        ),
        migrations.AddIndex(
            model_name="stockmaster",
            index=models.Index(fields=["updated_at"], name="idx_stock_master_updated_at"),
        ),
        migrations.AddIndex(
            model_name="stockmaster",
            index=models.Index(
                fields=["market", "category_l1"],
                name="idx_stock_master_market_category_l1",
            ),
        ),
    ]
