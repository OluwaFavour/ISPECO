from django.shortcuts import render


def index(request):
    """Video streaming home page."""
    return render(request, "live_stream.html")
