import os, re, dicom, csv, subprocess, shutil, sys
from glob import glob

class DataSet():
	'''
	The full pipeline of this module takes a set of raw dicoms, decompresses any rle or JPEG compressed ones, makes a copy of the entire dataset, attempts to filter out any non DTI datasets, converts the dicoms to nifti, removes any with odd/broken bval/bvec files, and 

	inputs:
		dicomDataPath: path to directory containing dicom files.
	'''
	def __init__(self, dicomDataPath):
		self.dicomDataPath = dicomDataPath
		if self.dicomDataPath.endswith('/') == False:
			self.dicomDataPath += '/'
		self.savePath = os.path.split(os.path.realpath(__file__))[0]+'/'
		self.rawNiftis = self.savePath+'Niftis/'
		self.decompressedDicoms = self.savePath+'decompressedDicoms/'
		self.notDTIdata = []
		self.dtiDataDicomPaths = []
		self.failedNiiConverts = []
		self.originalNiftiPaths = []
		self.noZeroBval = []
		self.negativeBval = []
		self.lessThanSixBval = []
		self.wrongNumBvec = []
		self.mismatchedBvecLength = []
		self.difNumBvalBvec = []


	def decompressAndCopyDicoms(self):
		'''
		Decends dicom directory tree looking for rle and JPEG compressed files.
		If it finds any it decompresses them and copies them to the output directory.
		If uncompressed dicoms are found they are copied directly to the output directory.
		'''
		if os.path.exists(self.decompressedDicoms):
			shutil.rmtree(self.decompressedDicoms)
		os.mkdir(self.decompressedDicoms)
	        for sub in os.listdir(self.dicomDataPath):
	                if os.path.isdir(self.dicomDataPath+sub):
	                        for run in os.listdir(self.dicomDataPath+sub):
	                                if os.path.isdir(self.dicomDataPath+sub+'/'+run):
						possibleDicoms = glob(self.dicomDataPath+sub+'/'+run+'/\.dcm')
						if len(possibleDicoms) != 0: #make sure there are dicoms in directory
		                                        ds = dicom.read_file(possibleDicoms[0])
                                                        if os.path.exists(self.decompressedDicoms+sub) == False:
                                                                os.mkdir(self.decompressedDicoms+sub)
                                                        if os.path.exists(self.decompressedDicoms+sub+'/'+run) == False:
                                                                os.mkdir(self.decompressedDicoms+sub+'/'+run)
                                                        try:
                                                                ds.pixel_array
                                                                shutil.copytree(self.dicomDataPath+sub+'/'+run, self.decompressedDicoms+sub+'/'+run)
                                                        except NotImplementedError:
								for dcm in os.listdir(self.dicomDataPath+sub+'/'+run):
									try:
		                                                                subprocess.Popen(['dcmdjpeg', self.dicomDataPath+sub+'/'+run+'/'+dcm, self.decompressedDicoms+sub+'/'+run+'/'+dcm])
									except TypeError:
										try:
											subprocess.Popen(['dcmdrle', self.dicomDataPath+sub+'/'+run+'/'+dcm, self.decompressedDicoms+sub+'/'+run+'/'+dcm])
										except:
											sys.exit('Possibly broken DICOM: '+self.dicomDataPath+sub+'/'+run+'/'+dcm)


	def removeNonDtiScans(self):
		def checkIfDTI(sequence, protocol, bval):
			'''
			input: list of sequences (from both standard and private tags), protocol, and bvals from a dicom run

			Determine whether or not a particular dicom dataset is a DTI by parsing the sequence, protocol, and bval for strings that would indicate otherwise.
			'''
		        DTI = False
	        	if False not in [x not in ["tof", "fl3d", "memp", "fse", "grass", "3-Plane", "gre" ] for x in sequence]: #if none of the elements of sequence match any of the given values
	                	if re.search('(ep2(?!(FA)|(MD)|(ARC)|(EXP)|(LOWB)|(DWI)|(ADC)))|b|(ep_(?!(FA)|(MD)|(ARC)|(EXP)|(LOWB)|(DWI)|(ADC)))|(ep1(?!(FA)|(MD)|(ARC)|(EXP)|(LOWB)|(DWI)|(ADC)))', str(sequence), re.IGNORECASE):
	                	        DTI = True
	                	elif re.search('(1000)|(directional)',bval, re.IGNORECASE):
	                	        DTI = True
	                	elif re.search('dif', protocol, re.IGNORECASE):
	                	        DTI = True
	                	else:
	                	        pass
	        	return DTI

		for sub in os.listdir(self.decompressedDicoms):
		        if os.path.isdir(self.decompressedDicoms+sub):
		                for run in os.listdir(self.decompressedDicoms+sub):
		                        if os.path.isdir(self.decompressedDicoms+sub+'/'+run) == True:
		                                if any(mm.endswith('.dcm') for mm in os.listdir(self.decompressedDicoms+sub+'/'+run)):
		                                        sequence = []
		                                        protocol, bval = '',''
		                                        f = os.listdir(self.decompressedDicoms+sub+'/'+run)[0]
		                                        try:
		                                                ds = dicom.read_file(self.decompressedDicoms+sub+'/'+run+'/'+f)
		                                        except:
		                                                f = os.listdir(self.decompressedDicoms+sub+'/'+run)[1]
		                                                ds = dicom.read_file(self.decompressedDicoms+sub+'/'+run+'/'+f)

		                                        #####GENERAL SEQUENCE####
		                                        try:
		                                                sequence.append(ds[0x18,0x24].value)
		                                        except:
		                                                pass
		                                        try:
		                                                sequence.append(ds[0x18,0x20].value)
		                                        except:
		                                                pass

		                                        #####GENERAL PROTOCOL#####
		                                        try:
		                                                protocol = ds[0x18,0x1030].value
		                                        except:
		                                                pass
	
		                                        #####GENERAL BVAL########
		                                        try:
		                                                bval = ds[0x18,0x9087].value
		                                        except:
		                                                pass

		                                        ####SIEMENS#####
		                                        if ds.Manufacturer == 'SIEMENS':
		                                                if bval == '':
		                                                        try:
		                                                                bval = ds[0x19,0x100C].value
		                                                        except:
		                                                                pass

		                                        #####GE######## 
		                                        elif ds.Manufacturer == 'GE MEDICAL SYSTEMS':
		                                                try:
		                                                        sequence.append([0x19,0x109C].value)
		                                                except:
		                                                        pass
		                                                if bval == '':
		                                                        try:
		                                                                bval = ds[0x43,0x1039].value
		                                                        except:
		                                                                pass
		                                        else:
		                                                pass

		                                        DTI = checkIfDTI(sequence, str(protocol), str(bval))
		                                        if DTI == True:
		                                                self.dtiDataDicomPaths.append(self.decompressedDicoms+sub+'/'+run)
							else:
								self.notDTIdata.append(self.decompressedDicoms+sub+'/'+run)


	def convertToNii(self):
		'''
		Convert all of the dicom sets deemed DTI by the removeNonDTI function to nii utilizing the dcm2nii tool
		'''
		if os.path.exists(self.rawNiftis):
			shutil.rmtree(self.rawNiftis)
		os.mkdir(self.rawNiftis)
		for data in self.dtiDataDicomPaths:
			root, run = os.path.split(data)
			subject = os.path.split(root)[1]
			subprocess.call(['dcm2nii', '-d', 'N', '-i', 'N', '-p', 'N', '-o', self.rawNiftis+subject+'/'+run, data])
			if len(glob(self.rawNiftis+subject+'/'+run+'/*bval')) == 0 or len(glob(self.rawNiftis+subject+'/'+run+'/*bvec')) == 0:
				self.failedNiiConverts.append(data)
				shutil.rmtree(self.rawNiftis+subject+'/'+run)
		for root, dirs, files in os.walk(self.rawNiftis):
			for dir in dirs:
				if len(os.listdir(root+'/'+dir)) == 0:
					shutil.rmtree(root+'/'+dir)


	def removeBadBvalsAndBvecs(self):
		'''
		Goes through bval and bvec files and removes any that appear to be unusable. Criteria for unusable bvals consists of lacking at least one zero bval and/or having less than 6 non-zero bvals. Criteria for unusable bvec includes havinv less than or greater than 3 rows (x,y,z) and/or having different numbers of values in each line.
		'''
		for sub in os.listdir(self.rawNiftis):
			for run in os.listdir(self.rawNiftis+sub):
				runPath = self.rawNiftis+sub+'/'+run+'/'
				bvalFile = open(runPath+glob(runPath+'*bval')[0])
				bvecFile = open(runPath+glob(runPath+'*bvec')[0])
				validBval, validBvec, zeroVal = True, True, False
				nonZeroVals = []
				bvalLine = bvalFile.readlines()[0].split(' ')
				for val in bvalLine:
					if str(val) == '0':
						zeroVal = True
					else:
						nonZeroVals.append(str(val))
				if '-' in str(bvalLine):
					self.negativeBval.append(runPath)
					validBval = False

				if zeroVal == False:
					self.noZeroBval.append(runPath)
					validBval = False

				if len(nonZeroVals) >= 6:
					self.lessThanSixBval.append(runPath)
					validBval = False

				bvecLines = bvecFile.readlines()
				if len(bvecLines) != 3:
					self.wrongNumBvecs.append(runPath)
					validBvec = False 
				if not len(bvecLines[0].split(' ')) == len(bvecLines[1].split(' ')) == len(bvecLines[2].split(' ')):
					self.mismatchedBvecLength
					validBvec = False
				else:
					if len(bvecLines[0].split(' ')) != len(bvalLine):
						self.difNumBvalBvec.append(runPath)
						validBvec = False

				if validBval + validBvec != 2:
					shutil.rmtree(runPath)
		for root, dirs, files in os.walk(self.rawNiftis):
			for dir in dirs:
				if len(os.listdir(root+'/'+dir)) == 0:
					shutil.rmtree(root+'/'+dir)


	def processDTI(self, parallel, numNodes=100, user=None):
		'''
		Inputs:
			parallel: True or False. If true, this function will write out a shell script that when run on the martinos launchpad server will submit a seperate processing script for each dataset to the cluster, thereby parallelizing the process. This is highly recommended if you are a part of the martinos network.
			numNodes: Integer. Maximum number of nodes to be used at a single time. Default is 100.
			user: String. Martinos username that launchpad jobs will be attributed to. Does not need to be set if not running in paralell.

		This function performs basic processing of a set of DTI data either in parallel or sequentially. It first eddy corrects each volume using fsl's `eddy_correct` function. Then, it rotates the bvec fileand performs skill stripping using fsl's `bet` tool. The skill stripping is performed with a thresholded fractional intensity of 0.315 (-f flag). If you'd like to change this threshold, you will have to do so by editing the DiffRecon_Rotate_B_Matrix.sh script. `bet` also generates a binary mask of the points it removed (-m flag). Finally, it peforms DTI reconstruction using fsl's 
		'''
		self.processedData = self.savePath+'processedData/'
		self.parallelProcessingScript = self.savePath+'parallelProcessing.sh'
		if os.path.exists(self.processedData):
			shutil.rmtree(self.processedData)
		os.mkdir(self.processedData)
		if parallel == True:
			print 'Generating tcsh script at %s which, when executed on the launchpad server, will automatically submit jobs to process the specified data in paralell. NOTE: THIS IS ONLY CONFIGURED TO WORK ON THE MARTINOS CLUSTER. IT IS UNLIKELY TO WORK ANYWHERE ELSE.'%self.parallelProcessingScript
			if user == None:
				sys.exit('User flag necessary to generate parallelized script.')
			f = open(self.parallelProcessingScript, 'w')
			f.write('#!/usr/local/bin/tcsh')
			f.write('foreach sub ( $s* )'%self.rawNiftis)
			f.write('\tsetenv subject `basename $sub`')
			f.write('\tforeach run ( $sub/* )')
			f.write('\t\tsetenv rundir `basename $run`')
			f.write('\t\tpbsubmit -q max%d -m %s -c "%sDiffRecon_Rotate_B_Matrix.sh -i $run -o %s"'%(numNodes, user, self.savePath, self.processedData))
			f.write('\tend')
			f.write('end')
			f.close()
		else:
			for sub in os.listdir(self.rawNiftis):
				for run in os.listdir(self.rawNiftis+sub):
					subprocess.call([self.savePath+'DiffRecon_Rotate_B_Matrix.sh', '-i', self.processedData, self.rawNiftis+sub+'/'+run, '-o', self.processedData])


	def makeThresholdedDTIMaps(self, threshval=1.0):
		'''
		Inputs:
			threshval: float. value you would like to threshold FA maps at (default = 1.0).
		Takes all of the FA maps for the dataset and uses `fslmaths -thr` to create a binary mask of the FA map where all of the pixels above threshval (default = 1.0) are set to 1.0 and all values lower than 1.0 are set to 0.0. It then inverts that mask using `fsl -bvin` so that the values greater that were originally greater than 1.0 are set to 0.0 and the values originally less than 1.0 are set to 1.0. Both the original FA map and the MD map are multiplied by this new, inverse mask resulting in FA and MD maps in which the "extreme" pixel values have been removed.
		'''
		for sub in os.listdir(self.rawNiftis):
			for run in os.listdir(self.rawNiftis+sub):
				runDir = self.rawNiftis+sub+'/'+run
				subprocess.call(['flsmaths', runDir+'/fsl_FA.nii.gz', '-thr', threshval, runDir+'/out.nii.gz'])
				subprocess.call(['fslmaths', runDir+'/out.nii.gz', '-binv', runDir+'/inverseMask.nii.gz'])
				subprocess.call(['fslmaths', runDir+'/inverseMask.nii.gz', '-mul', runDir+'/fsl_FA.nii.gz', runDir+'/thresholded_FA.nii.gz'])
				subprocess.call(['fslmaths', runDir+'/inverseMask.nii.gz', '-mul', runDir+'/fsl_MD.nii.gz', runDir+'/thresholded_MD.nii.gz'])
				os.remove(runDir+'/out.nii.gz')
				os.remove(runDir+'/inverseMask.nii.gz')


	def exportToCsv(self):
		with open(self.savePath+'removedFiles.csv', 'wb') as csvfile:
			writer = csv.writer(csvfile, delimiter=' ')
			writer.writerow(['Dicoms That Are Not DTI']+self.notDTIdata)
			writer.writerow(['Dicoms That Failed To Be Converted To Nifti']+self.failedNiiConverts)
			writer.writerow(['Niftis Without A Zero Bval']+self.noZeroBval)
			writer.writerow(['Niftis With Negative Bval']+self.negativeBval)
			writer.writerow(['Niftis With Less Than 6 Non Zero Bvals']+self.lessThanSixBval)
			writer.writerow(['Bvecs Without 3 Rows']+self.wrongNumBvec)
			writer.writerow(['Bvecs With Non Matching Direction Lengths']+self.mismatchedBvecLength)
			writer.writerow(['Niftis With Different Numbers of Bvals and Bvecs']+self.difNumBvalBvec)
			csvfile.close()
