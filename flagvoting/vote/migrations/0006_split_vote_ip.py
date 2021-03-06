# Generated by Django 3.1 on 2020-09-08 00:08

from django.db import migrations, models


def set_voted_ip(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Vote = apps.get_model("vote", "Vote")
    db_alias = schema_editor.connection.alias
    Vote.objects.using(db_alias).update(voter_voted_ip=models.F("voter_created_ip"))


class Migration(migrations.Migration):

    dependencies = [
        ("vote", "0005_flag_group"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="flag", options={"base_manager_name": "objects"},
        ),
        migrations.RenameField(
            model_name="vote", old_name="voter_ip", new_name="voter_created_ip",
        ),
        migrations.AddField(
            model_name="vote",
            name="voter_voted_ip",
            field=models.GenericIPAddressField(null=True),
        ),
        migrations.RunPython(set_voted_ip, migrations.RunPython.noop),
    ]
