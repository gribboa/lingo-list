from django.http import JsonResponse
from django.shortcuts import render


def landing_page(request):
    # if request.user.is_authenticated:
    #     return redirect("lists:list_index")
    return render(request, "landing.html")


def privacy_notice_page(request):
    return render(request, "privacy_notice.html")


def healthz(request):
    return JsonResponse({"status": "ok"})
