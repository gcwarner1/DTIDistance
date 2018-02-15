import dicom, os, subprocess, sys, shutil, re, time

failed = []
root = '/space/jazz/1/users/gwarner/compressedMi2b2Data/'
for base in os.listdir(root):
        for sub in os.listdir(root+base):
                if os.path.isdir(root+base+'/'+sub):
                        for scan in os.listdir(root+base+'/'+sub):
                                if os.path.isdir(root+base+'/'+sub+'/'+scan):
                                        for f in os.listdir(root+base+'/'+sub+'/'+scan):
						if f.endswith('.dcm'):
							if os.path.exists('/space/jazz/1/users/gwarner/decompressedMi2b2Data/'+sub+'/'+scan+'/'+f) == False:
								subprocess.call(['dcmdrle', root+base+'/'+sub+'/'+scan+'/'+f, '/space/jazz/1/users/gwarner/decompressedMi2b2Data/'+sub+'/'+scan+'/'+f])
