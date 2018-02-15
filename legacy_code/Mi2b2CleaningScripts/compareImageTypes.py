import os, re, shutil, sys, dicom, glob

niftis = '/space/jazz/1/users/gwarner/niftis/'
dcms = '/space/jazz/1/users/gwarner/decompressedMi2b2Data/'

bvalWorked, bvalFailed = set(), set()

for sub in os.listdir(niftis):
	for series in os.listdir(niftis+sub):
		if len(os.listdir(niftis+sub+'/'+series)) != 0:
			os.chdir(niftis+sub+'/'+series)	
			f = os.listdir(dcms+sub+'/'+series)[0]
			ds = dicom.read_file(dcms+sub+'/'+series+'/'+f)
			imageType = str(ds.ImageType)
			if len(glob.glob('*.bval')) != 0:
				bvalWorked.add(imageType)
			else:
				bvalFailed.add(imageType)

print 'Image Types for files that generated .bval file:'
print bvalWorked
print '\n\nImage Types for files that DID NOT generate .bval file:'
print bvalFailed
