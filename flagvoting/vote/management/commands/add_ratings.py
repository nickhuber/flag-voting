from django.core.management.base import BaseCommand, CommandError
from vote.models import Vote


class Command(BaseCommand):
    help = "Figure out elo for any previous votes, probably doesn't make sense to run multiple times"

    def handle(self, *args, **options):
        for vote in Vote.objects.filter(voted=True).order_by("updated_at"):
            vote.update_elo()
            vote.update_trueskill()
