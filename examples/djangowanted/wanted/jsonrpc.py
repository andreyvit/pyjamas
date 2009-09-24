# jsonrpc.py
#   original code: http://trac.pyworks.org/pyjamas/wiki/DjangoWithPyJamas
#   also from: http://www.pimentech.fr/technologies/outils
from django.utils import simplejson
from django.http import HttpResponse
import sys

# JSONRPCService and jsonremote are used in combination to drastically
# simplify the provision of JSONRPC services.  use as follows:
#
# jsonservice = JSONRPCService()
#
# @jsonremote(jsonservice)
# def test(request, echo_param):
#     return "echoing the param back: %s", echo_param
#
# dump jsonservice into urlpatterns:
#  (r'^service1/$', 'djangoapp.views.jsonservice'),

def response(id, result):
    return HttpResponse(simplejson.dumps({'version': '1.1', 'id':id,
                             'result':result, 'error':None}))
def error(id, code, message):
    return HttpResponse(simplejson.dumps({'id': id, 'version': '1.1',
                             'error': {'name': 'JSONRPCError',
                                       'code': code,
                                       'message': message
                                       }
                                 }))

class JSONRPCService:
    def __init__(self, method_map=None):
        self.method_map = method_map or {}
    
    def add_method(self, name, method):
        self.method_map[name] = method
        
    def __call__(self, request, extra=None):
        # We do not yet support GET requests, something pyjamas does
        # not use anyways.
        data = simplejson.loads(request.raw_post_data)
        # Altered to forward the request parameter when a member method
        # is invocated <julien@pimentech.net>
        id, method, params = data["id"],data["method"],[request,]+data["params"]
        if method in self.method_map:
            try:
                result = self.method_map[method](*params)
                return response(id, result)
            except BaseException:
                etype, eval, etb = sys.exc_info()
                return error(id, 100, '%s: %s' %(etype.__name__, eval))
            except:
                etype, eval, etb = sys.exc_info()
                return error(id, 100, 'Exception %s: %s' %(etype, eval))
        else:
            return error(id, 100, 'method "%s" does not exist' % method)


def jsonremote(service):
    """Make JSONRPCService a decorator so that you can write :
    
    from jsonrpc import JSONRPCService
    chatservice = JSONRPCService()

    @jsonremote(chatservice, 'login')
    def login(request, user_name):
        (...)
    """
    def remotify(func):
        if isinstance(service, JSONRPCService):
            service.add_method(func.__name__, func)
        else:
            emsg = 'Service "%s" not found' % str(service.__name__)
            raise NotImplementedError, emsg
        return func
    return remotify


# This provides a mechanism for turning Django Forms into JSONRPC
# Services.  If you have an existing Django app which makes prevalent
# use of Django Forms it will save you rewriting the app.
# use as follows:
#
# class SimpleForm(forms.Form):
#     testfield = forms.CharField(max_length=100)
#
# class SimpleForm2(forms.Form):
#     testfield = forms.CharField(max_length=20)
#
# processor = FormProcessor({'processsimpleform': SimpleForm,
#                            'processsimpleform2': SimpleForm2})
#
# this will result in a JSONRPC service being created with two
# RPC functions.  dump "processor" into urlpatterns to make it
# part of the app:
#  (r'^formsservice/$', 'djangoapp.views.processor'),


from django import forms 

def builderrors(form):
    d = {}
    for error in form.errors.keys():
        if error not in d:
            d[error] = []
        for errorval in form.errors[error]:
            d[error].append(unicode(errorval))
    return d

class FormProcessor(JSONRPCService):
    def __init__(self, forms, _formcls=None):

        if _formcls is None:
            JSONRPCService.__init__(self)
            for k in forms.keys():
                s  = FormProcessor({}, forms[k])
                self.add_method(k, s.__process)
                #self.add_method(k, s)
        else:
            JSONRPCService.__init__(self, forms)
            self.formcls = _formcls

    def __process(self, request, params):
        f = self.formcls(params)
        if f.is_valid():
            #do stuff
            return {'success':True}
        else:
            return {'success':False, 'errors': builderrors(f)}


# The following is incredibly convenient for saving vast amounts of
# coding, avoiding doing silly things like this:
#     jsonresult = {'field1': djangoobject.field1,
#                   'field2': djangoobject.date.strftime('%Y.%M'),
#                    ..... }
#
# The date/time flatten function is there because JSONRPC doesn't
# support date/time objects or formats, so conversion to a string
# is the most logical choice.  pyjamas, being python, can easily
# be used to parse the string result at the other end.
#
# use as follows:
#
# jsonservice = JSONRPCService()
#
# @jsonremote(jsonservice)
# def list_some_model(request, start=0, count=10):
#     l = SomeDjangoModelClass.objects.filter()
#     res = json_convert(l[start:end])
#
# @jsonremote(jsonservice)
# def list_another_model(request, start=0, count=10):
#     l = AnotherDjangoModelClass.objects.filter()
#     res = json_convert(l[start:end])
#
# dump jsonservice into urlpatterns to make the two RPC functions,
# list_some_model and list_another_model part of the django app:
#  (r'^service1/$', 'djangoapp.views.jsonservice'),

from django.core.serializers import serialize
import datetime
from datetime import date


def dict_datetimeflatten(item):
    d = {}
    for k, v in item.items():
        k = str(k)
        if isinstance(v, datetime.date):
            d[k] = str(v)
        elif isinstance(v, dict):
            d[k] = dict_datetimeflatten(v)
        else:
            d[k] = v
    return d

def json_convert(l, fields=None):
    res = []
    for item in serialize('python', l, fields=fields):
        res.append(dict_datetimeflatten(item))
    return res


