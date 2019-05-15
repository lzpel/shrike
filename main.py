# -encoding:utf-8
from template.appengine import *
from template.unit import *
from datetime import datetime, timedelta
import template.httpfunc as http
import re
http.httpfunc=httpfunc_appengine
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
	return output
def hello(request):
	return tempres("index.html",{"json":[i.smalljson for i in unit.query().order(-unit.born).fetch()],})
def presence_adaypost(request,*args,**kwargs):
	presence = unit.query(unit.area == "presence").order(-unit.born).get(offset=int(requestargs(request).get("offset",0)))
	if presence:
		for member in presence.smalljson:
			member["presencetext"]=presence_timetext(presence_roundoff(member["presence"],60))
		status, bodylist = http.get("https://slack.com/api/channels.list", {'token': requestargs(request)["bot_access_token"]}, datatype="json")
		if bodylist["ok"]:
			for i in bodylist["channels"]:
				if i["is_member"]:
					http.post("https://slack.com/api/chat.postMessage", {
						"username":"shrike@アクティブ時間帯報告bot",
						'token': requestargs(request)["bot_access_token"],
						'channel': i['id'],
						'text': "\n".join("{0}\t:{1}".format(i["name"],i["presencetext"]) for i in presence.smalljson if i["presencetext"]),
					})
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
		data={"id":t.key.id()}
		data.update(t.smalljson["bot"])
		addtask(path,data)
	return textres(path)

def oauth(request,path):
	CLIENT_ID = "19423426689.606115194753"
	CLIENT_SECRET = "69039563927271fad56a9eeffe8947b7"
	args=requestargs(request)
	if path=="oauth":
		params={"client_id": CLIENT_ID,"scope": "bot commands","redirect_uri": urlformat("{host}/oauthrecv", request, None)}
		return passres(urlformat("https://slack.com/oauth/authorize?{params}", None, params))
	if path=="oauthrecv":
		code, body = http.post("https://slack.com/api/oauth.access", {"client_id": CLIENT_ID,"client_secret": CLIENT_SECRET,"code": args.get("code","")}, datatype="json")
		if body["ok"]:
			model=unit.query(unit.iden==body["team_id"]).order(-unit.last).get() or unit()
			model.populate(area="team", iden=body["team_id"], smalljson=body)
			model.put()
			return jsonres(body)
		else:
			return jsonres(body) #for debug
def slash(request):
	lag=timedelta(hours=9)
	args = requestargs(request)
	team = unit.query(unit.area == "team", unit.iden == args["team_id"]).get()
	m=re.match("^(\d+)-(\d+)-(\d+)\s+(\d+)-(\d+)-(\d+)(\s+<@(\w+)\|\w+>)?$",args["text"])
	if m:
		m=m.groups()
		user=m[7] or args["user_id"]
		day1,day2=datetime(int(m[0]),int(m[1]),int(m[2])),datetime(int(m[3]),int(m[4]),int(m[5]))
		presence = unit.query(unit.area == "presence", unit.kusr == team.key, unit.born>min(day1,day2)-lag, unit.born<max(day1,day2)-lag).order(-unit.born).fetch()
		for i in presence:
			for j in i.smalljson:
				if j["id"]==user:
					i.text=presence_timetext(presence_roundoff(j["presence"],60))
		return textres("\n".join("{0}\t:{1}".format((i.born+lag).strftime('%Y-%m-%d'),i.text or str()) for i in presence))
	return textres(open("help.txt").read())
app = wsgiapp([
	('/team(/.+)', team),
	("/(oauth|oauthrecv)", oauth),
	("/slash", slash),
	('/presence_test', presence_test),
	('/presence_adaymake', presence_adaymake),
	('/presence_adaypost', presence_adaypost),
	('/', hello)
])