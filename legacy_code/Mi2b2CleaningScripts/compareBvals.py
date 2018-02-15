import os, re, shutil, sys, dicom, glob

niftis = '/space/jazz/1/users/gwarner/niftis/'
dcms = '/space/jazz/1/users/gwarner/decompressedMi2b2Data/'

bvalWorked, bvalFailed = {'SIEMENS':[], 'GE MEDICAL SYSTEMS':[], '':[]}, {'SIEMENS':[], 'GE MEDICAL SYSTEMS':[], '':[]}

def grabBval(path):
	bval = []
	for f in os.listdir(path):
		try:
			ds = dicom.read_file(path+f)
		except:
			try:
				f = os.listdir(path)[1]
				ds = dicom.read_file(path+f)
			except:
				sys.exit('Broken: '+path+f)
	#try:
	#	bval = ds[0x18,0x9087].value
	#except:
		if ds.Manufacturer == 'SIEMENS':
			try:
				bval.append(str(ds[0x19,0x100C].value))
			except:
				bval.append('')
				#print 'Bval not found for: ',path+f
			man = ds.Manufacturer
		elif ds.Manufacturer == 'GE MEDICAL SYSTEMS':
			try:
				bval.append(str(list(ds[0x43,0x1039].value)[0]))
			except:
				bval.append('')
				#print 'Bval not found for: ',path+f
			man = ds.Manufacturer
		else:
			print 'No manufacturer for: ',path+f
			bval.append('')
			man = ''
	return bval, str(man)
for sub in os.listdir(niftis):
	for series in os.listdir(niftis+sub):
		bval, man = grabBval(dcms+sub+'/'+series+'/')
		if len(glob.glob(niftis+sub+'/'+series+'/*.bval')) != 0:
			bvalWorked[man].append(bval)
		else:
			bvalFailed[man].append(bval)
for x in bvalWorked: #SIEMENS
	newList = {}
	for k in set(bvalWorked[x]):
		newList[k] = bvalWorked[x].count(k)
	print 'Bval Worked '+x
	print newList
print '\n\n'	
for x in bvalWorked: #SIEMENS
        newList = {}
        for k in set(bvalWorked[x]):
                newList[k] = bvalWorked[x].count(k)
        print 'Bval Failed '+x
        print newList

print '\n\n'
print 'Bvals of files that generated .bval file (%d):'%len(bvalWorked)
print set(bvalWorked)
print '\n\nBvals of files that DID NOT generate .bval file (%d):'%len(bvalFailed)
print set(bvalFailed)
print '\n\n\n\n'

