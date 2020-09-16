import itertools
import json
import random

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.core.cache import cache

from .models import Flag, FlagGroup, Vote


def get_ip_from_request(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    else:
        return request.META.get("REMOTE_ADDR")


def choose(request, group=FlagGroup.COUNTRY):
    if group not in FlagGroup:
        raise Http404("No flag has that group.")
    vote = None
    if request.session.get(f"vote/{group}", None):
        # Use the previous vote if it hasn't yet been resolved
        try:
            vote = Vote.objects.select_related("choice_1", "choice_2").get(
                id=request.session[f"vote/{group}"]
            )
        except Vote.DoesNotExist:
            del request.session[f"vote/{group}"]
    if not vote:
        # No previous vote, or previous vote was resolved
        ids = list(Flag.objects.filter(group=group, include_in_votes=True).values_list("id", flat=True))
        first_id = random.choice(ids)
        ids.remove(first_id)
        second_id = random.choice(ids)
        vote = Vote.objects.create(
            choice_1_id=first_id,
            choice_2_id=second_id,
            voter_created_ip=get_ip_from_request(request),
        )
        request.session[f"vote/{group}"] = str(vote.id)
    return render(
        request,
        "choice.html",
        {
            "vote": vote,
            "previous": request.session.get(f"previous/{group}"),
            "group": group.lower(),
        },
    )


def choice(request, group=FlagGroup.COUNTRY):
    if group not in FlagGroup:
        return redirect(f"/")
    if not request.session.get(f"vote/{group}"):
        messages.error(request, "Failed to submit vote, try again.")
        return redirect(f"/{group.lower()}/")
    vote = Vote.objects.select_related("choice_1", "choice_2").get(
        id=request.session[f"vote/{group}"]
    )
    if request.method == "POST":
        choice_id = int(request.POST["choice"])
        if vote.choice:
            request.session[f"vote/{group}"] = None
        elif choice_id in (vote.choice_1_id, vote.choice_2_id):
            vote.choice_id = choice_id
            vote.voter_voted_ip = get_ip_from_request(request)
            choice_1_rating_pre = vote.choice_1.get_trueskill_rating()
            choice_2_rating_pre = vote.choice_2.get_trueskill_rating()
            vote.update_elo()
            vote.update_trueskill()
            vote.save()
            choice_1_rating_post = vote.choice_1.get_trueskill_rating()
            choice_2_rating_post = vote.choice_2.get_trueskill_rating()
            request.session[f"vote/{group}"] = None
            request.session[f"previous/{group}"] = {
                "choice_1_svg": vote.choice_1.svg,
                "choice_2_svg": vote.choice_2.svg,
                "choice_1_name": vote.choice_1.name,
                "choice_2_name": vote.choice_2.name,
                "choice_1_change": choice_1_rating_post - choice_1_rating_pre,
                "choice_2_change": choice_2_rating_post - choice_2_rating_pre,
            }
    return redirect(f"/{group.lower()}/")


def stats(request):
    most_popular_country_flags = Flag.objects.filter(group=FlagGroup.COUNTRY, include_in_votes=True).order_by(
        "-trueskill_rating"
    )[:5]
    least_popular_country_flags = Flag.objects.filter(group=FlagGroup.COUNTRY, include_in_votes=True).order_by(
        "trueskill_rating"
    )[:5]
    most_popular_state_flags = Flag.objects.filter(group=FlagGroup.STATE, include_in_votes=True).order_by(
        "-trueskill_rating"
    )[:5]
    least_popular_state_flags = Flag.objects.filter(group=FlagGroup.STATE, include_in_votes=True).order_by(
        "trueskill_rating"
    )[:5]
    return render(
        request,
        "stats.html",
        {
            "most_popular_country_flags": most_popular_country_flags,
            "least_popular_country_flags": least_popular_country_flags,
            "most_popular_state_flags": most_popular_state_flags,
            "least_popular_state_flags": least_popular_state_flags,
        },
    )


def full_stats(request):
    country_flags = Flag.objects.filter(group=FlagGroup.COUNTRY, include_in_votes=True).order_by(
        "-trueskill_rating"
    )
    state_flags = Flag.objects.filter(group=FlagGroup.STATE, include_in_votes=True).order_by(
        "-trueskill_rating"
    )
    return render(
        request,
        "full_stats.html",
        {"flags": itertools.zip_longest(country_flags, state_flags)},
    )
