from dashboard_api.management.import_export import ImportExportException
from widget_def.models import *
from dashboard_loader.loader_utils import *

def import_widget_data(data):
    try:
        family = WidgetFamily.objects.get(url=data["family"])
    except WidgetFamily.DoesNotExist:
        raise ImportExportException("Widget Family %s does not exist" % data["family"])
    except Exception, e:
        raise ImportExportException("Invalid import data %s" % repr(data))
    for w in data["widgets"]:
        try:
            wd = WidgetDefinition.objects.get(family=family, actual_location__url=w["actual_location"], actual_frequency__url=w["actual_frequency"])
        except WidgetDefinition.DoesNotExist:
            raise ImportExportException("Widget definition %s (%s,%s) does not exist" % (family.url, w["actual_location"], w["actual_frequency"]))
        set_actual_frequency_display_text(data["family"],
                                w["actual_location"],
                                w["actual_frequency"],
                                w["data"]["actual_frequency"])
        for surl, s in w["data"]["statistics"].items():
            try:
                stat = Statistic.objects.get(tile__widget=wd,
                                url=surl)
            except Statistic.DoesNotExist:
                raise ImportExportException("Statistic %d for widget %s (%s,%s) does not exist" % (
                                surl,
                                data["family"], 
                                w["actual_location"],
                                w["actual_frequency"]))
                             
            if stat.is_data_list():
                clear_statistic_list(data["family"],
                                w["actual_location"],
                                w["actual_frequency"],
                                surl)
                sort_order = 10
                for item in s:
                    add_statistic_list_item(data["family"],
                                w["actual_location"],
                                w["actual_frequency"],
                                surl,
                                item["value"],
                                sort_order,
                                datetimekey=parse_datetime(item.get("datetime")),
                                datetimekey_level=item.get("datetime_level"),
                                datekey=parse_date(item.get("date")),
                                traffic_light_code=item.get("traffic_light"),
                                icon_code=item.get("icon"),
                                trend = item.get("trend"),
                                label = item.get("label"),
                                url = item.get("url"))
                    sort_order += 10
            else:
                set_statistic_data(data["family"],
                                w["actual_location"],
                                w["actual_frequency"],
                                surl,
                                s["value"],
                                traffic_light_code=s.get("traffic_light"),
                                icon_code=s.get("icon"),
                                trend = s.get("trend"),
                                label = s.get("label"))
        for gurl, g in w["graph_data"].items():
            try:
                graph = GraphDefinition.objects.get(tile__widget=wd, tile__url=gurl)
            except GraphDefinition.DoesNotExist:
                raise ImportExportException("Graph %s for widget %s(%s,%s) does not exist" % (
                                    gurl,
                                    data["family"], 
                                    w["actual_location"],
                                    w["actual_frequency"]))
            clear_graph_data(graph)
            if graph.use_clusters():
                for curl, c in g["data"].items():
                    for dsurl, ds in c.items():
                        add_graph_data(graph, dsurl, ds, cluster=curl)
            else:
                for dsurl, ds in g["data"].items():
                    for d in ds:
                        hval = d[0]
                        val = d[1]
                        if graph.horiz_axis_type == graph.DATE:
                            hval = parse_date(hval)
                        elif graph.horiz_axis_type == graph.TIME:
                            hval = parse_time(hval)
                        add_graph_data(graph, dsurl, val, horiz_value=hval)
    return family