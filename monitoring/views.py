from django.shortcuts import render


def dashboard(request):
    return render(
        request,
        'monitoring/dashboard.html'
    )


def mood(request):
    return render(
        request,
        'monitoring/mood.html'
    )


def sleep(request):
    return render(
        request,
        'monitoring/sleep.html'
    )


def journal(request):
    return render(
        request,
        'monitoring/journal.html'
    )