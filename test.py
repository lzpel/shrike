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

import random
a=[random.randint(0,1) for i in range(144)]
a=[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0]
presence_timetext(presence_roundoff(a, 60))
