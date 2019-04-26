def presence_roundoff(plist, windowhalfmin):
	windowhalflen = len(plist) * windowhalfmin / 1440
	plistA = [bool(i) for i in plist]
	while True:
		print(str().join(str(int(i)) for i in plistA))
		plistB = list(plistA)
		for i, n in enumerate(plistA):
			windowlist = []
			windowlist.extend(plistA[max(0, i - windowhalflen):i])
			windowlist.extend(plistA[i:i + 1])
			windowlist.extend(plistA[i + 1:i + 1 + windowhalflen])
			plistB[i] = bool(float(sum(windowlist)) / len(windowlist) >= 0.5)
		if plistA == plistB:
			return plistB
		else:
			plistA = plistB
def presence_timetext(plist):
	output=str()
	for i, p in enumerate(plist):
		timetext = "{0:0>2}:{1:0>2}".format(24 * i / len(plist), (1440 * i / len(plist)) % 60)
		if p and not (False if i==0 else plist[i-1]):
			output += " {0}-".format(timetext)
		if p and not (False if i==len(plist)-1 else plist[i+1]):
			output += "{0}".format(timetext)
	print(output)
	return output
a = "001110111111111111111111011111110001111110111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111110"
presence_timetext(presence_roundoff([int(i) for i in a],60))