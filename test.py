import random,time,template.httpfunc
intid1=lambda x:chr(97+(x/26**0)%26)+chr(97+(x/26**1)%26)+chr(97+(x/26**2)%26)+chr(97+(x/26**3)%26)+chr(97+(x/26**4)%26)
intid2=lambda x:chr(97+(x/26**0)%26)+chr(97+(x/26**1)%26)+chr(97+(x/26**2)%26)+"aiueo"[(x/26**3)%5]+chr(97+(x/26**4)%26)
while True:
	userid=intid2(random.randint(0,26**5-1))
	try:
		time.sleep(1)
		template.httpfunc.get("http://twitter.com/{0}".format(userid))
		continue
	except:
		pass
	print userid