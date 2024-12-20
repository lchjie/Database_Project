# Generated by Django 5.1.3 on 2024-11-30 19:17

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_item_menu"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="order",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterField(
            model_name="order",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to="core.student",
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="computing_id",
            field=models.CharField(
                max_length=6,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Computing ID must be exactly 6 alphanumeric characters",
                        regex="^[a-zA-Z0-9]{6}$",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="email",
            field=models.EmailField(editable=False, max_length=254, unique=True),
        ),
    ]
