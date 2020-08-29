from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
import vote.views

urlpatterns = [
    path("", vote.views.choose, name="vote"),
    path("choice/", vote.views.choice),
    path("stats/", vote.views.stats, name="stats"),
    path("flag/<int:id>.svg", vote.views.flag, name="flag"),
    path("admin/", admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
