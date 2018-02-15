import os, re, glob, sys, shutil, dicom

bval, nii = [], []
totalDirs, popDirs = 0,0
base = '/space/jazz/1/users/gwarner/niftis/'

for sub in os.listdir(base):
	for run in os.listdir(base+sub):
		totalDirs += 1
		os.chdir(base+sub+'/'+run)
		if len(os.listdir(base+sub+'/'+run)) != 0:
			popDirs += 1
		if len(glob.glob('*nii.gz')) != 0:
			nii.append(base+sub+'/'+run)
		if len(glob.glob('*.bval')) != 0:
			bval.append(base+sub+'/'+run)

print 'Series with .bved file: ',len(bval)
print 'Series with nii file: ',len(nii)
print 'Total series: ',totalDirs
print 'Series with files: ',popDirs
