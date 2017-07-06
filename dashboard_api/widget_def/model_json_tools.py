from django.db.models import Model
from django.db.utils import IntegrityError
from django.apps import apps

def call_or_get_attr(obj, name):
    a = getattr(obj, name)
    if callable(a):
        return a()
    else:
        return a

class JSON_ATTR(object):
    """Default handler.  Just use the attribute"""
    def __init__(self, attribute=None):
        self.attribute = attribute
    def handle_export(self, obj, export, key, env):
        if self.attribute:
            export[key] = getattr(obj, self.attribute)
        else:
            export[key] = getattr(obj, key)
        return
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        if self.attribute:
            cons_args[self.attribute] = js[key]
        else:
            cons_args[key] = js[key]
    def recurse_import(self, js, obj, key, imp_kwargs, env):
        pass

class JSON_STRINGIFY_ATTR(JSON_ATTR):
    def handle_export(self, obj, export, key, env):
        if self.attribute:
            export[key] = unicode(getattr(obj, self.attribute))
        else:
            export[key] = unicode(getattr(obj, key))
        return

class JSON_SOLE_ATTR(JSON_ATTR):
    def handle_export(self, obj, export, key, env):
        super(JSON_SOLE_ATTR, self).handle_export(obj, export, key, env)
        env["single_export_field"] = key
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        cons_args[key] = js

class JSON_OPT_ATTR(JSON_ATTR):
    def __init__(self, decider=None, attribute=None):
        self.decider = decider
        self.attribute = attribute
    def handle_export(self, obj, export, key, env):
        if self.decider:
            do_it = getattr(obj, self.decider)
        else:
            do_it = getattr(obj, key)
        if do_it:
            if self.attribute:
                export[key] = getattr(obj, self.attribute)
            else:
                export[key] = getattr(obj, key)
        return
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        if key in js:
            if self.attribute:
                cons_args[self.attribute] = js[key]
            else:
                cons_args[key] = js[key]

class JSON_IMPLIED(JSON_ATTR):
    def handle_export(self, *args, **kwargs):
        pass
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        cons_args[key] = imp_kwargs[key]

class JSON_INHERITED(JSON_ATTR):
    def __init__(self, related_name):
        super(JSON_INHERITED, self).__init__()
        self.related = related_name
    def handle_export(self, *args, **kwargs):
        pass
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        cons_args[key] = imp_kwargs[key]
    def recurse_import(self,js, obj, key, imp_kwargs, env):
        getattr(imp_kwargs[key], self.related).add(obj, bulk=False)

class JSON_RECURSEDOWN(JSON_ATTR):
    def __init__(self, model, related_name, related_attr, sub_attr_key, sub_exp_key=None, app=None, suppress_if_empty=False):
        super(JSON_RECURSEDOWN, self).__init__()
        self.related = related_name
        self.related_attr = related_attr
        self.app = app
        self.model = model
        self.suppress_if_empty = suppress_if_empty
        self.sub_attr_key = sub_attr_key
        if sub_exp_key:
            self.sub_exp_key = sub_exp_key
        else:
            self.sub_exp_key = sub_attr_key
    def handle_export(self, obj, export, key, env):
        if self.suppress_if_empty and getattr(obj, self.related).count() == 0:
            pass
        elif key:
            export[key] = [ o.export() for o in getattr(obj, self.related).all() ] 
        else: 
            for o in getattr(obj, self.related).all():
                export.append(o.export())
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        pass
    def recurse_import(self,js, obj, key, imp_kwargs, env):
        if self.app:
            model = apps.get_app_config(self.app).get_model(self.model)
        else:
            model = self.model
        base_kwargs = {}
        base_kwargs[self.related_attr] = obj
        if key is None:
            _js = js
        elif self.suppress_if_empty:
            _js = js.get(key, [])
        else:
            _js = js[key]
        keys_in_import=[]
        for js_elem in _js:
            keys_in_import.append(js_elem[self.sub_exp_key])
        for elem in getattr(obj,self.related).all():
            elem_key = getattr(elem, self.sub_attr_key)
            if elem_key not in keys_in_import:
                elem.delete()
        for i in range(len(_js)):
            kwargs = base_kwargs.copy()
            kwargs["sort_order"] = (i + 1)*100
            kwargs["js"] = _js[i]
            saved = False
            while not saved:
                try:
                    model.import_data(**kwargs)
                    saved = True
                except IntegrityError:
                    kwargs["sort_order"] += 1
              
class WidgetDefJsonMixin(object):
    export_def = {
    }
    export_lookup = []
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
    def __getstate__(self, view=None):
        if None in self.api_state_def:
            data = []
        else:
            data = {}
        env = {
            "single_export_field": False
        }
        for k, v in self.api_state_def.items():
            v.handle_export(self, data, k, env)
        if env["single_export_field"]:
            return data[env["single_export_field"]]
        else:
            return data
    @classmethod
    def import_data(cls, js, **kwargs):
        cons_args = kwargs.copy()
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
            except obj.DoesNotExist:
                obj = cls(**cons_args)
        else:
            obj = cls(**cons_args)
        if env["save"]:
            obj.save()
        for k, v in cls.export_def.items():
            v.recurse_import(js, obj, k, kwargs, env)
        return obj

