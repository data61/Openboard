from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dashboard_api.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    # Simple list API views
    url(r'^api/themes/$', 'widget_def.views.get_themes', name='get_themes'),
    url(r'^api/locations/$', 'widget_def.views.get_locations', name='get_locations'),
    url(r'^api/frequencies/$', 'widget_def.views.get_frequencies', name='get_frequencies'),
    url(r'^api/icons/$', 'widget_def.views.get_icon_libraries', name='get_icon_libraries'),

    # Main API view for obtaining widget definitions
    url(r'^api/widgets/$', 'widget_def.views.get_widgets', name='get_frequencies'),

    # Main Data API view
    url(r'^api/widgets/(?P<widget_url>[^/]+)$', 'widget_data.views.get_widget_data', name='get_widget_data'),

    # Views for manually maintaining data
    url(r'^data/$', 'widget_data.views.list_widgets', name='list_widget_data'),
    url(r'^data/(?P<widget_url>[^/]+)/(?P<actual_frequency_url>[^/]+)$', 
                        'widget_data.views.view_widget', name="view_widget_data"),
    url(r'^data/(?P<widget_url>[^/]+)/(?P<actual_frequency_url>[^/]+)/(?P<tile_url>[^/]+)/(?P<stat_url>[^/]*)$', 
                        'widget_data.views.edit_stat', name="edit_stat"),

    # Admin views (For modifying widget definitions, adding new widgets, etc.)
    url(r'^admin/', include(admin.site.urls)),
)
