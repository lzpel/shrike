# -encoding:utf-8
from template.appengine import *
from template.unit import *
CLIENT_ID="342204927924.592004947603"
CLIENT_SECRET="fd05589134031d6b61048a445041ac13"
OAUTH_TOKEN="xoxb-342204927924-595037105715-V0Cn4SmjDyQiVYrYuy5dUii2"
def testfunc(request, *args, **kwargs):
	r=http.get("http://info.cern.ch/hypertext/WWW/TheProject.html")
	return textres('You requested product<br>{0}<br>{1}'.format(json.dumps(args),json.dumps(kwargs)))
def helloslack(request,*args,**kwargs):
	a=requestjson(request)
	b=a["type"]
	if b=="url_verification":
		return textres(a["challenge"])
	if b=="event_callback":
		c=a["event"]
		d=c["type"]
		if "user" in c:
			if d=="message":
				unit(area="message",smalljson=c).put()
				http.post("https://slack.com/api/chat.postMessage", {
					'token': OAUTH_TOKEN,
					'channel': c['channel'],
					'text': c["text"],
					'username': 'shrike',
					'icon_url': urlformat("{host}/icon.png",request,None),
				})
			if d=="reaction_added":
				unit(area="reaction",smalljson=c).put()
def hello(request):
	n=unit.query().order(-unit.born).fetch()
	return jsonres([i.smalljson for i in n])
def presence(request):
	result=[]
	status,bodylist=http.get("https://slack.com/api/users.list", {'token': OAUTH_TOKEN},datatype="json")
	if bodylist["ok"]:
		for member in bodylist["members"]:
			if not ( member["is_bot"] or member["id"]=="USLACKBOT" ):
				status, bodypres = http.get("https://slack.com/api/users.getPresence", {
					'token': OAUTH_TOKEN,
					"user":member["id"]
				}, datatype="json")
				result.append({
					"id":member["id"],
					"name":member["name"],
					"presence":(bodypres["presence"]=="active")
				})
		unit(area="presense",smalljson=result).put()
	return jsonres(result)
def oauthsend(request):
	return passres(urlformat("https://slack.com/oauth/authorize?{params}",None,{
		"client_id":CLIENT_ID,
		"scope":"chat:write:bot users:read",
		"redirect_uri":urlformat("{host}/oauthrecv",request,None)
	}))
def oauthrecv(request):
	args=requestargs(request)
	if args.get("code",None):
		code,body=http.post("https://slack.com/api/oauth.access", {
			"client_id":CLIENT_ID,
			"client_secret":CLIENT_SECRET,
			"code":args["code"],
		}, datatype="json")
		if body.get("access_token",0):
			unit(area="workspace", smalljson=body).put()




app = wsgiapp([("/oauthsend",oauthsend), ('/slack', helloslack), ('/presence', presence), ('/', hello)])
# http://localhost:8080/products/1, Your requested Product %1,