#   Copyrigh 2017 CSIRO
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

import decimal

from django.db.models import Model, Max
from django.db.utils import IntegrityError
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist 
from django.db.models.manager import BaseManager

from dashboard_api.management.exceptions import ImportExportException
from widget_def.parametisation import parametise_label

def call_or_get_attr(obj, name):
    a = getattr(obj, name)
    if callable(a) and not isinstance(a, BaseManager):
        return a()
    else:
        return a

class JSON_ATTR(object):
    """Default handler.  Just use the attribute"""
    def __init__(self, attribute=None, parametise=False, solo=False, default=None, importer=None, exporter=None, decider=None, suppress_decider=None, deciders=None, self_decide=False):
        self.attribute = attribute
        self.parametise = parametise
        self.solo = solo
        self.importer = importer
        self.default = default
        self.exporter = exporter
        self.self_decide = self_decide
        self.decider = decider
        self.deciders = deciders
        self.suppress_decider = suppress_decider
    def suppress_export(self, obj, key):
        if self.self_decide and not bool(call_or_get_attr(obj, key)):
            return True
        if self.decider:
            if isinstance(self.decider, basestring):
                if not call_or_get_attr(obj, self.decider):
                    return True
            else:
                try:
                    decider_list = list(self.decider)
                    o = obj
                    for decider_element in decider_list:
                        o = call_or_get_attr(o, decider_element)
                    if not o:
                       return True 
                except TypeError:
                    raise ImportExportException("decider not iterable")
        if self.deciders:
            for d in self.deciders:
                if not call_or_get_attr(obj, d):
                    return True
        if self.suppress_decider and call_or_get_attr(obj, self.suppress_decider):
            return True
        return False
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        if not self.suppress_export(obj, key):
            self._handle_export(obj, export, key, env, recurse_func, **kwargs)
    def _handle_export(self, obj, export, key, env, recurse_func, **kwargs):
        if self.attribute:
            attr = self.attribute
        else:
            attr = key
        if self.exporter:
            if attr=="self":
                export[key] = self.exporter(obj)
            else:
                export[key] = self.exporter(getattr(obj, attr))
        else:
            export[key] = call_or_get_attr(obj, attr)
        if self.parametise:
            export[key] = self.apply_parametisation(obj, export[key], **kwargs)
        if self.solo:
            env["single_export_field"] = key
        return
    def attr_name(self, key):
        if self.attribute:
            return self.attribute
        else:
            return key
    def apply_parametisation(self, obj, val, **kwargs):
        parametisation_or_widget = kwargs.get("parametisation") 
        view = kwargs.get("view")
        if view is None and parametisation_or_widget is None:
            raise ImportExportException("Cannot determine which parametisation to use")
        return parametise_label(parametisation_or_widget, view, val)
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        if self.parametise:
            raise ImportExportException("Cannot perform import on a parametised export")
        if self.solo:
            val = js
        else:
            val = js.get(key, self.default)
        if self.importer:
            val = self.importer(val)   
        if self.attribute:
            cons_args[self.attribute] = val
        else:
            cons_args[key] = val
    def recurse_import(self, js, obj, key, imp_kwargs, env, do_not_delete=False):
        pass

class JSON_EXPORT_DICT(JSON_ATTR):
    def __init__(self, exp_dict, deciders=None):
        self.exp_dict = exp_dict
        self.deciders = deciders
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        doit = True
        if self.deciders:
            for d in self.deciders:
                doit = call_or_get_attr(obj, d)
                if callable(doit):
                    doit = doit()
                if not doit:
                    break
        if doit:
            export[key] = {}
            for k, v in self.exp_dict.items():
                v.handle_export(obj, export[key], k, env, recurse_func, **kwargs)
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        pass

class JSON_CONST(JSON_ATTR):
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        export[key] = self.default
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        pass

class JSON_EXP_ARRAY_LOOKUP(JSON_ATTR):
    def __init__(self, lookup_array, *args, **kwargs):
        super(JSON_EXP_ARRAY_LOOKUP, self).__init__(*args, **kwargs)
        self.lookup_array = lookup_array
    def _handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        if self.attribute:
            export[key] = self.lookup_array[call_or_get_attr(obj, self.attribute)]
        else:
            export[key] = self.lookup_array[call_or_get_attr(obj, key)]
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        pass

class JSON_CONDITIONAL_EXPORT(JSON_ATTR):
    def __init__(self, condition, yes, no):
        self.condition = condition
        self.yes = yes
        self.no = no
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        if self.condition(obj, kwargs):
            self.yes.handle_export(obj, export, key, env, recurse_func, **kwargs)
        else:
            self.no.handle_export(obj, export, key, env, recurse_func, **kwargs)
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        pass

class JSON_COMPLEX_IMPORTER_ATTR(JSON_ATTR):
    def __init__(self, complex_importer=None, **kwargs):
        super(JSON_COMPLEX_IMPORTER_ATTR, self).__init__(**kwargs)
        self.complex_importer = complex_importer
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        self.complex_importer(js, cons_args, imp_kwargs)

class JSON_MANYTOMANY_REF(JSON_ATTR):
    def __init__(self, refattr, model, app, manager_chain=[], **kwargs):
        self.refattr=refattr
        self.manager_chain=manager_chain
        self.model = model
        self.app = app
        super(JSON_MANYTOMANY_REF, self).__init__(**kwargs)
    def get_manager(self, obj, key):
        if self.manager_chain:
            mgr = obj
            for elem in self.manager_chain:
                mgr = call_or_get_attr(mgr, elem)
            return mgr
        else:
            return getattr(obj, self.attr_name(key))
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        m2m_mgr = self.get_manager(obj, key)
        export[key]=[ getattr(o, self.refattr) for o in m2m_mgr.all() ]
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        env["m2m_js"] = js[key]
    def recurse_import(self,js, obj, key, imp_kwargs, env, do_not_delete=False):
        m2m_mgr = self.get_manager(obj, key)
        m2m_mgr.clear()
        for ref in env["m2m_js"]:
            get_kwargs = { self.refattr: ref }
            obj = self.get_model().objects.get(**get_kwargs)
            m2m_mgr.add(obj)
    #TODO Defined elsewhere. make it a mixin.
    def get_model(self):
        if self.app:
            return apps.get_app_config(self.app).get_model(self.model)
        else:
            return self.model
            
class JSON_PASSDOWN(JSON_ATTR):
    def __init__(self, optional=False, model=None, app=None, related_attr=None, extend=None, **kwargs):
        super(JSON_PASSDOWN, self).__init__(**kwargs)
        self.optional = optional
        self.model = model
        self.app = app
        self.related_attr = related_attr
        self.extend = extend
    def _handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        try:
            if self.attribute:
                val = call_or_get_attr(obj, self.attribute)
            else:
                val = call_or_get_attr(obj, key)
        except AttributeError:
            if self.optional:
                return
            raise
        if val is None:
            export[key] = val
        else:
            val = getattr(val, recurse_func)(**kwargs)
            export[key] = val
        if self.solo:
            env["single_export_field"] = key
        if self.extend:
            for subkey, handler in self.extend.items():
                handler.handle_export(obj, export[key], subkey, env, recurse_func, **kwargs)
        return
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        if self.extend:
            raise ImportExportException("Cannot import extended passdowns")
        env["save"] = True
    def get_model(self):
        if self.app:
            return apps.get_app_config(self.app).get_model(self.model)
        else:
            return self.model
    def recurse_import(self,js, obj, key, imp_kwargs, env, do_not_delete=False):
        model = self.get_model()
        try:
            kwargs = {
                "js": js[key]
            }
        except KeyError:
            if self.optional:
                return
            raise ImportExportException("Non optional passdown is missing")
        if self.related_attr:
            kwargs[self.related_attr] = obj
        else:
            kwargs[key] = obj
        model.import_data(**kwargs)
        return 

class JSON_STRINGIFY_ATTR(JSON_ATTR):
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        if self.attribute:
            export[key] = unicode(getattr(obj, self.attribute))
        else:
            export[key] = unicode(getattr(obj, key))
        return
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        pass

class JSON_CAT_LOOKUP(JSON_ATTR):
    def __init__(self, lookup_fields, imp_lookup, import_model=None, optional=False, attribute=None):
        super(JSON_CAT_LOOKUP, self).__init__(attribute=attribute)
        self.fields=lookup_fields
        self.imp_lookup=imp_lookup
        self.optional = optional
        self.import_model = import_model
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        o = obj
        for fld in self.fields:
            o = getattr(o, fld)
            if o is None:
                if not self.optional:
                    export[key] = None
                return
            if callable(o):
                o = o()
        export[key] = o
        return 
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        try:
            obj = self.imp_lookup(js, key, imp_kwargs)
        except KeyError:
            obj = None
        except ObjectDoesNotExist:
            if js[key] is None:
                obj = None
            elif self.import_model and key:
                obj=self.import_model.import_data(js=js[key])
            elif self.import_model:
                obj=self.import_model.import_data(js=js)
            else:
                raise
        if self.attribute:
            cons_args[self.attribute] = obj
        else:
            cons_args[key] = obj

class JSON_NUM_ATTR(JSON_ATTR):
    def __init__(self, precision, allow_int=True, default=None, attribute=None):
        self.precision = precision
        self.allow_int=allow_int
        super(JSON_NUM_ATTR, self).__init__(attribute=attribute, default=default)
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        if self.attribute:
            attrval = getattr(obj, self.attribute)
        else:
            attrval = getattr(obj, key)
        if attrval is None:
            export[key] = None
        elif self.allow_int and attrval == attrval.to_integral_value():
            export[key] = int(attrval)
        else:
            export[key] = float(attrval)
        return
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        if key not in js and self.default is not None:
            cons_args[key] = decimal.Decimal(self.default)
        else:
            if js[key] is None:
                val = None
            else:
                val = decimal.Decimal(("%%.%df" % self.precision) % js[key])
            if self.attribute:
                cons_args[self.attribute] = val
            else:
                cons_args[key] = val

class JSON_EXP_SUB_DICT(JSON_ATTR):
    def __init__(self, defn, **kwargs):
        super(JSON_EXP_SUB_DICT,self).__init__(**kwargs)
        self.sub_handlers=defn
    def _handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        export[key]={}
        for subkey, handler in self.sub_handlers.items():
            handler.handle_export(obj, export[key], subkey, env, recurse_func, **kwargs)
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        pass

class JSON_OPT_ATTR(JSON_ATTR):
    def __init__(self, decider=None, **kwargs):
        super(JSON_OPT_ATTR, self).__init__(**kwargs)
        self.decider = decider
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        if self.decider is None:
            doit = call_or_get_attr(obj, key)
        elif isinstance(self.decider,basestring):
            doit = call_or_get_attr(obj, self.decider)
        else:
            try:
                decider_list = list(self.decider)
                o = obj
                for decider_element in decider_list:
                    o = getattr(o, decider_element)
                    if callable(o):
                        o = o()
                doit = o
            except TypeError:
                raise ImportExportException("decider not iterable")
        if doit:
            super(JSON_OPT_ATTR, self).handle_export(obj, export, key, env, recurse_func, **kwargs)
        return
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        if key in js:
            super(JSON_OPT_ATTR,self).handle_import(js, cons_args, key, imp_kwargs, env)

class JSON_IMPLIED(JSON_ATTR):
    def handle_export(self, *args, **kwargs):
        pass
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        cons_args[key] = imp_kwargs[key]


class JSON_UNIQUE(JSON_ATTR):
    def handle_export(self, *args, **kwargs):
        pass
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        cons_args[key] = imp_kwargs[key]


class JSON_INHERITED(JSON_ATTR):
    def __init__(self, related_name, optional=False):
        super(JSON_INHERITED, self).__init__()
        self.related = related_name
        self.optional=optional
    def handle_export(self, *args, **kwargs):
        pass
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        try:
            cons_args[key] = imp_kwargs[key]
        except KeyError:
            if not self.optional:
                raise
    def recurse_import(self,js, obj, key, imp_kwargs, env, do_not_delete=False):
        if not env["save"]:
            try:
                getattr(imp_kwargs[key], self.related).add(obj, bulk=False)
            except KeyError:
                if not self.optional:
                    raise

class JSON_COMPLEX_LOOKUP_WRAPPER(JSON_ATTR):
    def __init__(self, attribute, null, exporter, 
                    model, app, importer_kwargs, 
                    warning_on_importer_fail, name_key_for_warning):
        self.attribute = attribute
        self.null = null
        self.model = model
        self.app = app
        self.exporter = exporter
        self.importer_kwargs = importer_kwargs
        self.warning_on_importer_fail = warning_on_importer_fail
        self.name_key_for_warning = name_key_for_warning
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        export[key] = self.exporter(getattr(obj,self.attribute))
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        mdl = apps.get_app_config(self.app).get_model(self.model)
        if self.null and js[key] is None:
            lookup = None
        else:
            kwargs = self.importer_kwargs(js[key])
            try:
                lookup = mdl.objects.get(**kwargs)
            except mdl.DoesNotExist:
                print self.warning_on_importer_fail % js[self.name_key_for_warning]
                lookup = None
        cons_args[self.attribute] = lookup

class JSON_SIMPLE_LOOKUP_WRAPPER(JSON_ATTR):
    def __init__(self, attribute, null, exporters, 
                    model, app, importer_kwargs, 
                    warning_on_importer_fail=None, name_key_for_warning=None):
        self.attribute = attribute
        self.null = null
        self.model = model
        self.app = app
        self.exporters = exporters
        self.importer_kwargs = importer_kwargs
        self.warning_on_importer_fail = warning_on_importer_fail
        self.name_key_for_warning = name_key_for_warning
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        for k, exporter in zip(key, self.exporters):
            export[k] = exporter(getattr(obj,self.attribute))
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        mdl = apps.get_app_config(self.app).get_model(self.model)
        kwargs = self.importer_kwargs(js)
        try:
            lookup = mdl.objects.get(**kwargs)
        except mdl.DoesNotExist:
            if not self.null and self.warning_on_importer_fail:
                print self.warning_on_importer_fail % js[self.name_key_for_warning]
                lookup = None
            elif not self.null:
                raise ImportExportException("%s not found" % self.attribute)
            else:
                lookup = None
        cons_args[self.attribute] = lookup

class JSON_GEO_COORD(JSON_ATTR):
    def __init__(self, attribute, view_override_attribute=None, view_replacement_attribute=None):
        super(JSON_GEO_COORD, self).__init__(attribute=attribute)
        self.view_override_attr = view_override_attribute
        self.view_replacement_attr = view_replacement_attribute
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        keyx, keyy = key
        if self.view_override_attr and getattr(obj, self.view_override_attr) and view and getattr(view, self.view_replacement_attr):
            repl_win = getattr(view, self.view_replacement_attr)
            export[keyx] = repl_win.x
            export[keyy] = repl_win.y
        else:
            export[keyx] = getattr(obj, self.attribute).x 
            export[keyy] = getattr(obj, self.attribute).y 
        return
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        keyx, keyy = key
        from django.contrib.gis.geos import Point
        cons_args[self.attribute] = Point(js[keyx], js[keyy])

class JSON_RECURSEDOWN(JSON_ATTR):
    def __init__(self, model, related_name, related_attr, sub_attr_key, sub_exp_key=None, app=None, merge=True, recurse_attr_chain=[], suppress_if_empty=False, decider=None, suppress_decider=None, recurse_obj_arg=None, recurse_func_override=None,loop_extra={}):
        super(JSON_RECURSEDOWN, self).__init__()
        self.related = related_name
        self.related_attr = related_attr
        self.app = app
        self.model = model
        self.suppress_if_empty = suppress_if_empty
        self.suppress_decider = suppress_decider
        self.decider = decider
        self.merge = merge
        self.sub_attr_key = sub_attr_key
        self.recurse_attr_chain = recurse_attr_chain
        self.recurse_func_override = recurse_func_override
        self.recurse_obj_arg = recurse_obj_arg
        self.loop_extra = loop_extra
        if sub_exp_key:
            self.sub_exp_key = sub_exp_key
        else:
            self.sub_exp_key = sub_attr_key
    def recurse_loop(self, obj):
        if self.loop_extra:
           return getattr(obj, self.related).extra(self.loop_extra)
        else: 
            return getattr(obj, self.related).all()
    def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        if self.suppress_if_empty and self.recurse_loop(obj).count() == 0:
            return
        if self.decider and not call_or_get_attr(obj, self.decider):
            return
        if self.suppress_decider and call_or_get_attr(obj, self.suppress_decider):
            return
        if key:
            export[key] = []
            exp_target = export[key]
        else:
            exp_target = export
        for o in self.recurse_loop(obj):
            for attr in self.recurse_attr_chain:
                o = getattr(o, attr)
            if self.recurse_func_override:
                func = getattr(o, self.recurse_func_override)
            else:
                func = getattr(o, recurse_func)
            func_kwargs = kwargs.copy()
            if self.recurse_obj_arg:
                func_kwargs[self.recurse_obj_arg] = obj
            exp_target.append(func(**func_kwargs))
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        pass
    def get_model(self):
        if self.app:
            return apps.get_app_config(self.app).get_model(self.model)
        else:
            return self.model
    def recurse_import(self,js, obj, key, imp_kwargs, env, do_not_delete=False):
        model = self.get_model()
        base_kwargs = {}
        base_kwargs[self.related_attr] = obj
        if key is None:
            _js = js
        elif self.suppress_if_empty or self.suppress_decider:
            _js = js.get(key, [])
        else:
            _js = js[key]
        keys_in_import=[]
        if self.merge:
            for js_elem in _js:
                keys_in_import.append(js_elem[self.sub_exp_key])
            for elem in getattr(obj,self.related).all():
                elem_key = call_or_get_attr(elem, self.sub_attr_key)
                if elem_key not in keys_in_import and not do_not_delete:
                    elem.delete()
        elif not do_not_delete:
            getattr(obj, self.related).all().delete()
        for i in range(len(_js)):
            kwargs = base_kwargs.copy()
            kwargs["merge"] = do_not_delete
            if isinstance(model.export_def.get("sort_order"), JSON_IMPLIED):
                kwargs["sort_order"] = (i + 1)*100
            if isinstance(model.export_def.get("sort_order"), JSON_UNIQUE):
                curr_max = model.objects.all().aggregate(Max('sort_order'))['sort_order__max']
                if curr_max is None:
                    kwargs["sort_order"] = 1
                else:
                    kwargs["sort_order"] = curr_max + 1
            kwargs["js"] = _js[i]
            saved = False
            while not saved:
                try:
                    model.import_data(**kwargs)
                    saved = True
                except IntegrityError, e:
                    if isinstance(model.export_def.get("sort_order"), JSON_IMPLIED):
                        kwargs["sort_order"] += 1
                    else:
                        raise

class JSON_SELF_RECURSEDOWN(JSON_RECURSEDOWN):
    def recurse_loop(self, obj):
        return self.get_model().objects.filter(parent=obj.parent).exclude(id=obj.id)

class JSON_RECURSEDICT(JSON_ATTR):
   def __init__(self, related, key_attr, value_attr): 
       self.related = related
       self.key_attr = key_attr
       self.value_attr = value_attr
   def handle_export(self, obj, export, key, env, recurse_func="export", **kwargs):
        exp = {}
        for o in getattr(obj, self.related).all():
            exp[call_or_get_attr(o, self.key_attr)] = call_or_get_attr(o, self.value_attr)
        export[key] = exp
        return
   def handle_import(self, js, cons_args, key, imp_kwargs, env):
        pass

class WidgetDefJsonMixin(object):
    export_def = {
    }
    export_lookup = {}
    api_state_def = {
    }
    def export(self):
        if None in self.export_def:
            exp = []
        else:
            exp = {}
        env = {
            "single_export_field": False
        }
        for k, v in self.export_def.items():
            v.handle_export(self, exp, k, env)
        if env["single_export_field"]:
            return exp[env["single_export_field"]]
        else:
            return exp
    def __getstate__(self, **kwargs):
        if None in self.api_state_def:
            data = []
        else:
            data = {}
        env = {
            "single_export_field": False
        }
        for k, v in self.api_state_def.items():
            v.handle_export(self, data, k, env, recurse_func="__getstate__", **kwargs)
        if env["single_export_field"]:
            return data[env["single_export_field"]]
        else:
            return data
    @classmethod
    def import_data(cls, js, **kwargs):
        cons_args = kwargs.copy()
        if "merge" in kwargs:
            merge = kwargs["merge"]
            del cons_args["merge"]
        else:
            merge = False
        env = { "save": True }
        for k, v in cls.export_def.items():
            v.handle_import(js, cons_args, k, kwargs, env)
        if cls.export_lookup:
            get_kwargs = {}
            for v in cls.export_lookup.values():
                get_kwargs[v] = cons_args[v]
            try:
                obj = cls.objects.get(**get_kwargs)
                for k,v in cons_args.items():
                    if k not in cls.export_lookup:
                        setattr(obj, k, v)
            except cls.DoesNotExist:
                obj = cls(**cons_args)
        else:
            obj = cls(**cons_args)
        if env["save"]:
            try:
                clean = getattr(obj, "clean")
                clean()
            except AttributeError:
                pass
            obj.save()
        for k, v in cls.export_def.items():
            v.recurse_import(js, obj, k, kwargs, env, do_not_delete=merge)
        return obj

