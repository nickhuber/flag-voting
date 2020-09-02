import json
import random

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Count

from .models import Flag, Vote


def choose(request):
    if request.session.get("vote", None) is None:
        # No previous vote, or previous vote was resolved
        ids = list(Flag.objects.all().values_list("id", flat=True))
        first_id = random.choice(ids)
        ids.remove(first_id)
        second_id = random.choice(ids)
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            voter_ip = x_forwarded_for.split(",")[0]
        else:
            voter_ip = request.META.get("REMOTE_ADDR")
        vote = Vote.objects.create(
            voted=False,
            choice_1=Flag.objects.get(id=first_id),
            choice_2=Flag.objects.get(id=second_id),
            voter_ip=voter_ip,
        )
        request.session["vote"] = str(vote.id)
    else:
        # Use the previous vote if it hasn't yet been resolved
        vote = Vote.objects.get(id=request.session["vote"])
    return render(request, "choice.html", {"vote": vote})


def choice(request):
    if not request.session.get("vote"):
        return JsonResponse(
            {"status": "failure", "reason": "You do not have a vote in progress"},
            status=400,
        )
    vote = Vote.objects.get(id=request.session["vote"])
    if request.method == "POST":
        try:
            vote_request = json.loads(request.body)
        except TypeError:
            return JsonResponse(
                {"status": "failure", "reason": "malformed request"}, status=400,
            )
        if vote.voted:
            return JsonResponse(
                {"status": "failure", "reason": "This vote was already cast"},
                status=400,
            )
        if "chosen_flag_id" not in vote_request:
            return JsonResponse(
                {"status": "failure", "reason": "No flag was voted for"}, status=400,
            )

        if vote_request["chosen_flag_id"] in (vote.choice_1.id, vote.choice_2.id):
            vote.choice = Flag.objects.get(id=vote_request["chosen_flag_id"])
            vote.voted = True
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                vote.voter_ip = x_forwarded_for.split(",")[0]
            else:
                vote.voter_ip = request.META.get("REMOTE_ADDR")
            vote.update_elo()
            vote.update_trueskill()
            vote.save()
            request.session["vote"] = None
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse(
                {"status": "failure", "reason": "invalid chosen flag"}, status=400,
            )
    else:
        return JsonResponse(
            {"status": "failure", "reason": "only POST allowed"}, status=400
        )


def flag(request, id):
    flag = get_object_or_404(Flag, id=id)
    return HttpResponse(flag.svg, content_type="image/svg+xml")


def stats(request):
    ts_most_popular_flags = Flag.objects.order_by("-trueskill_rating")[:5]
    ts_least_popular_flags = Flag.objects.order_by("trueskill_rating")[:5]
    elo_most_popular_flags = Flag.objects.order_by("-elo_rating")[:5]
    elo_least_popular_flags = Flag.objects.order_by("elo_rating")[:5]
    flags_by_vote = (
        Vote.objects.filter(choice__isnull=False)
        .values("choice__id", "choice__name")
        .annotate(num_votes=Count("choice"))
        .order_by("-num_votes")
    )
    return render(
        request,
        "stats.html",
        {
            "most_voted_for": flags_by_vote.first(),
            "least_voted_for": flags_by_vote.last(),
            "ts_most_popular_flags": ts_most_popular_flags,
            "ts_least_popular_flags": ts_least_popular_flags,
            "elo_most_popular_flags": elo_most_popular_flags,
            "elo_least_popular_flags": elo_least_popular_flags,
        },
    )
