import copy
import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import FieldVisibleAlways, Game, Settings


def _fields_get(model_instance):
    field_list = []
    for field in model_instance._meta.get_fields():
        field_list.append(field.name)
    return field_list


def _fields_visible():
    fields = _fields_get(Game)
    settings = _settings_get()

    return_list = _fields_visible_always()
    for field in fields:
        field_setting_name = "show_" + field
        if hasattr(settings, field_setting_name):
            if getattr(settings, field_setting_name):
                if not field in return_list:
                    return_list.append(field)
    return return_list


def _fields_visible_always():
    return_list = ["id"]
    for field in FieldVisibleAlways.objects.all():
        return_list.append(field.name)
    return return_list


def _fields_hidden():
    fields = _fields_get(Game)
    settings = _settings_get()
    fields_visible_always = _fields_visible_always()

    return_list = []
    for field in fields:
        field_setting_name = "show_" + field
        if hasattr(settings, field_setting_name):
            if not getattr(settings, field_setting_name):
                if not field in fields_visible_always:
                    return_list.append(field)
    return return_list


def _fields_that_are_hideable():
    return_list = _fields_get(Game)
    for field in _fields_visible_always():
        if field in return_list:
            return_list.remove(field)
    return return_list


def _fields_hideable_settings():
    """
    This is needed becuase I have yet to find a way in a template
    to get the field show setting along with the propety name just
    from the field list. It is easy with plain old Python code using
    getattr.

    return: A list of dicts with the each fields hideable settings. e.g.
    [
        {
            "field_name": "field_1",
            "field_setting_name": "show_field_1,
            "field_show": True,
        },
        ...
    ]
    """
    return_list = []
    fields_hideable = _fields_that_are_hideable()
    settings = _settings_get()
    for field in fields_hideable:
        field_setting_name = "show_" + field
        if hasattr(settings, field_setting_name):
            field_show = getattr(settings, field_setting_name)
            return_list.append(
                {
                    "field_name": field,
                    "field_setting_name": field_setting_name,
                    "field_show": field_show
                }
            )
    return return_list


def _detail_post(request):
    id = None

    if request.POST:
        body = request.POST
    elif request.body:
        body = json.loads(request.body)
    else:
        body = {}

    print("body=" + str(body))
    id = body.get("id")

    if id:
        print("id=" + str(id))
        game = Game.objects.get(pk=id)

        for field in body:
            if hasattr(game, field) and field != "id":
                value = body[field]
                setattr(game, field, value)
                print('setting "' + value + '" to the "' + field + '" field of id ' + body['id'])

        game.save()
    else:
        id=1

    return HttpResponseRedirect(reverse('games:detail', args=(body["id"],)))


def _index_post(request):
    print("title=" + request.POST["title"])
    print("provider=" + request.POST["provider"])
    print("platform=" + request.POST["platform"])
    game = Game(
        title=request.POST["title"],
        provider=request.POST["provider"],
        platform=request.POST["platform"],
        type=request.POST["type"]
    )
    game.save()
    return HttpResponseRedirect(reverse('games:detail', args=(game.id,)))


def _settings_get():
    try:
        settings = Settings.objects.all()[0]
    except:
        print("No settings found. A set was created.")
        settings = Settings()
        settings.save()
    return settings


def _settings_post(request):
    settings = _settings_get()
    settings_fields = _fields_get(Settings)
    print(request.POST)
    for field in settings_fields:
        if field in request.POST:
            if field == "sort_by":
                settings.sort_by = request.POST["sort_by"]
            elif field == "sort_reverse":
                if request.POST["sort_reverse"].lower() == "true":
                    print("sort_reverse is true")
                    settings.sort_reverse = True
                elif request.POST["sort_reverse"].lower() == "false":
                    print("sort_reverse is false")
                    settings.sort_reverse = False
            elif request.POST[field].lower() == "true":
                setattr(settings, field, True)
            else:
                setattr(settings, field, False)
        else:
            if "missing_means_unchecked" in request.POST:
                setattr(settings, field, False)
    settings.save()
    return HttpResponseRedirect(reverse('games:index'))


def _generate_table(model, never_show_fields=[], sort_by="title"):
    """
    return: a list that desribes a table. The first row has header info e.g.
    [
        [
            {"title": field1, "hide_button_show":False},
            ...
            {"title": fieldN, "hide_button_show":True}
        ]
        {"id": 1, "data": [ {"name": field1, "value": model1_field1}, ...  ] }
        ...
        {"id": M, "data": [ {"name": fieldM, "value": modelM_field1}, ... ] }
    """
    model_list = model.objects.all()
    field_list = _fields_visible()
    settings = _settings_get()
    fields_visible_always = _fields_visible_always()

    # remove fields to never show
    for field in never_show_fields:
        if field in field_list:
            field_list.remove(field)

    # create the headers
    header_list = []
    for field in field_list:
        title_attributes = {"title": field.capitalize()}
        title_attributes["hide_button_show"] = not field in fields_visible_always
        header_list.append(copy.deepcopy(title_attributes))

    # add all the rows
    table = []
    col = 0
    for model_instance in model_list:
        row = {}
        row["id"] = model_instance.id
        row["field"] = field_list[col:col+1]
        data = []
        for field in field_list:
            cell = {}
            cell["name"] = field
            cell["value"] = getattr(model_instance,field)
            data.append(cell)
        row["data"] = data
        table.append(row)
        col += 1

    # sort the table
    if sort_by in field_list:
        i = field_list.index(sort_by)
        # ref for this magic: https://stackoverflow.com/questions/18411560/sort-list-while-pushing-none-values-to-the-end
        table = sorted(table, key=lambda row: (row["data"][i]["value"] is None, row["data"][i]["value"]), reverse=settings.sort_reverse)

    table = [header_list] + table
    return table


def index(request):
    if request.POST:
        response = _index_post(request)
    else:
        settings = _settings_get()
        context = {
            "fields_hidden": _fields_hidden(),
            "settings": _settings_get(),
            "table": _generate_table(
                model=Game,
                never_show_fields=[],
                sort_by=settings.sort_by
            )
        }
        response = render(request, 'games/index.html', context)
    return response


def settings(request):
    if request.POST:
        response = _settings_post(request)
    else:
        context = {
            "field_list": _fields_get(Game),
            "settings": _settings_get(),
            "fields_hideable_settings": _fields_hideable_settings()
        }
        response = render(request, 'games/settings.html', context)
    return response


def submit(request):
    return render(request, 'games/submit.html', {})  


def detail(request, game_id):
    print("request.POST="+str(request.POST))
    print("request.body="+str(request.body))
    if request.method == 'POST':
        print("!!! post exists !!!")
        response = _detail_post(request)
    else:
        print("!!! post does NOT exist !!!")
        game = Game.objects.get(pk=game_id)
        context = {"game": game}
        response = render(request, 'games/detail.html', context)
    return response
