import csv, os, re, dicom, sys, shutil, glob

root = '/space/jazz/1/users/gwarner/decompressedMi2b2Data/'
niftis = '/space/jazz/1/users/gwarner/niftis/'
output = '/space/jazz/1/users/gwarner/realDtiData/'

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

shutil.rmtree(output)
os.mkdir(output)

copied = 0

for sub in os.listdir(niftis):
        if os.path.isdir(niftis+sub):
                for run in os.listdir(niftis+sub):
                        if os.path.isdir(niftis+sub+'/'+run) == True and len(os.listdir(niftis+sub+'/'+run)) != 0:
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
					if len(glob.glob('*bval')) != 0:
						for bar in os.listdir(niftis+sub+'/'+run):
							if bar.endswith('bval'):
								bv = niftis+sub+'/'+run+'/'+bar
						bvalFile = open(bv, 'rb')
						lines = bvalFile.readlines()
						line = lines[0]
						vals = line.split(' ')
						newVals = []
						for v in vals:
							if str(v) != '0':
								newVals.append(v)
						if len(vals) >= 6:
							if DTI == True:
								if os.path.exists(output+sub) == False:
									os.mkdir(output+sub)
								shutil.copytree(niftis+sub+'/'+run, output+sub+'/'+run)
								copied += 1
print '%d datasets copied'%copied
