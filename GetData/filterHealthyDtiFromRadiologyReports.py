import os, re, sys, collections, csv

class FindHealthyDti():
	'''
	Search through radiology reports to identify reports relating to diffusion data collected from healthy subjects (i.e. no tumors)
	'''
	def __init__(self, allFiles ,radiologyReport):
		'''
		Inputs:
			allFiles (str):
				path to file containing list of reports retrieved from database. Each line looks like:
					#########|MGH|#######|3/59/6215|MRI|HDNK|MRRADMRIBRNWO|MRI Brain W/O Con (Test:MRIBRNWO)|########|Man,  , Hue  , CNP|A location|MGH|not recorded\n
			radiologyReport (str):
				path to file containing all radiology reports. Sample radiology report below: 
					EMPI|MRN_Type|MRN|Report_Number|MID|Report_Date_Time|Report_Description|Report_Status|Report_Type|Report_Text^M
					#########|MGH|#######|########|########|6/6/1008 5:20:00 AM|MRI Brain W & W/0 Con|Final|RAD|Exam Number:  ########				    Report Status:  Final^M
					Type:  MRI Brain W & W/0 Con^M
					Date/Time:  June 5th, 900BCE^M
					Exam Code:  Code
					Ordering Provider:  Shmicdougleberg, Doctor MD^M
					^M
					HISTORY:  ^M
						Some text^M
						^M
					^M
					REPORT:^M
						HISTORY: Some text^M
						^M
						TECHNIQUE: Some text^M
						^M
						COMPARISON: Some text^M
						^M
						FINDINGS:^M
						Some text^M
						^M
						IMPRESSION:^M
						Some text^M
						^M
					PROVIDERS:					  SIGNATURES:^M
						Doctorson, Doctor MD^M			 Doctorson, Doctor MD^M
					^M
					^M
					^M
					[report_end]^M
		'''
		self.allFiles = allFiles
		self.radiologyReport = radiologyReport
		self.examNumList = []
		self.keepDataDict = {} #becomes dictionary of all reports determined to be diffusion data from subjects with normal neuroanatomy. Key/value = ExamNum/Report
		self.fails = {} #becomes dictionary of all reports determined NOT to be diffusion data from subjects with normal neuroanatomy. Key/value = ExamNum/Report
		self.mrns = [] #becomes list of MRN numbers related to desirable data


	def grabExamNums(self):
		'''
		Compile list of exam numbers for radiology reports and additionally, a list of duplicates
		'''
		mriDoc = open(self.allFiles, 'rb')
		for line in mriDoc.readlines():
			self.examNumList.append(line.split('|')[8])
		self.duplicates = [item for item, count in collections.Counter(self.examNumList).items() if count > 1]


	def grabDiffusionReports(self):
		'''
		Go through all radiology reports and confirm the exam number for each one is found in the list generated by grabExamNums() and then grab all of them that contain "dti" or "diffusion"
		'''
		report = open(self.radiologyReport)
		self.reportDict = {}
		regex = re.compile('Exam\s*Number\:\s*(\d*)')
		dtiregex = re.compile('(dti)|(diffusion)', re.IGNORECASE)
		foo = ''.join(report.readlines()[1:])
		reportList = foo.split('[report_end]')
		for x in reportList:
			examNum = False
			try:
				examNum = regex.search(x).group(1)
			except AttributeError:
				pass
			if examNum != False:
				if examNum in self.examNumList:
					if examNum not in self.duplicates:
						if dtiregex.search(x):
							self.reportDict[examNum] = x+'\n[report_end]'


	def getCleanDiffusionData(self):
		'''
		Go through diffusion radiology reports and find all of the ones determined to be of neuroanatomically healthy individuals. See regexs for "healthy" criteria
		'''
		bracesRegex = re.compile('(braces)|(resection)|(craniotomy)|(callosotomy)|(cingulotomy)|(lobotomy)|(hemicraniotomy)|(lobectomy)', flags=re.IGNORECASE)
		lookForNegRegex = re.compile('(diffusion)|(dti)|(dwi)|(diffusion-weighted)|(adc)|(ischemia)|(tumor)|(stroke)|(ischemic)|(neurofibromatosis)|(infarct)|(glioblastoma)|(artifact)|(artifactual)|(mass effect)|(hyperintense)|(hyperintensity)', flags=re.IGNORECASE)
		mrnRegex = re.compile('\d*\|\w*\|\d*\|(\d*)\|')
		for examNum in self.reportDict:
			report = self.reportDict[examNum]
			if not bracesRegex.search(report):
				sentences = re.split('(HISTORY:.*\n*[^:]*:)|(TECHNIQUE:.*\n*[^:]*:)|(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)(\s|[A-Z].*)',report)
				goodSentenceFound = False
				badSentenceFound = False
				for s in sentences:
					if type(s) == str:
						if not re.search('(HISTORY:)|(TECHNIQUE:)',s):
							if lookForNegRegex.search(s):
								words = re.split('\W+',s)
								negWordFound = False
								for word in words:
									if word in ['no', 'No', 'NO', 'none', 'None', 'negative', 'Negative', 'not', 'Not', 'without', 'Without','inconsistant','Inconsistant']:
										negWordFound = True
									elif word in ['normal','Normal', 'performed', 'Performed', 'obtained', 'Obtained', 'acquired', 'Acquired', 'unremarkable', 'Unremarkable']:
										negWordFound = True
									else:
										pass
								if negWordFound == True:
									goodSentenceFound = True
								else:
									badSentenceFound = True
				if goodSentenceFound == True:
					if badSentenceFound == False:
						self.keepDataDict[examNum] = report
						self.mrns.append(mrnRegex.search(report).group(1))
					else:
						self.fails[examNum] = report
				else:
					self.fails[examNum] = report
			else:
				self.fails[examNum] = report


	def writeMRNsToCSV(self, outFile):
		'''
		Write MRN numbers derived from getCleanDiffusionData() to a csv file so that each row is one column long and contains a single MRN

		Inputs:
			outFile (str):
				Full file path of file to which you wish to write csv. Path should include filename ending in .csv
		'''
		with open(outFile, 'wb') as csvfile:
			spamwriter = csv.writer(csvfile, delimiter=',')
			spamwriter.writerow(self.mrns)
