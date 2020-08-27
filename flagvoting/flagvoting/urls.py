from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
import vote.views

urlpatterns = [
    path("", vote.views.choose),
    path("choice/", vote.views.choice),
    path("admin/", admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
