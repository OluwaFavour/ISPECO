from django.shortcuts import render


def index(request, cam_id):
    """Video streaming home page."""
    return render(request, "live_stream.html", context={"cam_id": cam_id})
