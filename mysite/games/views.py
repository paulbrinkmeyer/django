from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Game


def _index_post(request):
    print("title=" + request.POST["title"])
    print("provider=" + request.POST["provider"])
    print("platform=" + request.POST["platform"])
    game = Game(
        title=request.POST["title"],
        provider=request.POST["provider"],
        platform=request.POST["title"]
    )
    game.save()
    return HttpResponseRedirect(reverse('games:detail', args=(game.id,)))

def index(request):
    if request.POST:
        response = _index_post(request)
    else:
        games_list = Game.objects.all()
        context = {"games_list": games_list}
        response = render(request, 'games/index.html', context)
    return response


def submit(request):
    return render(request, 'games/submit.html', {})  


def detail(request, game_id):
    context = {"game_id": game_id}
    return render(request, 'games/detail.html', context)
