import json
import random

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Count

from .models import Flag, FlagGroup, Vote


def choose(request, group=FlagGroup.COUNTRY):
    if group not in FlagGroup:
        raise Http404("No flag has that group.")
    vote = Vote.objects.none()
    if request.session.get(f"vote/{group}", None):
        # Use the previous vote if it hasn't yet been resolved
        try:
            vote = Vote.objects.get(id=request.session[f"vote/{group}"])
        except Vote.DoesNotExist:
            pass
        else:
            vote = Vote.objects.get(id=request.session[f"vote/{group}"])
    if not vote:
        # No previous vote, or previous vote was resolved
        ids = list(Flag.objects.filter(group=group).values_list("id", flat=True))
        first_id = random.choice(ids)
        ids.remove(first_id)
        second_id = random.choice(ids)
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            voter_ip = x_forwarded_for.split(",")[0]
        else:
            voter_ip = request.META.get("REMOTE_ADDR")
        vote = Vote.objects.create(
            choice_1=Flag.objects.get(id=first_id),
            choice_2=Flag.objects.get(id=second_id),
            voter_created_ip=voter_ip,
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
        return JsonResponse(
            {"status": "failure", "reason": "Invalid group"}, status=400,
        )
    if not request.session.get(f"vote/{group}"):
        return JsonResponse(
            {"status": "failure", "reason": "You do not have a vote in progress"},
            status=400,
        )
    vote = Vote.objects.get(id=request.session[f"vote/{group}"])
    if request.method == "POST":
        choice = int(request.POST["choice"])
        if vote.choice:
            request.session[f"vote/{group}"] = None
        elif choice in (vote.choice_1.id, vote.choice_2.id):
            vote.choice = Flag.objects.get(id=choice)
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                vote.voter_voted_ip = x_forwarded_for.split(",")[0]
            else:
                vote.voter_voted_ip = request.META.get("REMOTE_ADDR")
            choice_1_rating_pre = vote.choice_1.trueskill_rating
            choice_2_rating_pre = vote.choice_2.trueskill_rating
            vote.update_elo()
            vote.update_trueskill()
            vote.save()
            vote.refresh_from_db()
            choice_1_rating_post = vote.choice_1.trueskill_rating
            choice_2_rating_post = vote.choice_2.trueskill_rating
            request.session[f"vote/{group}"] = None
            request.session[f"previous/{group}"] = {
                "choice_1_id": vote.choice_1.id,
                "choice_2_id": vote.choice_2.id,
                "choice_1_name": vote.choice_1.name,
                "choice_2_name": vote.choice_2.name,
                "choice_1_change": choice_1_rating_post - choice_1_rating_pre,
                "choice_2_change": choice_2_rating_post - choice_2_rating_pre,
            }
    return redirect(f"/{group.lower()}/")


def flag(request, id):
    flag = get_object_or_404(Flag, id=id)
    return HttpResponse(flag.svg, content_type="image/svg+xml")


def stats(request):
    most_popular_country_flags = Flag.objects.filter(group=FlagGroup.COUNTRY).order_by(
        "-trueskill_rating"
    )[:5]
    least_popular_country_flags = Flag.objects.filter(group=FlagGroup.COUNTRY).order_by(
        "trueskill_rating"
    )[:5]
    most_popular_state_flags = Flag.objects.filter(group=FlagGroup.STATE).order_by(
        "-trueskill_rating"
    )[:5]
    least_popular_state_flags = Flag.objects.filter(group=FlagGroup.STATE).order_by(
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
