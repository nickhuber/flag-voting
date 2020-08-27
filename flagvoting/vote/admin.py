from django.contrib import admin

from .models import Flag, Vote

admin.site.register(Flag)


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
