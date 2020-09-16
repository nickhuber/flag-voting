from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
import vote.views
from vote.models import FlagGroup

urlpatterns = [
    path("", vote.views.choose, name="vote"),
    path(
        "country/",
        vote.views.choose,
        name="vote-country",
        kwargs={"group": FlagGroup.COUNTRY},
    ),
    path(
        "state/",
        vote.views.choose,
        name="vote-state",
        kwargs={"group": FlagGroup.STATE},
    ),
    path("country/choice/", vote.views.choice, kwargs={"group": FlagGroup.COUNTRY}),
    path("state/choice/", vote.views.choice, kwargs={"group": FlagGroup.STATE}),
    path("stats/", vote.views.stats, name="stats"),
    path("full-stats/", vote.views.full_stats, name="full-stats"),
    path("admin/", admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls)),] + urlpatterns
