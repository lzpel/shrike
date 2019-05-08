import webapp2,json,os
from google.appengine.ext.webapp import template, blobstore_handlers, RequestHandler
from google.appengine.api import urlfetch, app_identity, mail, memcache

def httpfunc(method,url,header,data):
    method={"POST":urlfetch.POST,"GET":urlfetch.GET}[method]
    r=urlfetch.fetch(url=url, payload=data, method=method, headers=header)
    return (r.status_code, r.content)
def wsgiapp(accesstable):
    return webapp2.WSGIApplication(accesstable)
def textres(content,**kwargs):
    headers={}
    if "type" in kwargs:
        headers['Content-Type'] = kwargs["type"]
    return webapp2.Response(content,headers=headers)
def tempres(temp,params,**kwargs):
    tmp = os.path.join(os.path.dirname(__file__), "../" + temp)
    return textres(template.render(tmp, params),**kwargs)
<<<<<<< HEAD
def jsonres(content,**kwargs):
    kw={}
    if kwargs.get("indent",0):
        kw["indent"]=kwargs["indent"]
    content=json.dumps(content, **kw)
    if kwargs.get("html",0):
        content="\n".join("<p>{0}</p>".format(i) for i in content.split("\n"))
    return webapp2.Response(content)
def passres(uri):
    return webapp2.redirect(uri)
def requestjson(request):
    return json.loads(request.body)
def requestargs(request):
    result={}
    result.update(request.GET)
    result.update(request.POST)
    return result
def urlformat(formatstring,request,params):
    kwargs={}
    if params:
        kwargs.update({"params":"&".join("{0}={1}".format(k,v) for k,v in (params or {}).items())})
    if request:
        kwargs.update({"host":request.host_url,"path": request.path,"query":request.query_string})
    return formatstring.format(**kwargs)
=======
def jsonres(content):
    return webapp2.Response(json.dumps(content))
def passres(url):
    return webapp2.redirect(url)
def requestjson(request):
    return json.loads(request.body)
def requestargs(request):
    r={}
    r.update(request.GET)
    r.update(request.POST)
    return r
def urlformat(request,formatstring,**kwargs):
    return formatstring.format(host=request.host_url,path=request.path,query=request.query_string,**kwargs)
>>>>>>> b0c2b9b09284e86ca037c9f05c408f829e117f0a

class BlobHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        self.send_blob(photo_key)