from django.contrib import admin
from .models import Flag, Vote


@admin.register(Flag)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "elo_rating",
        "trueskill_rating_mu",
        "trueskill_rating_sigma",
        "trueskill_rating",
    )

    def trueskill_rating(self, obj):
        return obj.trueskill_rating

    trueskill_rating.admin_order_field = "trueskill_rating"


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "choice_1",
        "choice_2",
        "choice",
        "voted",
        "voter_ip",
        "created_at",
    )
    list_filter = ("voted",)
