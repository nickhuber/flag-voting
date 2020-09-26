import uuid
import re

from scour import scour
import elo
import trueskill

from django.conf import settings
from django.db import models
from django.db.models import F, Q, Count
from django.db.models.expressions import Case, When


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


class MinimumVoteManager(FlagManager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = (
            qs.annotate(
                num_first_choices=Count(
                    "first_choice",
                    Case(
                        When(first_choice__choice__isnull=False, then=True),
                        When(first_choice__choice__isnull=True, then=False),
                    ),
                ),
                num_second_choices=Count(
                    "second_choice",
                    Case(
                        When(second_choice__choice__isnull=False, then=True),
                        When(second_choice__choice__isnull=True, then=False),
                    ),
                ),
            )
            .annotate(num_choices=F("num_first_choices") + F("num_second_choices"))
            .filter(num_choices__gt=settings.MINIMUM_VOTES_FOR_STATS)
        )
        return qs


class FlagGroup(models.TextChoices):
    COUNTRY = "COUNTRY", "Country"
    STATE = "STATE", "State"


class Flag(models.Model):
    name = models.CharField(max_length=1024)
    svg = models.TextField(help_text="The SVG string to render this flag")
    group = models.CharField(
        max_length=7,
        choices=FlagGroup.choices,
        default=FlagGroup.COUNTRY,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    elo_rating = models.FloatField(default=1000.0)
    trueskill_rating_mu = models.FloatField(default=trueskill.Rating().mu)
    trueskill_rating_sigma = models.FloatField(default=trueskill.Rating().sigma)
    include_in_votes = models.BooleanField(default=True)

    objects = FlagManager()
    minimum_votes_objects = MinimumVoteManager()

    class Meta:
        base_manager_name = "objects"

    def __str__(self):
        return self.name

    def clean(self):
        self.svg = re.sub(r"<title>.*<\/title>", "", self.svg)
        try:
            self.svg = scour.scourString(self.svg)
        except:
            # Scour seems to struggle on some SVGs so just skip past them
            pass

    def get_trueskill_rating(self):
        """
        Should be the same as `.trueskill_rating` but you don't always get
        the right manager object so this can be helpful as a fallback.
        """
        return self.trueskill_rating_mu - (3 * self.trueskill_rating_sigma)


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    voter_created_ip = models.GenericIPAddressField(null=True)
    voter_voted_ip = models.GenericIPAddressField(null=True)
    choice_1 = models.ForeignKey(
        Flag, on_delete=models.CASCADE, related_name="first_choice"
    )
    choice_2 = models.ForeignKey(
        Flag, on_delete=models.CASCADE, related_name="second_choice"
    )
    choice = models.ForeignKey(
        Flag, on_delete=models.CASCADE, related_name="chosen_choice", null=True,
    )

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
        self.choice_1.elo_rating = choice_1_elo

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
        self.choice_1.trueskill_rating_mu = choice_1_trueskill.mu
        self.choice_1.trueskill_rating_sigma = choice_1_trueskill.sigma
