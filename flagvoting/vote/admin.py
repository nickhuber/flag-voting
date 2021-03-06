from django.contrib import admin
from django.contrib.sessions.models import Session
from django.db import models

from .models import Flag, Vote


@admin.register(Flag)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "include_in_votes",
        "elo_rating",
        "trueskill_rating",
    )
    list_filter = ("group", "include_in_votes")

    def trueskill_rating(self, obj):
        return obj.trueskill_rating

    trueskill_rating.admin_order_field = "trueskill_rating"


class HasVoteFilter(admin.SimpleListFilter):
    title = "Has vote"
    parameter_name = "has_vote"

    def lookups(self, request, model_admin):
        return (
            ("Yes", "Yes"),
            ("No", "No"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.filter(choice__isnull=False)
        elif value == "No":
            return queryset.filter(choice__isnull=True)
        return queryset


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "voter_created_ip",
        "voter_voted_ip",
        "created_at",
    )
    list_filter = (HasVoteFilter,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("choice_1", "choice_2", "choice")
        return qs

    def get_ordering(self, request):
        return ["-created_at"]

    def description(self, obj):
        return str(obj)

    def voted(self, obj):
        return obj.voted


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()

    list_display = ["session_key", "_session_data", "expire_date"]
