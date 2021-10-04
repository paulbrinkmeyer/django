import copy

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import FieldVisibleAlways, Game, Settings


def _fields_get(model_instance):
    field_list = []
    for field in model_instance._meta.get_fields():
        field_list.append(field.name)
    return field_list


def _fieds_visible():
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
    return_list = []
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
    if "id" in request.POST:
        print("requested id is " + request.POST["id"])
    if "title" in request.POST:
        print("requested title is " + request.POST["title"])
    if "provider" in request.POST:
        print("requested provider is " + request.POST["provider"])
    if "platform" in request.POST:
        print("requested platform is " + request.POST["platform"])
    game = Game.objects.get(pk=request.POST["id"])
    game.title = request.POST["title"]
    game.provider = request.POST["provider"]
    game.platform = request.POST["platform"]
    game.save()
    return HttpResponseRedirect(reverse('games:detail', args=(request.POST["id"],)))


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
    for field in settings_fields:
        if field in request.POST:
            if request.POST[field].lower() == "true":
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
            {"title": "field1", "hide_button_show":False},
            ...
            {"title": "fieldN", "hide_button_show":True}
        ]
        [ model1_field1, ... model1_fieldN ]
        ...
        [ modelM_field1, ... modelM_fieldN ]
    """
    model_list = model.objects.all()
    field_list = _fieds_visible()

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

    #print(header_list)

    # add all the rows
    table = []
    for model_instance in model_list:
        row = []
        for field in field_list:
            row.append(getattr(model_instance,field))
        table.append(row)

    # sort the table
    if sort_by in field_list:
        sort_by_index = field_list.index(sort_by)
        table = sorted(table, key=lambda col: col[sort_by_index])

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
            "settings": _settings_get(),
            "fields_hideable_settings": _fields_hideable_settings()
        }
        response = render(request, 'games/settings.html', context)
    return response


def submit(request):
    return render(request, 'games/submit.html', {})  


def detail(request, game_id):
    if request.POST:
        response = _detail_post(request)
    else:
        game = Game.objects.get(pk=game_id)
        context = {"game": game}
        response = render(request, 'games/detail.html', context)
    return response
