import os, dicom, sys, shutil

broken = True
while broken == True:
	broken = False
	for root, dirs, files in os.walk('/space/jazz/1/users/gwarner/newMi2b2/'):
		for dir in dirs:
			if len(os.listdir(root+'/'+dir)) == 0:
				shutil.rmtree(root+'/'+dir)
				broken = True
