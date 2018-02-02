import os, dicom, sys

fails = 0
total = 0
for root, dirs, files in os.walk('/space/jazz/1/users/gwarner/decompressedMi2b2Data/'):
	for dir in dirs:
		total += 1
		if len(os.listdir(root+'/'+dir)) == 0:
			fails += 1
			print root+'/'+dir
print fails
print total
