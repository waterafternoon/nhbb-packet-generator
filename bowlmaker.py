#just a reminder, this is python 3

import glob
import time
import re
import fileinput
import random
import os
import sys

if os.name == 'nt':
    Windows = True
else:
    Windows = False

foldername = "bowl"

createpacket = True

#below is the number of questions per category, in the case of q3q, it's the number of categories
q1q=10
q2q=8
q3q=3
q4q=8

packetsneeded = 1
packetnameheader = "_Camioneto"
desireddifficulty = "CA"
#CA = A level
#CB = B level
#CC = C level
#CN = Nationals

dirpath = ".\\"+ foldername + "\\*"
if Windows == False: dirpath = "./"+foldername+"/*"
packlist = glob.glob(dirpath)

alltossups = list()
allbonus = list()
alllightning = list()
alltiered = list()


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
	
#	writetest(bonus)
	bonuslist = re.findall(r"\d{1,2}\..*?\rANSWER.*?\rBONUS.*?\rANSWER.*?\r",bonus)
	bonuslist = strip_number(bonuslist)

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
	
	return tieredlist

def presanitize(filepath):
	if Windows == True: 
		filehandle = open(filepath,"r")
	else:
		filehandle = open(filepath,"r",encoding="cp1252")

	
#	import chardet
	filestring=filehandle.read()

#	filestring = filestring.decode(encoding='latin-1')
#	print(type(filestring))
#	sys.exit()

#	print(filestring)
	
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
	filestring = re.sub(r"\x0C","",filestring)
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
	
for filepath in packlist:
	if Windows == True: 
		textfile = open(filepath,"r+")
	else:
		textfile = open(filepath,"r+",encoding="cp1252")
	difficulty = id_difficulty(textfile)
	textfile.close()

	if difficulty == desireddifficulty: 
		print("adding this file to question pool",filepath,str(x+1))
		x=x+1
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
		if questionnumber >= 24601: print("http://i2.kym-cdn.com/photos/images/original/000/878/073/2a2.gif")
	return numberedquestions
	
numberofpackets = packetsneeded#input("How many packets do you need?")
numberofpackets = int(numberofpackets)
packetnameheader = packetnameheader
	
nop = numberofpackets

samtossups = random.sample(alltossups,q1q*nop)
print("there are "+str(len(alltossups)) + " tossups")
#appendtest(samtossups)

sambonus = random.sample(allbonus,q2q*nop)
print("there are "+str(len(allbonus)) + " bonuses")
#print(sambonus)

samlightning = random.sample(alllightning,q3q*nop)
print("there are "+str(len(alllightning)) + " lightning categories")
#print(samlightning)

samtiered = random.sample(alltiered,q4q*nop)
print("there are "+str(len(alltiered)) + " tiered questions")


print(str(min(len(alltiered)/q4q,len(alllightning)/q3q,len(allbonus)/q2q,len(alltossups)/q1q)) + " packets can be created.")
	
for x in range(numberofpackets):
	tempx = x + 1
	if tempx < 10: tempx = "0" + str(tempx)
	else: pass

	if Windows == True: 
		filename = ".\\export\\" + str(tempx) + packetnameheader + ".txt"
	else: 
		filename = "./export/" + str(tempx) + packetnameheader + ".txt"
	
	
	if Windows == True: 
		filehandle = open(filename,'w+')
	else: 
		filehandle = open(filename,'w+',encoding="cp1252")
	
	fc,sc = 0,0	#0-9, 10-19, 20-29
#	packettossups = samtossups[1]
	packettossups = samtossups[((x*q1q)+fc):((x+1)*q1q+sc)]
	packetbonus = sambonus[((x*q2q)+fc):((x+1)*q2q+sc)]
	packetlightning = samlightning[((x*q3q)+fc):((x+1)*q3q+sc)]
	packettiered = samtiered[((x*q4q)+fc):((x+1)*q4q+sc)]
	#it's not that complicated. the constants i added, fc and sc, were there because I don't understand lists.
	#feel free to take them out later, future me or some poor history club buddy that has to comb through my terrible code.
	
#	packettossups = random.sample(alltossups,10)
#	packetbonus = random.sample(allbonus,8)
#	packetlightning = random.sample(alllightning,3)
#	packettiered = random.sample(alltiered,8)

	packettossups = assign_numbers(packettossups)
	packetbonus = assign_numbers(packetbonus)
	packettiered = assign_numbers(packettiered)

	newpacketlightning = list()
	for item in packetlightning:
		newpacketlightning.extend([item,"\n"])

	packetlightning = newpacketlightning

	packettossups.insert(0,"Quarter One")
	packetbonus.insert(0,"Quarter Two")
	packetlightning.insert(0,"Quarter Three")
	packettiered.insert(0,"Quarter Four")
	
	packet = packettossups + ["\n\n"] + packetbonus + ["\n\n"] + packetlightning + ["\n\n"] + packettiered
	
	if createpacket == True: 
		for item in packet: 
			filehandle.write("%s\n" % item)
	else: pass
	filehandle.close()	
	
if createpacket == True: print("Created " + str(nop) + " packets, leveled " + desireddifficulty)
else: print(desireddifficulty + " packets were processed.\nNo packets have been created. Change createpacket to = True if you want to make packets.")
#well I can't stand to look at you now
#this revelation's out of my hands
#still I can't bear the thought of you now
#this complication's leaving me scared