import xml.etree.ElementTree as etree
from queue import *
from datetime import date, timedelta, datetime
from threading import Thread

class App:
	def __init__(self):
		self.xmlFileName = "activityLog.xml"
		self.tree = etree.parse(self.xmlFileName)
		self.root = self.tree.getroot()

		self.isRunning = True
		self.commands = Queue(maxsize=0) 
		self.cmdArgs = {} 

		self.elapsedTime = {}
		isElapsedTimeCalculated = False

	def run(self):
			self.printWelcomeMessage()
			while self.isRunning:
					self.getCommand()
					self.handleCommand()
	def printWelcomeMessage(self):
		print("If you don't know any commands, enter help")
	def getCommand(self):
		rawCommand = input('>')
		readingArgs = False
		lastCommand = ''
		lastParameter = ''

		i = 0
		splittedInput = rawCommand.split()

		self.commands.put(splittedInput[0])
		self.cmdArgs.setdefault(splittedInput[0], {})
		lastCommand = splittedInput[0]
		
		try:
			for word in splittedInput[1:]:
				if word[0] == '-':
					self.cmdArgs[lastCommand].setdefault(word[1:], [])
					lastParameter = word[1:]
				else:
					self.cmdArgs[lastCommand][lastParameter].append(word)
		except KeyError:
			print('Undefined key')
			return 

	def handleCommand(self):
		try:
			while self.commands.empty() == False:
				commandToExecute = self.commands.get_nowait()
				self.executeCommand(commandToExecute)
		except Empty:
				self.executeCommand(commandToExecute)
				return	
	def executeCommand(self, commandToExecute):
		thread1 = None
		if commandToExecute == 'up':
			thread1 = Thread(target = self.updateActivity,\
														args=[commandToExecute])
		elif commandToExecute == 'add':
			thread1 = Thread(target = self.addActivity)
		elif commandToExecute == 'list':
			thread1 = Thread(target = self.listActivities)
		elif commandToExecute == 'del':
			thread1 = Thread(target = self.deleteActivity,\
														args=[commandToExecute])
		elif commandToExecute == 'quit':
			self.isRunning = False
			thread1 = Thread(target = self.saveXML)
		elif commandToExecute == 'help':
			thread1 = Thread(target = self.printHelpFile)
		elif commandToExecute == 'save':
			thread1 = Thread(target = self.saveXML)
		elif commandToExecute == 'xml':
			thread1 = Thread(target = self.printXML())
		else:
			print("Unknown command")
			return
		thread1.start()
		thread1.join()

	def addActivity(self):
			name = input('Name:')
			fieldName = input('Field:')
			rcDate = self.date2Str(datetime.today(), True)

			activityNode = etree.Element("activity")
			self.root.append(activityNode)

			nameNode = etree.Element("name")
			nameNode.text = name
			fieldNode = etree.Element("field")
			fieldNode.text = fieldName
			cdateNode = etree.Element("cdate")
			cdateNode.text = rcDate
			rdateNode = etree.Element("rdate")
			rdateNode.text = rcDate

			activityNode.append(nameNode)
			activityNode.append(fieldNode)
			activityNode.append(cdateNode)
			activityNode.append(rdateNode)

			nextId = int(self.root.attrib['noAdded'])+1
			self.root.attrib['noAdded'] = str(nextId)
			activityNode.attrib['id'] = str(nextId)

	def deleteActivity(self, commandName):
		activities = self.root.findall('activity')
		
		try:
			listOfIds = self.cmdArgs[commandName]['f']
			for elementId in listOfIds:
				for activity in activities:
					if activity.attrib['id'] == elementId:
						self.root.remove(activity)
			self.cmdArgs[commandName].clear()
		except ValueError:
			print("Failed")
			return 
		except KeyError:
			print('Lack of key')
			return 
		

	def listActivities(self):
			activities = self.root.findall("activity")
			print("%-4s %-20s %-10s %-10s %-10s %-10s" % ("ID","Name", \
											   "Field","CDate","RDate",\
											   "Elapsed"))
			for activity in activities:
					self.handleActivityInfo(activity)
					print("")

	def handleActivityInfo(self, activityData):
		activityElements = {}
		i = 0
		for dataField in activityData:
				activityElements.setdefault(dataField.tag, dataField.text)	
		if len(activityElements) >= 4:
			activityID = activityData.attrib["id"]
			activityElements['id'] = activityID
			elapsedTimeStr = self.convertElapsedTime(\
									self.calculateElapsedTime(\
									self.strToDate(activityElements['rdate'])))
			activityElements['elapsed'] = elapsedTimeStr
			self.printFormattedInfo(activityElements)

	def printFormattedInfo(self, activityElements = {}):
		name = activityElements['name']
		if len(name) > 20:
			name = name[0:17]
			name += "..."

		fieldName = activityElements['field']
		if len(fieldName) > 10:
			fieldName = fieldName[0:7]
			fieldName += "..."

		cdate = activityElements['cdate']
		cdatetime = self.strToDate(cdate)
		cdate = self.date2Str(cdatetime, False)

		rdate = activityElements['rdate']
		rdatetime = self.strToDate(rdate)
		rdate = self.date2Str(rdatetime, False)

		activityId = activityElements['id']
		elapsedTime = activityElements['elapsed']

		print("%-4s %-20s %-10s %-10s %-10s %-10s" % (activityId,\
				  name, fieldName, cdate, rdate, elapsedTime), end="")

	def printHelpFile(self):
			helpFile = open('help.txt', 'r')
			helpContent = helpFile.read()
			print(helpContent)
			helpFile.close()

	def strToDate(self, dateString):
			tempDate = []
			temp = ""
			for c in dateString:
					if c != '-':
							temp += c
					else:
							tempDate.append(int(temp))
							temp = ""
			tempDate.append(int(temp))
			convertedDate = datetime(tempDate[0],	#year
									 tempDate[1], 	#month	
									 tempDate[2],	#day
									 tempDate[3],	#hour
									 tempDate[4])	#minute
			return convertedDate

	def date2Str(self, dateToConvert, fullFormat):
		years = dateToConvert.year
		months = dateToConvert.month
		days = dateToConvert.day
		minutes = dateToConvert.minute
		hours = dateToConvert.hour

		if(days < 10):
			days = '0'+str(days)
		else:
			days = str(days)
		
		if(months < 10):
			months = '0'+str(months)
		else:
			months = str(months)

		if(minutes < 10):
			minutes = '0'+str(minutes)
		else:
			minutes = str(minutes)

		if(hours < 10):
			hours = '0'+str(hours)
		else:
			hours = str(hours)

		strDate = "{0}-{1}-{2}".format(years, months, days)
		if fullFormat:
			strDate += "-{0}-{1}".format(hours, minutes)
		return strDate

	def calculateElapsedTime(self, previousDate):
			return datetime.today() - previousDate

	def convertElapsedTime(self, elapsedTime):
			seconds = elapsedTime.seconds
			minutes = seconds // 60
			hours = seconds // 3600
			days = elapsedTime.days
			
			minutes = minutes % 60
			if(minutes < 10):
				minutes = '0'+str(minutes)
			else:
				minutes = str(minutes)	
			
			hours = hours % 24
			if(hours < 10):
				hours = '0'+str(hours)
			else:
				hours = str(hours)

			elapsedTimeStr = "{0} days {1}:{2}".format(days, hours, minutes)
			return elapsedTimeStr

	def updateActivity(self, commandName):
		activities = self.root.findall('activity')

		try:
			listOfIds = self.cmdArgs[commandName]['i']
			for elementId in listOfIds:
				for activity in activities:
					if activity.attrib['id'] == elementId:
						activity.find("rdate").text = self.date2Str(\
												datetime.today(), True)
						repeatsNumber = activity.find('repeatsNumber')
						if repeatsNumber == None:
							repeatsNumber = etree.Element(\
														'repeatsNumber')
							repeatsNumber.text = '0'
							activity.append(repeatsNumber)
						numberOfRepeats = repeatsNumber.text
						numberOfRepeats = int(numberOfRepeats) + 1
						repeatsNumber.text = str(numberOfRepeats)

			self.cmdArgs[commandName].clear()
		except ValueError:
			print("Failed")
			return 
		except KeyError:
			print("Enter element's id you want to update")
			return

	def printXML(self):
			print(etree.tostring(self.root))
	def saveXML(self):
			self.tree.write('activityLog.xml')
app = App()
app.run()


