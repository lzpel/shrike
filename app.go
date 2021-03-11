package main

import (
	"bytes"
	"fmt"
	"github.com/slack-go/slack"
	"io"
	"net/http"
	"os"
	"reflect"
	"strings"
	"time"
)
type Daily struct{
	Team string
	Date time.Time
	Active []bool
	UserID []string
}
func (d*Daily) GetActive() map[string][]bool{
	count,m:=len(d.Active)/len(d.UserID),map[string][]bool{}
	for i,n:=range d.UserID{
		m[n]=d.Active[i*count:i*count+count]
	}
	return m
}
func (d*Daily) SetActive(m map[string][]bool){
	d.UserID=nil
	d.Active=nil
	for k,v:=range m{
		d.UserID=append(d.UserID,k)
		d.Active=append(d.Active,v...)
	}
}
func TimeAlign(t time.Time) time.Time {
	const PREDICT_HOUR = 0
	t = t.In(time.Local).Add(-time.Hour * time.Duration(PREDICT_HOUR))
	return time.Date(t.Year(), t.Month(), t.Day(), 0, 0, 0, 0, time.Local)
}

func printActive(w io.Writer,plist []bool){
	for _,n:=range plist{
		if n{
			fmt.Fprint(w,1)
		}else{
			fmt.Fprint(w,0)
		}
	}
	fmt.Fprintln()
}

func roundoff(plist []bool,windowhalfmin int) []bool{
	windowhalflen:=len(plist)*windowhalfmin/1440
	plistA:=make([]bool,windowhalflen*2+len(plist))
	plistB:=make([]bool,windowhalflen*2+len(plist))
	for i,n:=range plist{
		plistA[i+windowhalflen]=n
	}
	for true{
		printActive(os.Stdout, plistA)
		copy(plistB,plistA)
		for i, n:= range plist{
			windowList,sum:=plistA[i:i+windowhalflen*2+1],0
			for j,m:=range windowList{
				if m{sum++}
			}
			plistB[i+windowhalflen] = float32(sum) / float32(len(windowList)) >= 0.5
		}
		if reflect.DeepEqual(plistA,plistB) {
			return plistB[windowhalflen:-windowhalflen]
		}else{
			copy(plistA,plistB)
		}
	}
}
func timeText(w io.Writer,plist []bool){
	plistA:=make([]bool,2+len(plist))
	copy(plistA[1:1+len(plist)],plist)
	f:=func(w io.Writer,i,n int){
		fmt.Fprintf(w, "%02d:%02d", 24*i/n, (1440*i/n)%60)
	}
	for i:=0;i<=len(plist);i++{
		if plistA[i]==false && plistA[i+1]==true{
			fmt.Fprint(w," ")
			f(w,i,len(plist))
			fmt.Fprint(w,"-")
		}
		if plistA[i]==true && plistA[i+1]==false{
			f(w,i,len(plist))
		}
	}
}
func dailyPost(){
	ms:=[1]Daily{}
	res:= TableGetAll(NewQuery("DAILY").Order("-Born").Limit(1), &ms)
	if len(res)>0{
		client:=newClient()
		w:=bytes.NewBufferString("")
		for key, value:=range ms[0].GetActive(){
			fmt.Fprint(w,key)
			timeText(w,roundoff(value,60))
		}
		if channels,_,e:=client.GetConversationsForUser(&slack.GetConversationsForUserParameters{});e==nil{
			for _,channel:=range channels{
				client.PostMessage(channel.ID, slack.MsgOptionText(w.String(), false))
			}
		}
	}
}
func check(){
	ms,now:=[1]Daily{},TimeAlign(time.Now())
	res:= TableGetAll(NewQuery("DAILY").Order("-Born").Limit(1), &ms)
	if len(res)>0 && TimeAlign(ms[0].Date)==now{
		//nothing
	}else{
		ms[0]=Daily{
			Date: now,
		}
	}
	c:=newClient()
	c.GetUserPresence()
	presence = unit.query(unit.area == "presence", unit.kusr == unit.key_by_id(requestargs(request)["id"])).order(-unit.born).get()
	if presence:
	for i in presence.smalljson:
	status, bodypres = http.get("https://slack.com/api/users.getPresence", {'token': requestargs(request)["bot_access_token"],"user": i["id"]}, datatype="json")
	i["presence"][len(i["presence"]) * (datetime.now() - presence.born).seconds / 86400] = (bodypres["presence"] == "active")
	presence.put()
}
func newClient() *slack.Client{
	return slack.New("39iBSDC5AF0YxP3eucMvNyd0",nil)
}
func command(command string) Dict{
	if strings.Contains(command,"post"){
		dailyPost()
	}
	if strings.Contains(command,"check"){
		check()
	}
}

func main() {
	time.Local,_=time.LoadLocation("Asia/Tokyo")
	Handle("/command/",func(w Response, r Request){
		command(r.URL.Path)
	})
	Handle("/", func(w Response, r Request) {
		WriteTemplate(w, nil, nil,"index.html")
	})
	Listen()
}
