from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


def landing_page(request):
    # if request.user.is_authenticated:
    #     return redirect("lists:list_index")
    return render(request, "landing.html")


def privacy_notice_page(request):
    return render(request, "privacy_notice.html")


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Allow: /privacy/",
        "Allow: /accounts/login/",
        "Allow: /accounts/signup/",
        "Allow: /accounts/password/reset/",
        "Allow: /use-cases/",
        "Disallow: /admin/",
        "Disallow: /lists/",
        "Disallow: /healthz/",
        "Disallow: /accounts/profile/",
        "Disallow: /accounts/logout/",
        "Disallow: /lists/join/",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def use_case_multilingual_shopping_lists(request):
    return render(request, "use_cases/multilingual_shopping_lists.html")


def use_case_travel_planning_shared_lists(request):
    return render(request, "use_cases/travel_planning_shared_lists.html")


def use_case_roommate_household_task_lists(request):
    return render(request, "use_cases/roommate_household_task_lists.html")


def healthz(request):
    return JsonResponse({"status": "ok"})
