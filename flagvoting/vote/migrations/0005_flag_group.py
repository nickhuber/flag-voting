# Generated by Django 3.1 on 2020-09-05 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vote", "0004_flag_trueskill_rating"),
    ]

    operations = [
        migrations.AddField(
            model_name="flag",
            name="group",
            field=models.CharField(
                choices=[("COUNTRY", "Country"), ("STATE", "State")],
                db_index=True,
                default="COUNTRY",
                max_length=7,
            ),
        ),
    ]
