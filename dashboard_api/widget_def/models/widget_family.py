#   Copyright 2015,2016,2017 CSIRO
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

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, Group

from widget_def.models.reference import Subcategory
from widget_def.models.widget_definition import WidgetDefinition
from widget_def.model_json_tools import *

# Create your models here.

class WidgetFamily(models.Model, WidgetDefJsonMixin):
    """
    Represents a family of closely related widgets. 

    When you have two widgets in two views with the same heading and subheading but which require slightly different
    presentation and data, consider making them a widget family.
    """
    export_def = {
        ("category", "subcategory"): JSON_SIMPLE_LOOKUP_WRAPPER(attribute="subcategory", 
                                                null=False,
                                                exporters=(
                                                    lambda o: o.category.name,
                                                    lambda o: o.name,
                                                ),
                                                model="Subcategory",
                                                app="widget_def",
                                                importer_kwargs=lambda js: {
                                                    "name": js["subcategory"],
                                                    "category__name": js["category"]
                                                }),
        "subtitle": JSON_ATTR(),
        "name": JSON_ATTR(),
        "url": JSON_ATTR(),
        "source_url": JSON_ATTR(),
        "source_url_text": JSON_ATTR(),
        "groups": JSON_MANYTOMANY_REF("name", "Group", "auth", manager_chain=["edit_permission", "group_set"]),
        "edit_all_groups": JSON_MANYTOMANY_REF("name", "Group", "auth", manager_chain=["edit_all_permission", "group_set"]),
        "definitions": JSON_RECURSEDOWN("WidgetDefinition", "definitions", "family", "label", app="widget_def")
    }
    export_lookup={ "url": "url" }
    subcategory = models.ForeignKey(Subcategory, help_text="The subcategory (and therefore category) of the widget family")
    name = models.CharField(max_length=120, help_text="The name (main heading) of widgets in this family. May be parametised.")
    subtitle = models.CharField(max_length=240, null=True, blank=True, help_text="The option subheading of widgets in this family. May be parametised.")
    url  = models.SlugField(unique=True, help_text="A short symbolic name used to refer to widgets in this family in the API. May be parametised.")
    source_url = models.URLField(max_length=400, help_text="An external URL that the user can be directed to for more information.  Typically the canonical source for the widget's data. May be parametised.")
    source_url_text = models.CharField(max_length=60, help_text="The text for the source_url link. May be parametised.")
    class Meta:
        ordering=("subcategory",)
    def edit_permission_name(self):
        """
            Returns the name of the django auth permission required to manually edit the 
            editable data for this widget family.
        """
        return "w_%s" % self.url
    def edit_permission_label(self):
        """
            Returns the label of the django auth permission required to manually edit the 
            editable data for this widget family.
        """
        p = self.edit_permission()
        return "%s.%s" % (p.content_type.app_label, p.codename) 
    def edit_permission(self, log=None):
        """
            Returns the actual :model:`auth.Permission` permission object required to manually edit 
            the editable data for this widget family, creating it if it does not already exist.
        """
        ct = ContentType.objects.get_for_model(self)
        try:
            p = Permission.objects.get(content_type=ct, codename=self.edit_permission_name())
        except Permission.DoesNotExist:
            p = Permission(content_type=ct, codename=self.edit_permission_name(),
                            name="Edit data for widget %s" % self.name)
            p.save()
            if log is not None:
                print >> log, "Created permission for widget %s" % self.name
        return p
    def edit_all_permission_name(self):
        """
            Returns the name of the django auth permission required to manually edit 
            all data for this widget family.
        """
        return "wa_%s" % self.url
    def edit_all_permission_label(self):
        """
            Returns the label of the django auth permission required to manually edit 
            all data for this widget family.
        """
        p = self.edit_all_permission()
        return "%s.%s" % (p.content_type.app_label, p.codename) 
    def edit_all_permission(self, log=None):
        """
            Returns the actual :model:`auth.Permission` permission object required to manually edit 
            all data for this widget family, creating it if it does not already exist.
        """
        ct = ContentType.objects.get_for_model(self)
        try:
            p = Permission.objects.get(content_type=ct, codename=self.edit_all_permission_name())
        except Permission.DoesNotExist:
            p = Permission(content_type=ct, codename=self.edit_all_permission_name(),
                            name="Edit all data for widget %s" % self.name)
            p.save()
            if log is not None:
                print >> log, "Created edit all permission for widget %s" % self.name
        return p
    def __unicode__(self):
        if self.subtitle:
            return "%s (%s)" % (self.name, self.subtitle)
        else:
            return self.name

