from django.core.management.base import BaseCommand, CommandError
from vote.models import Vote, Flag

import trueskill


class Command(BaseCommand):
    help = "Figure out elo and trueskill for all votes"

    def handle(self, *args, **options):
        Flag.objects.all().update(
            elo_rating=1000.0,
            trueskill_rating_mu=trueskill.Rating().mu,
            trueskill_rating_sigma=trueskill.Rating().sigma,
        )
        for vote in Vote.objects.filter(voted=True).order_by("updated_at"):
            vote.update_elo()
            vote.update_trueskill()
