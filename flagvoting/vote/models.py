import uuid
import re

import elo
import trueskill

from django.db import models
from django.db.models import F


class FlagManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(
            trueskill_rating=models.ExpressionWrapper(
                F("trueskill_rating_mu") - (3 * F("trueskill_rating_sigma")),
                output_field=models.FloatField(),
            )
        )
        return qs


class Flag(models.Model):
    name = models.CharField(max_length=1024)
    svg = models.TextField(help_text="The SVG string to render this flag")
    elo_rating = models.FloatField(default=1000.0)
    trueskill_rating_mu = models.FloatField(default=trueskill.Rating().mu)
    trueskill_rating_sigma = models.FloatField(default=trueskill.Rating().sigma)
    objects = FlagManager()

    def __str__(self):
        return self.name

    def clean(self):
        self.svg = re.sub(r"<title>.*<\/title>", "", self.svg)


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    voter_ip = models.GenericIPAddressField(null=True)
    choice_1 = models.ForeignKey(
        Flag, on_delete=models.CASCADE, related_name="first_choice"
    )
    choice_2 = models.ForeignKey(
        Flag, on_delete=models.CASCADE, related_name="second_choice"
    )
    choice = models.ForeignKey(
        Flag, on_delete=models.CASCADE, related_name="chosen_choice", null=True,
    )
    voted = models.BooleanField(db_index=True)

    def __str__(self):
        if self.choice:
            return f"{self.choice_1} vs {self.choice_2} => {self.choice}"
        else:
            return f"{self.choice_1} vs {self.choice_2}"

    def update_elo(self):
        if self.choice_id == self.choice_1_id:
            (choice_1_elo, choice_2_elo) = elo.rate_1vs1(
                self.choice_1.elo_rating, self.choice_2.elo_rating
            )
        else:
            (choice_2_elo, choice_1_elo) = elo.rate_1vs1(
                self.choice_2.elo_rating, self.choice_1.elo_rating
            )
        self.choice_2.elo_rating = choice_2_elo
        self.choice_2.save()
        self.choice_1.elo_rating = choice_1_elo
        self.choice_1.save()

    def update_trueskill(self):
        if self.choice_id == self.choice_1_id:
            (choice_1_trueskill, choice_2_trueskill) = trueskill.rate_1vs1(
                trueskill.Rating(
                    mu=self.choice_1.trueskill_rating_mu,
                    sigma=self.choice_1.trueskill_rating_sigma,
                ),
                trueskill.Rating(
                    mu=self.choice_2.trueskill_rating_mu,
                    sigma=self.choice_2.trueskill_rating_sigma,
                ),
            )
        else:
            (choice_2_trueskill, choice_1_trueskill) = trueskill.rate_1vs1(
                trueskill.Rating(
                    mu=self.choice_2.trueskill_rating_mu,
                    sigma=self.choice_2.trueskill_rating_sigma,
                ),
                trueskill.Rating(
                    mu=self.choice_1.trueskill_rating_mu,
                    sigma=self.choice_1.trueskill_rating_sigma,
                ),
            )
        self.choice_2.trueskill_rating_mu = choice_2_trueskill.mu
        self.choice_2.trueskill_rating_sigma = choice_2_trueskill.sigma
        self.choice_2.save()
        self.choice_1.trueskill_rating_mu = choice_1_trueskill.mu
        self.choice_1.trueskill_rating_sigma = choice_1_trueskill.sigma
        self.choice_1.save()
