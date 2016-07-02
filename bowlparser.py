#just a reminder, this is python 3

import glob
import time
import re
import fileinput
import random

#import sqlite3
#conn = sqlite3.connect('bowlquestions.db')

foldername = "bowl"
#donefolder = "donefolder"

#below is the number of questions per category, in the case of q3q, it's the number of categories
#confused about q3q? think about it for a second.
q1q=10
q2q=8
q3q=3
q4q=8

packetsneeded = 8
packetnameheader = "Stockholm"
desireddifficulty = "CA"
#CA = A level
#CB = B level
#CC = C level
#CN = Nationals

dirpath = ".\\"+ foldername + "\\*"
packlist = glob.glob(dirpath)

alltossups = list()
allbonus = list()
alllightning = list()
alltiered = list()

#import random

x=0

print("importing files from this directory:", dirpath)

def id_difficulty(axtext):
	linenumber,linelimit,difficulty = 0,5,'fuck'
	for line in axtext:
		if "Bowl A" in line: 
			difficulty = "CA"
			break
		elif "Bowl B" in line:
			difficulty = "CB"
			break
		elif "Bowl C" in line:
			difficulty = "CC"
			break
		elif "National" in line:
			difficulty = "CN"
			break
		elif "Set A" in line: 
			difficulty = "CA"
			break
		elif "Set B" in line:
			difficulty = "CB"
			break
		elif "Set C" in line:
			difficulty = "CC"
			break
		else:
			linenumber = linenumber + 1
			if linenumber >= linelimit:
				result = False
				break#this is to help with debugging. see the first line in this def, fuck is the default 
	#	print(line)
	return difficulty	

def split_cats(filestring):
	tossup = re.search("First Quarter.*Second Quarter",filestring,flags=re.DOTALL).group(0)
	tossup = re.sub("Second Quarter","",tossup)
	
	bonus = re.search("Second Quarter(.*)Third Quarter",filestring,flags=re.DOTALL).group(0)
	bonus = re.sub("Third","",bonus)
	
	lightning = re.search("Third Quarter(.*)Fourth Quarter",filestring,flags=re.DOTALL).group(0)
	lightning = re.sub("Fourth","",lightning)
	
	tiered = re.search("Fourth Quarter.*",filestring,flags=re.DOTALL).group(0)
	
	return (tossup,bonus,lightning,tiered)

def extract_tossup(tossup):
	tossup = remove_double(tossup)
	tossup = re.sub(r"\r(?!ANSWER:|\d{1,2}\.)", " ", tossup)
	tossup = remove_double(tossup)
	tossup = re.sub(r"\d{1,69}-\d{1,69}-\d{1,69}.*?(\r|$)", r" \r",tossup)
	#Standin' on your mama's porch \ You told me that it'd last forever
	tossup = remove_double(tossup)
	
	tossuplist = re.findall(r"\d{1,2}\..*?\rANSWER:.*?\r",tossup)
	tossuplist = strip_number(tossuplist)
	
#	appendtest(tossuplist)
	return tossuplist
	
def extract_bonus(bonus):
	bonus = remove_double(bonus)
	bonus = re.sub(r"\r(?!ANSWER:|\d{1,2}\.|BONUS:)", " ", bonus)
	bonus = remove_double(bonus)
	bonus = re.sub(r"\d{1,69}-\d{1,69}-\d{1,69}.*?(\r|$)", r" \r",bonus)
	#Oh, and when you held my hand

	bonus = re.sub(r"\r", r"\n",bonus)
#	bonus = re.sub(r"BONUS\.",r"BONUS:",bonus)
	bonus = re.sub(r"::",r":",bonus)
	bonus = re.sub(r"\nANSWER.*\nANSWER",r"DELETETHISSHIZ",bonus)
	bonus = re.sub(r".*DELETETHISSHIZ.*",r"",bonus)
	
#	print(re.findall(r"\nANSWER.*\nANSWER.*",bonus))
	
	bonus = remove_double(bonus)

	filehandle=open(".\\bowltest\\ayy2.txt","a")
#	filehandle.write(bonus)
	filehandle.close()	
	
#	writetest(bonus)
	bonuslist = re.findall(r"\d{1,2}\..*?\rANSWER.*?\rBONUS.*?\rANSWER.*?\r",bonus)
	bonuslist = strip_number(bonuslist)
#	appendtest(bonuslist)

#	some stupid shortcut
	return bonuslist
	
def extract_lightning(lng):
	lng = remove_double(lng)
	lng = re.sub(r"\r",r"\n",lng)
	#i'm a fucking idiot. Python uses \n to indicate a new line
	#more than halfway through the definitions, i realize that using \r was a stupid idea that was detrimental instead of just neutral
	#fuck fuck fuck fuck fuck
	#well, it did save me from having to flag = re.DOTALL for a lot of lines
	#ehhhh.
	lng = re.sub(r"\n(.*)\n1\.",r"\nQUESTION: \1\n1.",lng)
	lng = re.sub(r"\n(.*)\nQUESTION:",r"\nENDOFCAT\nCATEGORY: \1\nQUESTION:",lng)
	for i in range(10): lng = re.sub(r"(ANSWER:.*)(\n)(?!\d{1,2}\.)(?!ANSWER:)(?!CATEGORY)(?!QUESTION)(?!ENDOFCAT)",r"\1",lng)
	lng = remove_double(lng)
	lng = re.sub(r"\d{1,69}-\d{1,69}-\d{1,69}.*?(\r|$)", r" \r",lng)
	#I knew that it was now or never
	lng = remove_double(lng)
	
	lng = lng + "ENDOFCAT"
	#i'm lazy. this line of code is probably going to bite me in the ass when i adapt this for bee and other types of packets
	
	lightninglist = re.findall(r"(CATEGORY.*?)ENDOFCAT",lng)
#	appendtest(lightninglist)
	return lightninglist

def extract_tiered(tiered):
	tiered = remove_double(tiered)
	tiered = re.sub(r"\r(?!ANSWER:|\d{1,2}\.)", " ", tiered)
	tiered = remove_double(tiered)
	tiered = re.sub(r"\d{1,69}-\d{1,69}-\d{1,69}.*?(\r|$)", r" \r",tiered)
	#Those were the best days of my life

	tiered = remove_double(tiered)
	
	tieredlist = re.findall(r"\d{1,2}\..*?\rANSWER:.*?\r",tiered)
	tieredlist = strip_number(tieredlist)
	
#	appendtest(tieredlist)
	return tieredlist

def presanitize(filepath):
	filehandle=open(filepath,"r")
	filestring=filehandle.read()
	filehandle.close()

	for i in range(5): filestring = re.sub(r"  "," ",filestring)
	filestring = re.sub(r"(First|Second|Third|Fourth) Quarter", r"\r\1 Quarter\r",filestring)
		#this, of course, gets cleaned up at the end of the function
	filestring = re.sub(r".*Bowl.*","",filestring)
	filestring = re.sub(r".*tcpdf.*","",filestring)
	#to be replaced with something like "I'm Van Duong, and Arcadia High School Can't Use This Packet."
	for i in range(5): filestring = re.sub(r"  "," ",filestring)
	filestring = re.sub(r".*Round \d{1,2}","",filestring)
	filestring = re.sub(r"\\\"","\"",filestring)
	for i in range(5): filestring = re.sub(r"\n|\r\r|\r\r\r|\r\r\r\r|\r \r",r"\r",filestring)
	for i in range(5): filestring = re.sub(r"\r ",r"\r",filestring)
	for i in range(5): filestring = re.sub("^ ","",filestring)
	for i in range(5): filestring = re.sub(r"::",r":",filestring)
	#so many unnecessary iterations. this def should have been renamed anal_retentive_sanitation().
	return filestring

def remove_double(thestring):
	#double spaces and double lines
	for i in range(7): thestring = re.sub(r"\n|\r\n|\r\r",r"\r", thestring)
	for i in range(7): thestring = re.sub(r"\r \r","\r", thestring)
	for i in range(7): thestring = re.sub("  "," ", thestring)
	return thestring

def strip_number(listofqs):
	listofqs2 = list()
	for item in listofqs:
		item = re.sub(r"^\d{1,2}\.","",item)
		item = re.sub("^ ","",item)
		listofqs2.append(item)
	#that's right, take off those numbers.
	return listofqs2
	
def writetest(teststring):
	filehandle=open(".\\bowltest\\ayy.txt","w+")
	filehandle.write(teststring)
	filehandle.close()	

def appendtest(testlist):
	filehandle=open(".\\bowltest\\ayy.txt","w+")
	for item in testlist:
		filehandle.write("%s\n\r" % item)
	#i have to admit, i copy-pasted the above two lines of code from stackoverflow. I don't know how this works.
	filehandle.close()	
	
for filepath in packlist:
	x=x+1
	print("accessing file",filepath,x)
#	print("using the following file as a test")
#	filepath = r".\\bowltest\\nhbb (121).txt"
	textfile = open(filepath,"r+")
	difficulty = id_difficulty(textfile)
	textfile.close()

	if difficulty == desireddifficulty: pass
	else: continue
	
	filestring = presanitize(filepath)
	
	(tossup,bonus,lightning,tiered) = split_cats(filestring)

	tossuplist = extract_tossup(tossup)
	bonuslist = extract_bonus(bonus)
	lightninglist = extract_lightning(lightning)
	tieredlist = extract_tiered(tiered)

	for item in tossuplist: alltossups.append(item)
	for item in bonuslist: allbonus.append(item)
	for item in lightninglist: alllightning.append(item)
	for item in tieredlist: alltiered.append(item)
	
def assign_numbers(packetquestions):
	questionnumber = 1
	numberedquestions = list()
	for x in packetquestions:
		numberedquestions.append(str(questionnumber) + ". " + x)
		questionnumber = questionnumber +1
		if questionnumber => 24601: print("http://i2.kym-cdn.com/photos/images/original/000/878/073/2a2.gif")
	return numberedquestions
	
numberofpackets = packetsneeded#input("How many packets do you need?")
numberofpackets = int(numberofpackets)
packetnameheader = packetnameheader
	
nop = numberofpackets
samtossups = random.sample(alltossups,q1q*nop)
sambonus = random.sample(allbonus,q2q*nop)
samlightning = random.sample(alllightning,q3q*nop)
samtiered = random.sample(alltiered,q4q*nop)

	
for x in range(numberofpackets):
	filename = packetnameheader + str(x) + ".txt"
	filehandle = open(filename,'w+')
	
	fc,sc = 0,0	#0-9, 10-19, 20-29
#	packettossups = samtossups[1]
	packettossups = samtossups[((x*q1q)+fc):((x+1)*q1q+sc)]
	packetbonus = sambonus[((x*q2q)+fc):((x+1)*q2q+sc)]
	packetlightning = samlightning[((x*q3q)+fc):((x+1)*q3q+sc)]
	packettiered = samtiered[((x*q3q)+fc):((x+1)*q4q+sc)]
	#it's not that complicated. the constants i added, fc and sc, were there because I don't understand lists.
	#feel free to take them out later, future me or some poor history bowl buddy that has to comb through my terrible code.
	
#	packettossups = random.sample(alltossups,10)
#	packetbonus = random.sample(allbonus,8)
#	packetlightning = random.sample(alllightning,3)
#	packettiered = random.sample(alltiered,8)

	packettossups = assign_numbers(packettossups)
	packetbonus = assign_numbers(packetbonus)
	packettiered = assign_numbers(packettiered)

	packettossups.append("Quarter Two")
	packetbonus.append("Quarter Three")
	packetlightning.append("Quarter Four")
	
	packet = packettossups + packetbonus + packetlightning + packettiered
	
	for item in packet: filehandle.write("%s\n" % item)
	filehandle.close()	
	
print("Created " + str(nop) + " packets, leveled " + desireddifficulty)