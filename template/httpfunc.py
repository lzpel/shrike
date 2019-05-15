# -*- coding: utf-8 -*-

import time, random, platform, hmac, hashlib, base64, json, traceback, datetime,itertools,functools

if int(platform.python_version_tuple()[0]) == 2:
	from urllib2 import urlopen, Request, HTTPError,URLError
	from urllib import quote, urlencode
	from urlparse import parse_qs
	input = raw_input
	words=unicode
else:
	from urllib.request import urlopen, Request
	from urllib.parse import quote, urlencode, parse_qs
	from urllib.error import HTTPError,URLError
	input = input
	words=str
getstr = lambda d, k: d.get(k, None) or ""
tobyte=lambda x:(isinstance(x,words) and x.encode("utf-8")) or (isinstance(x,bytes) and x) or bytes(x)
totext=lambda x:(isinstance(x,bytes) and x.decode("utf-8")) or (isinstance(x,words) and x) or words(x)

def exceptionpass(sleepseconds=5,retry=0):
	def inner(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			for i in (retry>0 and range(retry)) or itertools.count():
				try:
					return func(*args, **kwargs)
				except Exception as e:
					traceback.print_exc()
					time.sleep(sleepseconds)
		return wrapper
	return inner

def unixtime(t=None):
	t = t or datetime.datetime.now()
	if isinstance(t, int):
		return datetime.datetime.fromtimestamp(t)
	else:
		return int(time.mktime(t.timetuple()))
def datauri(data,type="text/plain"):
	if isinstance(data,words):
		header, encoded = data.split(u",")
		return base64.b64decode(encoded)
	if isinstance(data,bytes):
		return totext("data:{};base64,{}".format(type,base64.b64encode(data).decode()))

def httpfunc(method,url,header,data):
	req=Request(url=url, data=data, headers=header)
	req.get_method=lambda:method
	h = urlopen(req)
	return h.getcode(), h.read()

def get(url,param=None,**kwargs):
	return request("GET",url,param,**kwargs)

def post(url,param=None,**kwargs):
	return request("POST",url,param,**kwargs)

def request(method, url, param,**kwargs):
	context=dict(kwargs.get("base",{}))
	context.update(kwargs)
	protocol=context.get("protocol",None)
	header=context.get("header",{})
	param={k:tobyte(v) for k,v in param.items()} if param else {}
	if not protocol:
		if method == "GET":
			url=url + "?" + urlencode(param) if param else url
			param=None
		else:
			param=tobyte(urlencode(param)) if isinstance(param, dict) else param
	if protocol=="oauth10":
		acckey, accsec = getstr(context,"acckey"),getstr(context,"accsec")
		conkey, consec = getstr(context,"conkey"),getstr(context,"consec")
		baseparam = {
			"oauth_token": acckey,
			"oauth_consumer_key": conkey,
			"oauth_signature_method": "HMAC-SHA1",
			"oauth_timestamp": str(int(time.time())),
			"oauth_nonce": str(random.getrandbits(64)),
			"oauth_version": "1.0"
		}
		signature = dict(baseparam)
		signature.update(param)
		signature = '&'.join('{0}={1}'.format(quote(key, ''), quote(signature[key], '~')) for key in sorted(signature))
		signature = ("{0}&{1}".format(consec, accsec), '{0}&{1}&{2}'.format(method, quote(url, ''), quote(signature, '')))
		signature = base64.b64encode(hmac.new(tobyte(signature[0]), tobyte(signature[1]), hashlib.sha1).digest())
		header = dict(baseparam)
		header.update({"oauth_signature": signature})
		header = ",".join("{0}={1}".format(quote(k, ''), quote(header[k], '~')) for k in sorted(header))
		header = {"Authorization": 'OAuth {0}'.format(header)}
		if method == "GET":
			url=url + "?" + urlencode(param) if param else url
			param=None
		else:
			param=tobyte(urlencode(param))
	time.sleep(context.get("sleep",0))
	code,body=httpfunc(method,url,header,param)
	datatype=context.get("datatype","raw")
	if datatype=="raw":
		body=body
	if datatype=="text":
		body=totext(body)
	if datatype=="query":
		body={k: v for k, v in [i.split("=") for i in body.split("&")]}
	if datatype=="json":
		body=json.loads(totext(body))
	return code,body

if __name__ == '__main__':
	print(unixtime())
	print(datauri(datauri("%abc%")))
	print(get("http://info.cern.ch/hypertext/WWW/TheProject.html", None))