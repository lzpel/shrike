# -encoding:utf-8
from template.appengine import *
from template.unit import *
from datetime import datetime, timedelta
import template.http as http
http.httpfunc=httpfunc
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

def hello(request):
	return tempres("index.html",{"json":[i.smalljson for i in unit.query().order(-unit.born).fetch()],})
def presence_adaypost(request,*args,**kwargs):
	LPFLENMIN=60
	presence = unit.query(unit.area == "presence").order(-unit.born).get(offset=int(requestargs(request).get("offset",0)))
	if presence:
		for member in presence.smalljson:
			a=member["modifiedpresence"]=presence_roundoff(member["presence"],LPFLENMIN)
			member["presencetext"]="\n{0} :{1}".format(member["name"],presence_timetext(a)) if any(a) else str()
		status, bodylist = http.get("https://slack.com/api/channels.list", {'token': requestargs(request)["bot"]["bot_access_token"]}, datatype="json")
		if bodylist["ok"]:
			for i in bodylist["channels"]:
				if i["is_member"]:
					http.post("https://slack.com/api/chat.postMessage", {'token': requestargs(request)["bot_access_token"],'channel': i['id'],'text': "".join(i["presencetext"] for i in presence.smalljson),})
	return jsonres(presence.smalljson,html=True,indent=4)
def presence_adaymake(request):
	status, bodylist = http.get("https://slack.com/api/users.list", {'token': requestargs(request)["bot_access_token"]}, datatype="json")
	if bodylist["ok"]:
		member = [i for i in bodylist["members"] if not (i["is_bot"] or i["id"] == "USLACKBOT")]
		for i in member:
			i["presence"] = [False] * (1440 / 5)
	presence = unit(area="presence", kusr=unit.key_by_id(requestargs(request)["id"]), smalljson=member)
	presence.put()
def presence_test(request):
	presence = unit.query(unit.area == "presence", unit.kusr == unit.key_by_id(requestargs(request)["id"])).order(-unit.born).get()
	if presence:
		for i in presence.smalljson:
			status, bodypres = http.get("https://slack.com/api/users.getPresence", {'token': requestargs(request)["bot_access_token"],"user": i["id"]}, datatype="json")
			i["presence"][len(i["presence"]) * (datetime.now() - presence.born).seconds / 86400] = (bodypres["presence"] == "active")
		presence.put()
def team(request,path):
	for t in unit.query(unit.area=="team").iter():
		t.smalljson["id"]=t.key.id()
		t.smalljson.update(t.smalljson["bot"])
		addtask(path,t.smalljson)
	return textres(path)

def oauth(request,path):
	CLIENT_ID = "19423426689.606115194753"
	CLIENT_SECRET = "69039563927271fad56a9eeffe8947b7"
	args=requestargs(request)
	if not path:
		return passres(urlformat("https://slack.com/oauth/authorize?{params}", None, {"client_id": CLIENT_ID,"scope": "bot commands","redirect_uri": urlformat("{host}/oauth/recv", request, None)}))
	else:
		code, body = http.post("https://slack.com/api/oauth.access", {"client_id": CLIENT_ID,"client_secret": CLIENT_SECRET,"code": args.get("code","")}, datatype="json")
		if body.get("ok", 0):
			model=unit.query(unit.iden==body["team_id"]).order(-unit.last).get() or unit()
			model.populate(area="team", iden=body["team_id"], smalljson=body)
			model.put()
		return jsonres(body)
def slash(request):
	args = requestargs(request)
	return jsonres({
		"text":"hello"
	})
app = wsgiapp([
	('/team(/.+)', team),
	("/oauth(/recv)?", oauth),
	("/slash", slash),
	('/presence_test', presence_test),
	('/presence_adaymake', presence_adaymake),
	('/presence_adaypost', presence_adaypost),
	('/', hello)
])