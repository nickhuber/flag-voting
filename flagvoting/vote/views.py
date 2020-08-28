import json
import random

from django.shortcuts import render
from django.http import JsonResponse

from .models import Flag, Vote


def choose(request):
    ids = list(Flag.objects.all().values_list("id", flat=True))
    first_id = random.choice(ids)
    ids.remove(first_id)
    second_id = random.choice(ids)
    flag_1 = Flag.objects.get(id=first_id)
    flag_2 = Flag.objects.get(id=second_id)
    vote = Vote.objects.create(voted=False, choice_1=flag_1, choice_2=flag_2,)
    return render(
        request, "choice.html", {"flag_1": flag_1, "flag_2": flag_2, "vote": vote}
    )


def choice(request):
    if request.method == "POST":
        try:
            vote_request = json.loads(request.body)
        except TypeError:
            return JsonResponse(
                {"status": "failure", "reason": "malformed request"}, status=400,
            )
        if "vote_id" not in vote_request:
            return JsonResponse(
                {"status": "failure", "reason": "No vote ID provided"}, status=400,
            )
        try:
            vote = Vote.objects.get(id=vote_request["vote_id"])
        except Vote.DoesNotExist:
            return JsonResponse(
                {"status": "failure", "reason": "Vote does not exist"}, status=400,
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
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                vote.voter_ip = x_forwarded_for.split(',')[0]
            else:
                vote.voter_ip = request.META.get('REMOTE_ADDR')
            vote.update_elo()
            vote.update_trueskill()
            vote.save()
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse(
                {"status": "failure", "reason": "invalid chosen flag"}, status=400,
            )
    else:
        return JsonResponse(
            {"status": "failure", "reason": "only POST allowed"}, status=400
        )
