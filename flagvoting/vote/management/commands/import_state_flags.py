import json
import os
from django.core.management.base import BaseCommand, CommandError
from vote.models import Flag, FlagGroup


STATES = {
    "ca/bc.svg": "British Columbia, Canada",
    "ca/ab.svg": "Alberta, Canada",
    "ca/sk.svg": "Saskatchewan, Canada",
    "ca/mb.svg": "Manitoba, Candada",
    "ca/on.svg": "Ontario, Canada",
    "ca/qc.svg": "Quebec, Canada",
    "ca/nb.svg": "New Brunswick, Canada",
    "ca/ns.svg": "Nova Scotia, Canada",
    "ca/pe.svg": "Prince Edward Island, Canada",
    "ca/nl.svg": "Newfoundland and Labrador, Canada",
    "ca/yt.svg": "Yukon, Canada",
    "ca/nt.svg": "Northwest Territories, Canada",
    "ca/nu.svg": "Nunavut, Canada",
    "us/al.svg": "Alabama, United States",
    "us/ak.svg": "Alaska, United States",
    "us/az.svg": "Arizona, United States",
    "us/ar.svg": "Arkansas, United States",
    "us/ca.svg": "California, United States",
    "us/co.svg": "Colorado, United States",
    "us/ct.svg": "Connecticut, United States",
    "us/de.svg": "Delaware, United States",
    "us/dc.svg": "District of Columbia, United States",
    "us/fl.svg": "Florida, United States",
    "us/ga.svg": "Georgia, United States",
    "us/hi.svg": "Hawaii, United States",
    "us/id.svg": "Idaho, United States",
    "us/il.svg": "Illinois, United States",
    "us/in.svg": "Indiana, United States",
    "us/ia.svg": "Iowa, United States",
    "us/ks.svg": "Kansas, United States",
    "us/ky.svg": "Kentucky, United States",
    "us/la.svg": "Louisiana, United States",
    "us/me.svg": "Maine, United States",
    "us/md.svg": "Maryland, United States",
    "us/ma.svg": "Massachusetts, United States",
    "us/mi.svg": "Michigan, United States",
    "us/mn.svg": "Minnesota, United States",
    "us/ms.svg": "Mississippi, United States",
    "us/mo.svg": "Missouri, United States",
    "us/mt.svg": "Montana, United States",
    "us/ne.svg": "Nebraska, United States",
    "us/nv.svg": "Nevada, United States",
    "us/nh.svg": "New Hampshire, United States",
    "us/nj.svg": "New Jersey, United States",
    "us/nm.svg": "New Mexico, United States",
    "us/ny.svg": "New York, United States",
    "us/nc.svg": "North Carolina, United States",
    "us/nd.svg": "North Dakota, United States",
    "us/oh.svg": "Ohio, United States",
    "us/ok.svg": "Oklahoma, United States",
    "us/or.svg": "Oregon, United States",
    "us/pa.svg": "Pennsylvania, United States",
    "us/ri.svg": "Rhode Island, United States",
    "us/sc.svg": "South Carolina, United States",
    "us/sd.svg": "South Dakota, United States",
    "us/tn.svg": "Tennessee, United States",
    "us/tx.svg": "Texas, United States",
    "us/ut.svg": "Utah, United States",
    "us/vt.svg": "Vermont, United States",
    "us/va.svg": "Virginia, United States",
    "us/wa.svg": "Washington, United States",
    "us/wv.svg": "West Virginia, United States",
    "us/wi.svg": "Wisconsin, United States",
    "us/wy.svg": "Wyoming, United States",
    "nl/dr.svg": "Drenthe, Netherlands",
    "nl/fl.svg": "Flevoland, Netherlands",
    "nl/fr.svg": "Friesland, Netherlands",
    "nl/ge.svg": "Gelderland, Netherlands",
    "nl/gr.svg": "Groningen, Netherlands",
    "nl/li.svg": "Limburg, Netherlands",
    "nl/nb.svg": "North Brabant, Netherlands",
    "nl/nh.svg": "North Holland, Netherlands",
    "nl/ov.svg": "Overijssel, Netherlands",
    "nl/zh.svg": "South Holland, Netherlands",
    "nl/ut.svg": "Utrecht, Netherlands",
    "nl/ze.svg": "Zeeland, Netherlands",
}


class Command(BaseCommand):
    help = "Import some flags from https://github.com/oxguy3/flags"

    def add_arguments(self, parser):
        parser.add_argument("path_to_repo", type=str)

    def handle(self, *args, **options):
        for path, name in STATES.items():
            with open(os.path.join(options["path_to_repo"], "svg", path), "r") as f:
                if not Flag.objects.filter(name=name).exists():
                    flag = Flag(name=name, svg=f.read(), group=FlagGroup.STATE)
                    flag.clean()
                    flag.save()
            self.stdout.write(self.style.SUCCESS(f'Imported "{name}"'))
