from widget_def.models import *

def api_get_themes():
    return [ t.__getstate__() for t in Theme.objects.all() ]

def api_get_locations():
    return [ l.__getstate__() for l in Location.objects.all() ]

def api_get_frequencies():
    return [ f.__getstate__() for f in Frequency.objects.filter(display_mode=True) ]

def api_get_icon_libraries():
    return { l.name : l.__getstate__() for l in IconLibrary.objects.all() }

def api_get_widgets(theme, location, frequency):
    widgets = WidgetDeclaration.objects.filter(theme=theme, 
                    location=location, 
                    frequency=frequency)
    return [ w.__getstate__() for w in widgets ]

