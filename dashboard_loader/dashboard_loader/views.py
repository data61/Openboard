from django import forms
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from widget_def.models import WidgetDefinition, Statistic, TrafficLightScaleCode, IconCode
from widget_data.models import StatisticData, StatisticListItem
from dashboard_loader.permissions import get_editable_widgets_for_user, user_has_edit_permission
from dashboard_loader.dynform import get_form_class_for_statistic

# View methods

# Authentication Views
class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, label="User name")
    password = forms.CharField(max_length=255, widget=forms.widgets.PasswordInput)

def login_view(request):
    error = None
    next_url = request.GET.get("next")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect("list_widget_data")
            else:
                 error = "Sorry, that account has been deactivated"
        else:
             error = "Invalid login"
    form = LoginForm()
    return render(request, "login.html", {
            "next": next_url,
            "form": form,
            "error": error,
            })

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

# Data Editing Views
@login_required
def list_widgets(request):
    editable_widgets = get_editable_widgets_for_user(request.user)
    return render(request, "widget_data/list_widgets.html", {
            "widgets": editable_widgets
            })

@login_required
def view_widget(request, widget_url, actual_frequency_url):
    try:
        w = WidgetDefinition.objects.get(url=widget_url, 
                    actual_frequency_url=actual_frequency_url)
    except WidgetDefinition.DoesNotExist:
        return HttpResponseNotFound("This Widget Definition does not exist")
    if not user_has_edit_permission(request.user, w):
        return HttpResponseForbidden("You do not have permission to edit the data for this widget")
    statistics = Statistic.objects.filter(tile__widget=w)
    stats = []
    for s in statistics:
        try:
            data = StatisticData.objects.get(statistic=s)
        except StatisticData.DoesNotExist:
            data = None
        listdata = StatisticListItem.objects.filter(statistic=s)
        stats.append({
                "statistic": s,
                "data": data,
                "listdata": listdata,
            })
    return render(request, "widget_data/view_widget.html", {
            "widget": w,
            "stats": stats,
            })

@login_required
def edit_stat(request, widget_url, actual_frequency_url, tile_url, stat_url):
    try:
        w = WidgetDefinition.objects.get(url=widget_url, actual_frequency_url=actual_frequency_url)
    except WidgetDefinition.DoesNotExist:
        return HttpResponseNotFound("This Widget Definition does not exist")
    if not user_has_edit_permission(request.user, w):
        return HttpResponseForbidden("You do not have permission to edit the data for this widget")
    try:
        s = Statistic.objects.get(tile__widget=w, tile__url=tile_url, url=stat_url)
    except Statistic.DoesNotExist:
        return HttpResponseNotFound("This Widget Definition does not exist")

    form_class = get_form_class_for_statistic(s)
    if s.is_list():
        form_class = forms.formsets.formset_factory(form_class, can_delete=True, extra=4)
    if request.method == 'POST':
        if request.POST.get("submit") or request.POST.get("submit_stay"):
            form = form_class(request.POST)
            if form.is_valid():
                if s.is_list():
                    StatisticListItem.objects.filter(statistic=s).delete()
                    for subform in form:
                        fd = subform.cleaned_data
                        if fd and not fd.get("DELETE"):
                            sli = StatisticListItem(statistic=s)
                            if s.is_numeric():
                                if s.num_precision == 0:
                                    sli.intval = fd["value"]
                                else:
                                    sli.decval = fd["value"]
                            else:
                                sli.strval = fd["value"]
                            if s.traffic_light_scale:
                                try:
                                    tlc = TrafficLightScaleCode.objects.get(scale=s.traffic_light_scale, value=fd["traffic_light_code"])
                                except TrafficLightScaleCode.DoesNotExist:
                                    # TODO: handle error - transactions??
                                    tlc = None
                                sli.traffic_light_code = tlc
                            if s.trend:
                                sli.trend = int(fd["trend"])
                            if s.is_kvlist():
                                sli.keyval = fd["label"]
                            if s.is_eventlist():
                                sli.datekey = fd["date"]
                            if s.hyperlinkable:
                                sli.url = fd["url"]
                            sli.sort_order = fd["sort_order"]
                            sli.save()
                    if request.POST.get("submit"):
                        return redirect("view_widget_data", 
                                widget_url=w.url, 
                                actual_frequency_url=w.actual_frequency_url)
                    else:
                        form = form_class(initial=s.initial_form_data())
                else:
                    fd = form.cleaned_data
                    sd = s.get_data()
                    if not sd:
                        sd = StatisticData(statistic=s)
                    if s.is_numeric():
                        if s.num_precision == 0:
                            sd.intval = fd["value"]
                        else:
                            sd.decval = fd["value"]
                    else:
                        sd.strval = fd["value"]
                    if not s.name_as_label:
                        sd.label = fd["label"]
                    if s.traffic_light_scale:
                        try:
                            tlc = TrafficLightScaleCode.objects.get(scale=s.traffic_light_scale, value=fd["traffic_light_code"])
                        except TrafficLightScaleCode.DoesNotExist:
                            # TODO: handle error
                            tlc = None
                        sd.traffic_light_code = tlc
                    if s.icon_library:
                        try:
                            icon = IconCode.objects.get(scale=s.icon_library, value=fd["icon_code"])
                        except IconCode.DoesNotExist:
                            # TODO: handle error
                            icon = None
                        sd.icon_code = icon
                    if s.trend:
                        sd.trend = int(fd["trend"])
                    sd.save()
                    return redirect("view_widget_data", 
                            widget_url=w.url, 
                            actual_frequency_url=w.actual_frequency_url)
                    
        elif request.POST.get("cancel"):
            return redirect("view_widget_data", 
                        widget_url=w.url, 
                        actual_frequency_url=w.actual_frequency_url)
        elif not s.is_list() and request.POST.get("delete"):
            sd = s.get_data()
            if sd:
                sd.delete()
            return redirect("view_widget_data", 
                        widget_url=w.url, 
                        actual_frequency_url=w.actual_frequency_url)
        else:
            form = form_class(initial=s.initial_form_data())
    else:
        form = form_class(initial=s.initial_form_data())

    return render(request, "widget_data/edit_widget.html", {
                "widget": w,
                "statistic": s,
                "form": form
                })

