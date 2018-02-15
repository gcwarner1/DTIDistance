import os, re, dicom, sys, shutil, glob

root = '/space/jazz/1/users/gwarner/decompressedMi2b2Data/'
niftis = '/space/jazz/1/users/gwarner/niftis/'

def checkIfDTI(sequence):
	DTI = True
	for x in ['ADC', 'MD', 'FA', 'EXP','LOWB', 'DWI']:
		if re.search('ep2_'+x, str(sequence), re.IGNORECASE):
			DTI = False
		elif re.search('ep_'+x, str(sequence), re.IGNORECASE):
			DTI = False
		elif re.search('ep1_'+x, str(sequence), re.IGNORECASE):
			DTI = False
		else:
			pass
	return DTI

total = 0
dic = {'bval':{'dti':0,'dwi map':0}, 'nobval':{'dti':0,'dwi map':0}}
dtiData = []
dtiSize = []
notDtiSize = []

for sub in os.listdir(niftis):
        if os.path.isdir(niftis+sub):
                for run in os.listdir(niftis+sub):
                        if os.path.isdir(niftis+sub+'/'+run) == True and len(os.listdir(niftis+sub+'/'+run)) != 0:
					total += 1
					sequence = []
                                        f = os.listdir(root+sub+'/'+run)[0]
                                        try:
                                                ds = dicom.read_file(root+sub+'/'+run+'/'+f)
                                        except:
                                                f = os.listdir(root+sub+'/'+run)[1]
                                                ds = dicom.read_file(root+sub+'/'+run+'/'+f)

					#####GENERAL SEQUENCE####
					try:
						sequence.append(ds[0x18,0x24].value)
					except:
						pass
					try:
						sequence.append(ds[0x18,0x20].value)
					except:
						pass

					#####GE########	
					if ds.Manufacturer == 'GE MEDICAL SYSTEMS':
						try:
							sequence.append([0x19,0x109C].value)
						except:
							pass
					else:
						pass

					DTI = checkIfDTI(sequence)
					os.chdir(niftis+sub+'/'+run)
					if len(glob.glob('*bval')) == 0:
						if DTI == True:
							dic['nobval']['dti'] += 1
						else:
							dic['nobval']['dwi map'] += 1
					else:
						if DTI == True:
							dic['bval']['dti']+=1
						else:
							dic['bval']['dwi map']+=1
					

print 'Total series: ',total
print dic
