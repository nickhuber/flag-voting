import os
from django.core.management.base import BaseCommand, CommandError
from vote.models import Flag, FlagGroup


class Command(BaseCommand):
    help = "Import some flags"

    def add_arguments(self, parser):
        parser.add_argument("path_to_flags", type=str)

    def handle(self, *args, **options):
        for country in os.listdir(options["path_to_flags"]):
            for state_flag in os.listdir(
                os.path.join(options["path_to_flags"], country)
            ):
                name = f"{state_flag[:-4]}, {country}"
                with open(
                    os.path.join(options["path_to_flags"], country, state_flag), "r"
                ) as f:
                    if not Flag.objects.filter(name=name).exists():
                        flag = Flag(name=name, svg=f.read(), group=FlagGroup.STATE)
                        flag.clean()
                        flag.save()
                        self.stdout.write(self.style.SUCCESS(f'Imported "{name}"'))
                    else:
                        
                        flag = Flag.objects.get(name=name)
                        svg = f.read()
                        if flag.svg != svg:
                            flag.svg = svg
                            flag.save() 
                            self.stdout.write(self.style.SUCCESS(f'"{name}" updated'))
                        else:
                            self.stdout.write(f'"{name}" unchanged')

