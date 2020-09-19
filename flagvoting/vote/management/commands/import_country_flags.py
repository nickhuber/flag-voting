import os
from django.core.management.base import BaseCommand, CommandError
from vote.models import Flag, FlagGroup


class Command(BaseCommand):
    help = "Import some flags"

    def add_arguments(self, parser):
        parser.add_argument("path_to_flags", type=str)

    def handle(self, *args, **options):
        for country in os.listdir(options["path_to_flags"]):
            name = f"{country[:-4]}"
            with open(os.path.join(options["path_to_flags"], country), "r") as f:
                if not Flag.objects.filter(name=name).exists():
                    flag = Flag(name=name, svg=f.read(), group=FlagGroup.COUNTRY)
                    flag.clean()
                    flag.save()
                    self.stdout.write(self.style.SUCCESS(f'Imported "{name}"'))
                else:
                    self.stdout.write(f'"{name}" already exists')
