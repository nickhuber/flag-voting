import json
import os
from django.core.management.base import BaseCommand, CommandError
from vote.models import Flag


class Command(BaseCommand):
    help = "Import flags from a clone of https://github.com/hjnilsson/country-flags"

    def add_arguments(self, parser):
        parser.add_argument("path_to_repo", type=str)

    def handle(self, *args, **options):
        with open(os.path.join(options["path_to_repo"], "countries.json"), "r") as f:
            countries = json.load(f)
        for abbr, name in countries.items():
            with open(
                os.path.join(options["path_to_repo"], "svg", f"{abbr.lower()}.svg"), "r"
            ) as f:
                Flag.objects.create(name=name, svg=f.read())
            self.stdout.write(self.style.SUCCESS(f'Imported "{name}"'))
