#   Copyright 2016 CSIRO
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
from disability_social_participation_uploader.models import *
from coag_uploader.uploader import load_state_grid, load_benchmark_description, update_graph_data, populate_raw_data, populate_crosstab_raw_data, update_stats, update_state_stats, indicator_tlc_trend
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
                            ('B', 'Row Discriminator ("%" or "+")'),
                            ('...', 'Column per state + Aust'),
                        ],
                "rows": [
                            ('1', "Heading row"),
                            ('2', "State Heading row"),
                            ('...', 'Pair of rows per year, one for percentage (%) and one for uncertainty (%)'),
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
                            ('Status', 'Indicator status'),
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

indicators = "Increase the proportion of people with disabilirt participating in social and community activities"

def upload_file(uploader, fh, actual_freq_display=None, verbosity=0):
    messages = []
    try:
        if verbosity > 0:
            messages.append("Loading workbook...")
        wb = load_workbook(fh, read_only=True)
        messages.extend(
                load_state_grid(wb, "Data",
                                "Disability", "Social Participation",
                                None, DisabilitySocialParticipationData,
                                {}, {"percentage": "%", "uncertainty": "+",},
                                verbosity))
        desc = load_benchmark_description(wb, "Description", indicator=True)
        messages.extend(update_stats(desc, indicators,
                                "social_participation-disability-hero", "social_participation-disability-hero", 
                                "social_participation-disability-hero-state", "social_participation-disability-hero-state", 
                                None, None,
                                None, None,
                                verbosity))
        messages.extend(update_state_stats(
                                "social_participation-disability-hero-state", "social_participation-disability-hero-state", 
                                None, None,
                                DisabilitySocialParticipationData, "percentage", "uncertainty",
                                verbosity=verbosity))
        earliest_aust = DisabilitySocialParticipationData.objects.filter(state=AUS).order_by("year").first()
        latest_aust = DisabilitySocialParticipationData.objects.filter(state=AUS).order_by("year").last()
        tlc, trend = indicator_tlc_trend(earliest_aust.percentage, latest_aust.percentage)

        set_statistic_data('social_participation-disability-hero', 'social_participation-disability-hero',
                        'ref_participation',
                        earliest_aust.percentage,
                        traffic_light_code=tlc,
                        label=earliest_aust.year_display()
                        )
        set_statistic_data('social_participation-disability-hero', 'social_participation-disability-hero',
                        'curr_participation',
                        latest_aust.percentage,
                        traffic_light_code=tlc,
                        trend=trend,
                        label=latest_aust.year_display())
        p = Parametisation.objects.get(url="state_param")
        for pval in p.parametisationvalue_set.all():
            state_num = state_map[pval.parameters()["state_abbrev"]]
            earliest_state = DisabilitySocialParticipationData.objects.filter(state=state_num).order_by("year").first()
            latest_state = DisabilitySocialParticipationData.objects.filter(state=state_num).order_by("year").last()
            tlc_state, trend_state = indicator_tlc_trend(earliest_state.percentage, latest_state.percentage)

            set_statistic_data('social_participation-disability-hero-state', 'social_participation-disability-hero-state',
                            'ref_year',
                            earliest_aust.year_display(),
                            pval=pval)
            set_statistic_data('social_participation-disability-hero-state', 'social_participation-disability-hero-state',
                            'curr_year',
                            latest_aust.year_display(),
                            pval=pval)
            set_statistic_data('social_participation-disability-hero-state', 'social_participation-disability-hero-state',
                            'ref_participation',
                            earliest_aust.percentage,
                            traffic_light_code=tlc,
                            pval=pval)
            set_statistic_data('social_participation-disability-hero-state', 'social_participation-disability-hero-state',
                            'curr_participation',
                            latest_aust.percentage,
                            traffic_light_code=tlc,
                            trend=trend,
                            pval=pval)
            set_statistic_data('social_participation-disability-hero-state', 'social_participation-disability-hero-state',
                            'ref_participation_state',
                            earliest_state.percentage,
                            traffic_light_code=tlc_state,
                            pval=pval)
            set_statistic_data('social_participation-disability-hero-state', 'social_participation-disability-hero-state',
                            'curr_participation_state',
                            latest_state.percentage,
                            traffic_light_code=tlc_state,
                            trend=trend_state,
                            pval=pval)
    except LoaderException, e:
        raise e
    except Exception, e:
        raise LoaderException("Invalid file: %s" % unicode(e))
    return messages

