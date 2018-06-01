#   Copyright 2016,2017 CSIRO
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.



import datetime
import csv
from decimal import Decimal, ROUND_HALF_UP
import re
from openpyxl import load_workbook
from dashboard_loader.loader_utils import *
from coag_uploader.models import *
from housing_remote_indigenous_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_crosstab_raw_data, populate_raw_data, update_stats, update_state_stats
from django.template import Template, Context
from widget_def.models import Parametisation

# These are the names of the groups that have permission to upload data for this uploader.
# If the groups do not exist they are created on registration.
groups = [ "upload_all", "upload" ]

# This describes the file format.  It is used to describe the format by both
# "python manage.py upload_data frontlineservice_uploader" and by the uploader 
# page in the data admin GUI.

file_format = {
    "format": "xlsx",
    "sheets": [
            {
                "name": "Data",
                "cols": [ 
                            ('A', 'Year e.g. 2007-08 or 2007/08 or 2007'),
                            ('B', 'Row Discriminator ("New houses", or "Refurbishments")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Pairs of rows per year, one for new homes (New), one for refurbishments (Refurbishments).'),
                        ],
                "notes": [
                    'Blank rows and columns ignored',
                ],
            },
            {
                "name": "Description",
                "cols": [
                            ('A', 'Key'),
                            ('B', 'Value'),
                        ],
                "rows": [
                            ('Status', 'Benchmark status'),
                            ('Updated', 'Year data last updated'),
                            ('Desc body', 'Body of benchmark status description. One paragraph per line.'),
                            ('Influences', '"Influences" text of benchmark status description. One paragraph per line (optional)'),
                            ('Other Benchmarks', '(optional) Description and results or other benchmark(s) under the national partnership agreement that do not have their own widget(s).'),
                            ('Notes', 'Notes for benchmark status description.  One note per line.'),
                        ],
                "notes": [
                         ],
            }
        ],
}

def state_benchmarker(obj):
    if obj.state == WA:
        return "not_on_track"
    elif obj.state in (TAS, NSW):
        return "no_participate"
    else:
        return "on_track"

new_house_targets = {
    AUS: 4200,
    NSW: 310,
    QLD: 1141,
    WA: 1012,
    SA: 241,
    TAS: 18,
    NT: 1456,
}
new_house_target_year = 2018

refurbishment_targets = {
    AUS: 4876,
    NSW: 101,
    QLD: 1216,
    WA: 1288,
    SA: 206,
    TAS: 3,
    NT: 2052,
}
refurbishment_target_year = 2014

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    # try
    if verbosity > 0:
        messages.append("Loading workbook...")
    wb = load_workbook(fh, read_only=True)
    messages.extend(
            load_state_grid(wb, "Data",
                            "Housing", "Remote Indigenous Housing",
                            None, HousingRemoteIndigenousData,
                            {}, {
                                "new_houses": "New houses",
                                "refurbishments": "Refurbishments",
                            },
                            verbosity=verbosity)
    )
    desc = load_benchmark_description(wb, "Description")
    messages.extend(update_stats(desc, None,
                        "indigenous_remote-housing-hero", "indigenous_remote-housing-hero",
                        "indigenous_remote-housing-hero-state", "indigenous_remote-housing-hero-state",
                        "housing_remote_indigenous", "housing_remote_indigenous",
                        "housing_remote_indigenous_state", "housing_remote_indigenous_state",
                        verbosity))
    messages.extend(update_state_stats(
                "indigenous_remote-housing-hero-state", "indigenous_remote-housing-hero-state",
                "housing_remote_indigenous_state", "housing_remote_indigenous_state",
                HousingRemoteIndigenousData, [],
                use_benchmark_tls=True,
                status_func=state_benchmarker,
                verbosity=verbosity))
    messages.extend(update_summary_graph_data(
                "indigenous_remote-housing-hero",
                "indigenous_remote-housing-hero",
                "housing-rih-hero-graph"))
    messages.extend(update_summary_graph_data(
                "housing_remote_indigenous",
                "housing_remote_indigenous",
                "housing_remote_indigenous_summary_graph"))
    messages.extend(update_detail_graph_data())
    messages.extend(
            generate_csv_data("housing_remote_indigenous", "housing_remote_indigenous",
                          "housing_indigenous_remote", None)
            )
    messages.extend(
            generate_csv_datatable("housing_remote_indigenous", "housing_remote_indigenous",
                                   "data_table", None)
            )
    p = Parametisation.objects.get(url="state_param")
    for pval in p.parametisationvalue_set.all():
        state_num = state_map[pval.parameters()["state_abbrev"]]
        messages.extend(update_summary_graph_data(
                    "indigenous_remote-housing-hero-state",
                    "indigenous_remote-housing-hero-state",
                    "housing-rih-hero-graph",
                    pval=pval))
        messages.extend(update_summary_graph_data(
                    "housing_remote_indigenous_state",
                    "housing_remote_indigenous_state",
                    "housing_remote_indigenous_summary_graph",
                    pval=pval))
        messages.extend(update_detail_state_graph_data(pval))
        messages.extend(
                generate_csv_data("housing_remote_indigenous_state", "housing_remote_indigenous_state",
                          "housing_indigenous_remote", pval)
                )
        messages.extend(
                generate_csv_datatable("housing_remote_indigenous_state", "housing_remote_indigenous_state",
                                   "data_table", pval)
                )
  #  except LoaderException, e:
  #      raise e
  #  except Exception, e:
  #      raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_summary_graph_data(wurl, wlbl, graph_lbl, pval=None):
    messages = []
    g = get_graph(wurl, wlbl, graph_lbl)
    clear_graph_data(g, pval=pval)
    if pval:
        state_abbrev = pval.parameters()["state_abbrev"]
        state_num = state_map[state_abbrev]
        if state_num not in new_house_targets:
            messages.append("No target for %s, skipping" % state_abbrev)
            return messages
        add_graph_data(g, "benchmark", new_house_targets[AUS], cluster="new", pval=pval)
        add_graph_data(g, "benchmark", refurbishment_targets[AUS], cluster="refurbished", pval=pval)
        add_graph_data(g, "state_benchmark", new_house_targets[state_num], cluster="new", pval=pval)
        add_graph_data(g, "state_benchmark", refurbishment_targets[state_num], cluster="refurbished", pval=pval)
    else:
        add_graph_data(g, "benchmark", new_house_targets[AUS], cluster="new", pval=pval)
        add_graph_data(g, "benchmark", refurbishment_targets[AUS], cluster="refurbished", pval=pval)

    data = HousingRemoteIndigenousData.objects.filter(state=AUS).order_by("year").last()
    add_graph_data(g, "year", data.new_houses, cluster="new", pval=pval)
    add_graph_data(g, "year", data.refurbishments, cluster="refurbished", pval=pval)
    yr = data.year_display()
    if pval:
        set_dataset_override(g, "year", "%s (Nat)" % data.year_display(), pval=pval)
        data = HousingRemoteIndigenousData.objects.filter(state=state_num).order_by("year").last()
        if data is not None:
            add_graph_data(g, "year_state", data.new_houses, cluster="new", pval=pval)
            add_graph_data(g, "year_state", data.refurbishments, cluster="refurbished", pval=pval)
            set_dataset_override(g, "year_state", "%s (%s)" % (data.year_display(), state_abbrev), pval=pval)
        else:
            set_dataset_override(g, "year_state", "%s (%s)" % (yr, state_abbrev), pval=pval)
    else:
        set_dataset_override(g, "year", data.year_display())
    return messages

def update_detail_graph_data():
    messages = []
    g = get_graph("housing_remote_indigenous", "housing_remote_indigenous",
                        "housing_remote_indigenous_detail_graph")
    clear_graph_data(g)
    year = 0
    for data in HousingRemoteIndigenousData.objects.exclude(state=AUS).order_by("-year"):
        if year and year != data.year:
            break
        year = data.year
        add_graph_data(g, "new", data.new_houses, cluster=data.state_display().lower())
        add_graph_data(g, "refurbished", data.refurbishments, cluster=data.state_display().lower())
    return messages

def update_detail_state_graph_data(pval):
    messages = []
    state_abbrev = pval.parameters()["state_abbrev"]
    state_num = state_map[state_abbrev]
    if state_num not in new_house_targets:
        messages.append("No target for %s, skipping" % state_abbrev)
        return messages
    g = get_graph("housing_remote_indigenous_state", "housing_remote_indigenous_state",
                        "housing_remote_indigenous_detail_graph")
    clear_graph_data(g, pval=pval)
    year = 0
    add_graph_data(g, "refurbished_benchmark", refurbishment_targets[state_num], cluster="state", pval=pval)
    add_graph_data(g, "refurbished_benchmark", refurbishment_targets[AUS], cluster="australia", pval=pval)
    add_graph_data(g, "new_benchmark", new_house_targets[state_num], cluster="state", pval=pval)
    add_graph_data(g, "new_benchmark", new_house_targets[AUS], cluster="australia", pval=pval)
    for data in HousingRemoteIndigenousData.objects.filter(state__in=[AUS, state_num]).order_by("-year"):
        if year and year != data.year:
            break
        year = data.year
        if data.state == AUS:
            cluster = "australia"
        else:
            cluster = "state"
        add_graph_data(g, "new", data.new_houses, cluster=cluster, pval=pval)
        add_graph_data(g, "refurbished", data.refurbishments, cluster=cluster, pval=pval)
    return messages

def generate_csv_datatable(w_url, w_lbl, rds_lbl, pval):
    messages = []
    rds = get_rawdataset(w_url, w_lbl, rds_lbl)
    clear_rawdataset(rds, pval=pval)
    sort_order = 1
    kwargs = { "year": None }
    for obj in HousingRemoteIndigenousData.objects.order_by("year", "financial_year", "state"):
        if obj.year_display() != kwargs["year"]:
            if kwargs["year"]:
                add_rawdatarecord(rds, sort_order, **kwargs)
                sort_order += 1
            kwargs = {}
            kwargs["year"] = obj.year_display()
            if pval:
                kwargs["pval"] = pval
        jurisdiction = obj.state_display().lower()
        kwargs[jurisdiction + "_new"] = obj.new_houses
        kwargs[jurisdiction + "_refurbished"] = obj.refurbishments
    if kwargs["year"]:
        add_rawdatarecord(rds, sort_order, **kwargs)
    sort_order += 1
    kwargs = {
                "year": "Target",
                "pval": pval,
    }
    for state_num in new_house_targets.keys():
        state_name = state_dict[state_num].lower()
        kwargs[state_name + "_new"] = new_house_targets[state_num]
        kwargs[state_name + "_refurbished"] = refurbishment_targets[state_num]
    add_rawdatarecord(rds, sort_order, **kwargs)
    return messages

def generate_csv_data(w_url, w_lbl, rds_lbl, pval):
    messages = []
    rds = get_rawdataset(w_url, w_lbl, rds_lbl)
    clear_rawdataset(rds, pval=pval)
    sort_order = 1
    for obj in HousingRemoteIndigenousData.objects.order_by("state", "year", "financial_year"):
        kwargs = {}
        kwargs["year"] = obj.year_display()
        kwargs["jurisdiction"] = obj.state_display()
        kwargs["new"] = obj.new_houses
        kwargs["refurbished"] = obj.refurbishments
        add_rawdatarecord(rds, sort_order, **kwargs)
        sort_order += 1

    for state_num in new_house_targets.keys():
        state_name = state_dict[state_num]
        add_rawdatarecord(rds, sort_order,
                                year="Target",
                                jurisdiction=state_name,
                                new=new_house_targets[state_num],
                                refurbished=refurbishment_targets[state_num])
        sort_order += 1

    return messages