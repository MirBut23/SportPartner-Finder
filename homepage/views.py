from django.shortcuts import render


def index(request):
    return render(request, "homepage/index.html")


def page_not_found(request, exception):
    return render(request, "homepage/404.html", status=404)
