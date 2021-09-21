import requests

from django.http import HttpResponse
from socket import gethostname, gethostbyname


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def ip(request):
    # another option is http://checkip.dyndns.org/
    response = requests.get("http://ipinfo.io/ip")
    return HttpResponse(response.text)
