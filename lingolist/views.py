from django.shortcuts import redirect, render


def landing_page(request):
    # if request.user.is_authenticated:
    #     return redirect("lists:list_index")
    return render(request, "landing.html")
