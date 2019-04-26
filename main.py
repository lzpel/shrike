# -encoding:utf-8
from template.appengine import *
from template.unit import *
from datetime import datetime, timedelta

CLIENT_ID = "342204927924.592004947603"
CLIENT_SECRET = "fd05589134031d6b61048a445041ac13"
OAUTH_BOT_TOKEN = "xoxb-19423426689-612454598432-5FKIs2IVpXqz6fDArb0EewKY"


def testfunc(request, *args, **kwargs):
	r = http.get("http://info.cern.ch/hypertext/WWW/TheProject.html")
	return textres('You requested product<br>{0}<br>{1}'.format(json.dumps(args), json.dumps(kwargs)))


def helloslack(request, *args, **kwargs):
	a = requestjson(request)
	b = a["type"]
	if b == "url_verification":
		return textres(a["challenge"])
	if b == "event_callback":
		c = a["event"]
		d = c["type"]
		if "user" in c:
			if d == "message":
				unit(area="message", smalljson=c).put()
				http.post("https://slack.com/api/chat.postMessage", {
					'token': OAUTH_BOT_TOKEN,
					'channel': c['channel'],
					'text': c["text"],
					'username': 'shrike',
					'icon_url': urlformat("{host}/icon.png", request, None),
				})
			if d == "reaction_added":
				unit(area="reaction", smalljson=c).put()


def hello(request):
	return jsonres([i.smalljson for i in unit.query().order(-unit.born).fetch()])
def presence_roundoff(plist, windowhalfmin):
	windowhalflen = len(plist) * windowhalfmin / 1440
	plistA = ([False] * windowhalflen)+[bool(i) for i in plist]+([False] * windowhalflen)
	while True:
		print(str().join(str(int(i)) for i in plistA))
		plistB = list(plistA)
		for i, n in enumerate(plist):
			windowlist = plistA[i:i + windowhalflen]+plistA[i + windowhalflen:i + windowhalflen + 1]+plistA[i + windowhalflen + 1:i + windowhalflen + 1 + windowhalflen]
			plistB[i+windowhalflen] = bool(float(sum(windowlist)) / len(windowlist) >= 0.5)
		if plistA == plistB:
			return plistB[windowhalflen:len(plistB)-windowhalflen]
		else:
			plistA = plistB


def presence_timetext(plist):
	output = str()
	plist2=[False]+plist+[False]
	for i in range(len(plist)+1):
		timetext = "{0:0>2}:{1:0>2}".format(24 * i / len(plist), (1440 * i / len(plist)) % 60)
		if not plist2[i] and plist2[i+1]:
			output += " {0}-".format(timetext)
		if plist2[i] and not plist2[i+1]:
			output += "{0}".format(timetext)
	print(output)
	return output

def presence_adaypost(request,*args,**kwargs):
	LPFLENMIN=60
	kwargs.update(requestargs(request))
	presence = unit.query(unit.area == "presence").order(-unit.born).get(offset=int(kwargs.get("offset",0)))
	if presence:
		for member in presence.smalljson:
			a=member["modifiedpresence"]=presence_roundoff(member["presence"],LPFLENMIN)
			member["presencetext"]="\n{0} :{1}".format(member["name"],presence_timetext(a)) if any(a) else str()
		status, bodylist = http.get("https://slack.com/api/channels.list", {'token': OAUTH_BOT_TOKEN}, datatype="json")
		if bodylist["ok"]:
			for i in bodylist["channels"]:
				if i["is_member"]:
					http.post("https://slack.com/api/chat.postMessage", {
						'token': OAUTH_BOT_TOKEN,
						'channel': i['id'],
						'text': "".join(i["presencetext"] for i in presence.smalljson),
					})
	return jsonres(presence.smalljson,html=True,indent=4)
def presence_adaymake(request):
	status, bodylist = http.get("https://slack.com/api/users.list", {'token': OAUTH_BOT_TOKEN}, datatype="json")
	if bodylist["ok"]:
		member = [i for i in bodylist["members"] if not (i["is_bot"] or i["id"] == "USLACKBOT")]
		for i in member:
			i["presence"] = [False] * (1440 / 5)
	presence = unit(area="presence", smalljson=member)
	presence.put()
def presence_test(request):
	presence = unit.query(unit.area == "presence").order(-unit.born).get()
	if presence:
		for i in presence.smalljson:
			status, bodypres = http.get("https://slack.com/api/users.getPresence", {'token': OAUTH_BOT_TOKEN, "user": i["id"]}, datatype="json")
			i["presence"][len(i["presence"]) * (datetime.now() - presence.born).seconds / 86400] = (bodypres["presence"] == "active")
		presence.put()

def oauthsend(request):
	return passres(urlformat("https://slack.com/oauth/authorize?{params}", None, {
		"client_id": CLIENT_ID,
		"scope": "chat:write:bot users:read",
		"redirect_uri": urlformat("{host}/oauthrecv", request, None)
	}))

def oauthrecv(request):
	args = requestargs(request)
	if args.get("code", None):
		code, body = http.post("https://slack.com/api/oauth.access", {
			"client_id": CLIENT_ID,
			"client_secret": CLIENT_SECRET,
			"code": args["code"],
		}, datatype="json")
		if body.get("access_token", 0):
			unit(area="workspace", smalljson=body).put()


app = wsgiapp([
	("/oauthsend", oauthsend),
	('/slack', helloslack),
	('/presence_test', presence_test),
	('/presence_adaymake', presence_adaymake),
	('/presence_adaypost', presence_adaypost),
	('/', hello)
])
# http://localhost:8080/products/1, Your requested Product %1,
