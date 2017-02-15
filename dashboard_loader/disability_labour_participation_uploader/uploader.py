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
from disability_labour_participation_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data, populate_crosstab_raw_data, update_stats, update_state_stats
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
                            ('B', 'Row Discriminator ("People with disability aged 15-64 years in the labour force (%)", "Confidence Interval", "Male (%)", "Male (Confidence Interval)", "Female (%)" or "Female (Confidence Interval)")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Six rows per year, one for each row discriminator value.  Note that Male and Female data may not be available at the state level.'),
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
                            ('Measure', 'Full description of benchmark'),
                            ('Short Title', 'Short widget title (not used)'),
                            ('Status', 'Benchmark status'),
                            ('Updated', 'Year data last updated'),
                            ('Desc body', 'Body of benchmark status description. One paragraph per line.'),
                            ('Influences', '"Influences" text of benchmark status description. One paragraph per line'),
                            ('Notes', 'Notes for benchmark status description.  One note per line.'),
                        ],
                "notes": [
                         ],
            }
        ],
}

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Disability", "Labour Force Participation",
                                None, DisabilityLabourParticipation,
                                {}, {
                                    "percentage": "People with disability aged 15-64 years in the labour force (%)", 
                                    "uncertainty": "Confidence Interval", 
                                    "rse": "RSE", 
                                    "percentage_male": "Male (%)", 
                                    "uncertainty_male": "Male (Confidence Interval)", 
                                    "percentage_female": "Female (%)",
                                    "uncertainty_female": "Female (Confidence Interval)",
                                },
                                verbosity=verbosity)
        )
        desc = load_benchmark_description(wb, "Description")
        messages.extend(update_stats(desc, None,
                                "labour_participation-disability-hero", "labour_participation-disability-hero",  
                                "labour_participation-disability-hero-state", "labour_participation-disability-hero-state",  
                                "disability_labour_participation", "disability_labour_participation",  
                                "disability_labour_participation_state", "disability_labour_participation_state",
                                verbosity))
        messages.extend(update_state_stats(
                                "labour_participation-disability-hero-state", "labour_participation-disability-hero-state",  
                                "disability_labour_participation_state", "disability_labour_participation_state",
                                DisabilityLabourParticipation, [("percentage", "uncertainty", "rse"),],
                                verbosity=verbosity))
        messages.extend(
                update_gender_graph(
                            "labour_participation-disability-hero", "disability-labour_participation-hero-graph",
                            benchmark_start=2009.0,
                            benchmark_end=2018.0,
                            benchmark_gen=lambda init: Decimal("5.0") + init,
                            use_error_bars=False,
                            verbosity=verbosity)
        )
        messages.extend(
                update_gender_graph(
                            "disability_labour_participation", "disability_labour_participation_summary_graph",
                            benchmark_start=2009.0,
                            benchmark_end=2018.0,
                            benchmark_gen=lambda init: Decimal("5.0") + init,
                            use_error_bars=False,
                            verbosity=verbosity)
        )
        messages.extend(
                update_graph_data(
                            "disability_labour_participation", "disability_labour_participation", 
                            "disability_labour_participation_detail_graph",
                            DisabilityLabourParticipation, "percentage",
                            benchmark_start=2009.0,
                            benchmark_end=2018.0,
                            benchmark_gen=lambda init: Decimal("5.0") + init,
                            use_error_bars=True,
                            verbosity=verbosity)
        )
        messages.extend(
                populate_raw_data(
                            "disability_labour_participation", "disability_labour_participation", 
                            "disability_labour_participation", DisabilityLabourParticipation, 
                                {
                                    "percentage": "disabled_labour_force_participation",
                                    "uncertainty": "uncertainty",
                                    "percentage_male": "disabled_male_labour_force_participation",
                                    "uncertainty_male": "uncertainty",
                                    "percentage_female": "disabled_female_labour_force_participation",
                                    "uncertainty_female": "uncertainty",
                                })
                )
        messages.extend(
                populate_crosstab_raw_data(
                            "disability_labour_participation", "disability_labour_participation", 
                                "data_table", DisabilityLabourParticipation, 
                                {
                                    "percentage": "percent",
                                    "uncertainty": "error",
                                    "percentage_male": "males_percent",
                                    "uncertainty_male": "males_error",
                                    "percentage_female": "females_percent",
                                    "uncertainty_female": "females_error",
                                },
                                field_map_states = {
                                    "percentage": "percent",
                                    "uncertainty": "error",
                                })
                )
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            messages.extend(
                    update_graph_data(
                                "labour_participation-disability-hero-state", "labour_participation-disability-hero-state", 
                                "disability-labour_participation-hero-graph",
                                DisabilityLabourParticipation, "percentage",
                                [ AUS, state_num ],
                                benchmark_start=2009.0,
                                benchmark_end=2018.0,
                                benchmark_gen=lambda init: Decimal("5.0") + init,
                                use_error_bars=False,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                    update_graph_data(
                                "disability_labour_participation_state", "disability_labour_participation_state", 
                                "disability_labour_participation_summary_graph",
                                DisabilityLabourParticipation, "percentage",
                                [ AUS, state_num ],
                                benchmark_start=2009.0,
                                benchmark_end=2018.0,
                                benchmark_gen=lambda init: Decimal("5.0") + init,
                                use_error_bars=False,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                    update_graph_data(
                                "disability_labour_participation_state", "disability_labour_participation_state", 
                                "disability_labour_participation_detail_graph",
                                DisabilityLabourParticipation, "percentage",
                                benchmark_start=2009.0,
                                benchmark_end=2018.0,
                                benchmark_gen=lambda init: Decimal("5.0") + init,
                                use_error_bars=True,
                                verbosity=verbosity,
                                pval=pval)
            )
            messages.extend(
                    populate_raw_data(
                                "disability_labour_participation_state", "disability_labour_participation_state", 
                                "disability_labour_participation", DisabilityLabourParticipation, 
                                    {
                                        "percentage": "disabled_labour_force_participation",
                                        "uncertainty": "uncertainty",
                                        "percentage_male": "disabled_male_labour_force_participation",
                                        "uncertainty_male": "uncertainty",
                                        "percentage_female": "disabled_female_labour_force_participation",
                                        "uncertainty_female": "uncertainty",
                                    }, pval=pval)
                    )
            messages.extend(
                    populate_crosstab_raw_data(
                                "disability_labour_participation_state", "disability_labour_participation_state", 
                                    "data_table", DisabilityLabourParticipation, 
                                    {
                                        "percentage": "percent",
                                        "uncertainty": "error",
                                        "percentage_male": "males_percent",
                                        "uncertainty_male": "males_error",
                                        "percentage_female": "females_percent",
                                        "uncertainty_female": "females_error",
                                    },
                                    field_map_states = {
                                        "percentage": "percent",
                                        "uncertainty": "error",
                                    }, pval=pval)
                    )
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

def update_gender_graph(wurl, graph, 
                    benchmark_start=None, benchmark_end=None, benchmark_gen=lambda x:x, 
                    use_error_bars=False, verbosity=0, pval=None):
    messages=[]
    g = get_graph(wurl, wurl, graph)
    clear_graph_data(g, pval=pval)
    qry = DisabilityLabourParticipation.objects.filter(state=AUS)
    benchmark_init = None
    benchmark_final = None
    for o in qry:
        if o.state == AUS and o.float_year() == benchmark_start:
            benchmark_init = o.percentage
            benchmark_final = benchmark_gen(benchmark_init)
        kwargs = {}
        kwargs["horiz_value"] = o.year_as_date()
        if use_error_bars:
            kwargs["val_min"] = o.percentage-o.uncertainty
            kwargs["val_max"] = o.percentage+o.uncertainty
        if pval is not None:
            kwargs["pval"] = pval
        add_graph_data(g, "australia", o.percentage,
                **kwargs)
        if use_error_bars:
            kwargs["val_min"] = o.percentage_male-o.uncertainty_male
            kwargs["val_max"] = o.percentage_male+o.uncertainty_male
        add_graph_data(g, "male", o.percentage_male,
                **kwargs)
        if use_error_bars:
            kwargs["val_min"] = o.percentage_female-o.uncertainty_female
            kwargs["val_max"] = o.percentage_female+o.uncertainty_female
        add_graph_data(g, "female", o.percentage_female,
                **kwargs)
    if benchmark_init is not None and benchmark_final is not None :
        add_graph_data(g, "benchmark",
                    benchmark_init,
                    horiz_value=float_year_as_date(benchmark_start),
                    pval=pval)
        add_graph_data(g, "benchmark",
                    benchmark_final,
                    horiz_value=float_year_as_date(benchmark_end),
                    pval=pval)
    if verbosity > 1:
        if pval:
            messages.append("Graph %s (%s) updated" % (graph, pval.parameters()["state_abbrev"]))
        else:
            messages.append("Graph %s updated" % graph)
    return messages
                
