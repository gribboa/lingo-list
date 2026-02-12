from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from .sitemaps import sitemaps
from .views import (
    healthz,
    landing_page,
    privacy_notice_page,
    robots_txt,
    use_case_multilingual_shopping_lists,
    use_case_roommate_household_task_lists,
    use_case_travel_planning_shared_lists,
)

urlpatterns = [
    path("", landing_page, name="landing"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap_xml"),
    path("healthz/", healthz, name="healthz"),
    path("privacy/", privacy_notice_page, name="privacy_notice"),
    path(
        "use-cases/multilingual-shopping-lists/",
        use_case_multilingual_shopping_lists,
        name="use_case_multilingual_shopping_lists",
    ),
    path(
        "use-cases/travel-planning-shared-lists/",
        use_case_travel_planning_shared_lists,
        name="use_case_travel_planning_shared_lists",
    ),
    path(
        "use-cases/roommate-household-task-lists/",
        use_case_roommate_household_task_lists,
        name="use_case_roommate_household_task_lists",
    ),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("lists/", include("lists.urls")),
]
