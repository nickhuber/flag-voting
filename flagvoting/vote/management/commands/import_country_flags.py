import json
import os
from django.core.management.base import BaseCommand, CommandError
from vote.models import Flag, FlagGroup

# These flags are copies of other flags
excluded_abbrs = {
    "bq",  # Caribbean Netherlands
    "um",  # US Minor Outlying Islands
    "hm",  # Heard Island and McDonald Islands, same as Australia
    # These are all france
    "gp",  # Guadeloupe
    "mf",  # Saint Martin
    "pm",  # Saint Pierre and Miquelon
    "re",  # Réunion
    "yt",  # Mayotte
    "gf",  # French Guiana
    # These are Norway
    "bv",  # Bouvet Island
    "sj",  # Svalbard and Jan Mayen Islands
    # These have the UK flag
    "gb-nir",  # Northern Ireland doesn't have its own flag I guess
    "sh",  # Saint Helena, Ascension and Tristan da Cunha
}


class Command(BaseCommand):
    help = "Import flags from a clone of https://github.com/hjnilsson/country-flags"

    def add_arguments(self, parser):
        parser.add_argument("path_to_repo", type=str)

    def handle(self, *args, **options):
        with open(os.path.join(options["path_to_repo"], "countries.json"), "r") as f:
            countries = json.load(f)
        for abbr, name in countries.items():
            if abbr in excluded_abbrs:
                continue
            with open(
                os.path.join(options["path_to_repo"], "svg", f"{abbr.lower()}.svg"), "r"
            ) as f:
                flag = Flag(name=name, svg=f.read(), group=FlagGroup.COUNTRY)
                flag.clean()
                flag.save()
            self.stdout.write(self.style.SUCCESS(f'Imported "{name}"'))
