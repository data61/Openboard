#   Copyright 2015 NICTA
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

from django.db import models

# Create your models here.

class WidgetData(models.Model):
    widget = models.ForeignKey("widget_def.WidgetDefinition")
    param_value = models.ForeignKey("widget_def.ParameterValue", blank=True, null=True)
    actual_frequency_text = models.CharField(max_length=60, blank=True, null=True)
    class Meta:
        unique_together = [
                ("widget", "param_value"),
        ]
