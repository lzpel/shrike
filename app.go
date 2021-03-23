package main

import (
	"bytes"
	"fmt"
	"github.com/slack-go/slack"
	"io"
	"os"
	"reflect"
	"strings"
	"time"
)

type Daily struct {
	Self   Key `datastore:"__key__"`
	Team   string
	Date   time.Time
	Active []bool `datastore:",noindex"`
	UserID []string
}

func (d *Daily) GetActive() map[string][]bool {
	m := map[string][]bool{}
	if d.Active != nil && d.UserID != nil {
		count := len(d.Active) / len(d.UserID)
		for i, n := range d.UserID {
			m[n] = d.Active[i*count : i*count+count]
		}
	}
	return m
}
func (d *Daily) SetActive(m map[string][]bool) {
	d.UserID = nil
	d.Active = nil
	for k, v := range m {
		d.UserID = append(d.UserID, k)
		d.Active = append(d.Active, v...)
	}
}
func TimeAlign(t time.Time) time.Time {
	const PREDICT_HOUR = 0
	t = t.In(time.Local).Add(-time.Hour * time.Duration(PREDICT_HOUR))
	return time.Date(t.Year(), t.Month(), t.Day(), 0, 0, 0, 0, time.Local)
}

func printActive(w io.Writer, plist []bool) {
	for _, n := range plist {
		if n {
			fmt.Fprint(w, 1)
		} else {
			fmt.Fprint(w, 0)
		}
	}
	fmt.Fprintln(w)
}

func roundoff(plist []bool, windowhalfmin int) []bool {
	windowhalflen := len(plist) * windowhalfmin / 1440
	plistA := make([]bool, windowhalflen*2+len(plist))
	plistB := make([]bool, windowhalflen*2+len(plist))
	for i, n := range plist {
		plistA[i+windowhalflen] = n
	}
	for true {
		printActive(os.Stdout, plistA)
		for i, _ := range plist {
			windowList, sum := plistA[i:i+windowhalflen*2+1], 0
			for _, m := range windowList {
				if m {
					sum++
				}
			}
			plistB[i+windowhalflen] = float32(sum)/float32(len(windowList)) >= 0.5
		}
		if reflect.DeepEqual(plistA[windowhalflen:windowhalflen+len(plist)], plistB[windowhalflen:windowhalflen+len(plist)]) {
			return plistB[windowhalflen : windowhalflen+len(plist)]
		} else {
			copy(plistA, plistB)
		}
	}
	return nil
}
func timeText(w io.Writer, plist []bool) {
	plistA := make([]bool, 2+len(plist))
	copy(plistA[1:1+len(plist)], plist)
	f := func(w io.Writer, i, n int) {
		fmt.Fprintf(w, "%02d:%02d", 24*i/n, (1440*i/n)%60)
	}
	for i := 0; i <= len(plist); i++ {
		if plistA[i] == false && plistA[i+1] == true {
			fmt.Fprint(w, " ")
			f(w, i, len(plist))
			fmt.Fprint(w, "-")
		}
		if plistA[i] == true && plistA[i+1] == false {
			f(w, i, len(plist))
		}
	}
}
func post() {
	ms := []Daily{}
	res := TableGetAll(NewQuery("DAILY").Order("-Date").Limit(1), &ms)
	if len(res) > 0 {
		client := NewSlackClient()
		w := bytes.NewBufferString("")
		if users, e := client.GetUsers(); e == nil {
			for key, value := range ms[0].GetActive() {
				for _, u := range users {
					if u.ID == key {
						flag, rounded := false, roundoff(value, 60)
						for _, n := range rounded {
							if n {
								flag = true
							}
						}
						fmt.Println(u.Name, flag)
						if flag {
							fmt.Fprint(w, u.Name)
							fmt.Fprint(w, ":")
							timeText(w, rounded)
							fmt.Fprintln(w)
						}
					}
				}
			}
		}
		if channels, _, e := client.GetConversationsForUser(&slack.GetConversationsForUserParameters{}); e == nil {
			for _, channel := range channels {
				client.PostMessage(channel.ID, slack.MsgOptionText(w.String(), false))
			}
		}
	}
}
func check() {
	const interval = 5
	ms, now := []Daily{}, time.Now().In(time.Local)
	res := TableGetAll(NewQuery("DAILY").Order("-Date").Limit(1), &ms)
	if len(res) > 0 && TimeAlign(ms[0].Date) == TimeAlign(now) {
		//nothing
	} else {
		ms = append([]Daily{{
			Self: NewKey("DAILY"),
			Date: now,
		}}, ms...)
	}
	c := NewSlackClient()
	if users, e := c.GetUsers(); e == nil {
		activeMap := ms[0].GetActive()
		for _, u := range users {
			if u.IsBot == true || u.ID == "USLACKBOT" {
				continue
			}
			if presence, e := c.GetUserPresence(u.ID); e == nil {
				if presence.Presence == "active" {
					if _, ok := activeMap[u.ID]; ok == false {
						activeMap[u.ID] = make([]bool, 1440/interval)
					}
					activeMap[u.ID][(now.Hour()*60+now.Minute())/interval] = true
				}
			} else {
				println(e)
			}
		}
		fmt.Println(activeMap)
		ms[0].SetActive(activeMap)
		TablePut(ms[0].Self, &ms[0])
	} else {
		print(e)
	}
}
func NewSlackClient() *slack.Client {
	return slack.New("xoxb-19423426689-612454598432-QVlIU73UYj8sVtj2opGeAP7S")
}
func command(command string) {
	if strings.Contains(command, "post") {
		post()
	}
	if strings.Contains(command, "check") {
		check()
	}
}

func main() {
	time.Local, _ = time.LoadLocation("Asia/Tokyo")
	Handle("/command/", func(w Response, r Request) {
		command(r.URL.Path)
	})
	Handle("/", func(w Response, r Request) {
		WriteTemplate(w, nil,nil, "index.html")
	})
	Credential("default.json")
	Listen()
}
