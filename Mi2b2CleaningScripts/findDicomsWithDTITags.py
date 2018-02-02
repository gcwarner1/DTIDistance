import os, re, shutil, sys, dicom

root = '/space/jazz/1/users/gwarner/decompressedMi2b2Data/'

scannerModel = set()
dti = 0
other = 0
total = 0
seriess = 0
empty = 0
ge = 0
siemens = 0
philips = 0
badVendor = 0
failedModel = 0
tagsForUnknown= []
badVendorFiles = []

vendorDict = {"SIEMENS": [0x19,0x100D],
	      "GE MEDICAL SYSTEMS": [0x43,0x1039],
	      "PHILIPS": [0x18,9089]}

for sub in os.listdir(root):
	if os.path.isdir(root+sub):
		for run in os.listdir(root+sub):
			if os.path.isdir(root+sub+'/'+run) == True:
				total += 1
				seriess += 1
				if any(mm.endswith('.dcm') for mm in os.listdir(root+sub+'/'+run)):
					f = os.listdir(root+sub+'/'+run)[0]
					try:
						ds = dicom.read_file(root+sub+'/'+run+'/'+f)
					except:
						f = os.listdir(root+sub+'/'+run)[1]
						ds = dicom.read_file(root+sub+'/'+run+'/'+f)
					try:
						scannerModel.add(str(ds[0x08,0x1090].value))
						#print ds[0x08,0x1090]
					except KeyError:
						try:
							tagsForUnknown.append(str(ds[0x08,0x1090].value))
						except KeyError:
							pass
						failedModel += 1
					try:
						tags = vendorDict[ds.Manufacturer]
						if ds.Manufacturer == "SIEMENS":
							siemens += 1
						elif ds.Manufacturer == "GE MEDICAL SYSTEMS":
							ge += 1
						elif ds.Manufacturer == "PHILIPS":
							philips += 1
						else:
							pass
						try:
							ds[tags[0],tags[1]]
							dti += 1
						#	print 'SUCCESS: '+root+sub+'/'+run+'/'+f
						except KeyError:
							other += 1
						#	print 'FAIL: '+root+sub+'/'+run+'/'+f
					except KeyError:
						badVendor += 1
						badVendorFiles.append(root+sub+'/'+run+'/'+f)
				else:
					empty += 1
print 'DTI = '+str(dti)
print 'Other = '+str(other)
print 'Total = '+str(total)
print 'Series = '+str(seriess)
print 'Empty = '+str(empty)
print 'GE = '+str(ge)
print 'Siemens = '+str(siemens)
print 'Philips = '+str(philips)
print 'Bad vendor = '+str(badVendor)
print 'Unique Scanner Models = '+str(len(scannerModel))
print 'Unfound Scanner Models = '+str(failedModel)
print tagsForUnknown
print badVendorFiles
