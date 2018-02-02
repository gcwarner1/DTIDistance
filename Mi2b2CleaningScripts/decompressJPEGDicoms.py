import os, re, dicom, subprocess, shutil, sys

input = '/space/jazz/1/users/gwarner/compressedMi2b2Data/'
output = '/space/jazz/1/users/gwarner/decompressedMi2b2Data/'

def conv(input, output):
	print '\n\n\n\nStart for '+input
	for sub in os.listdir(input):
		if os.path.isdir(input+sub):
			for run in os.listdir(input+sub):
				if os.path.isdir(input+sub+'/'+run):
					for f in os.listdir(input+sub+'/'+run):
						print 'File: '+input+sub+'/'+run+'/'+f
						if f.endswith('.dcm'):
							print 'File is dicom'
							ds = dicom.read_file(input+sub+'/'+run+'/'+f)
							if os.path.exists(output+sub) == False:
								os.mkdir(output+sub)
							if os.path.exists(output+sub+'/'+run) == False:
								os.mkdir(output+sub+'/'+run)
							try:
								ds.pixel_array
								shutil.copy(input+sub+'/'+run+'/'+f, output+sub+'/'+run+'/'+f)
								print 'UNCOMPRESSED DICOM\n\n'
							except NotImplementedError:
								print 'Compressed dicom...'
								subprocess.Popen(['dcmdjpeg', input+sub+'/'+run+'/'+f, output+sub+'/'+run+'/'+f])
								if os.path.exists(output+sub+'/'+run+'/'+f) == True:
									print 'Copied successfully\n\n'
								else:
									print 'Failed to copy\n\n'
							except TypeError:
								print 'TypeError'
								pass
						else:
							print 'File is NOT dicom\n\n'
							if os.path.exists(output+sub) == False:
								os.mkdir(output+sub)
							if os.path.exists(output+sub+'/'+run):
								os.mkdir(output+sub+'/'+run)
							shutil.copy(input+sub+'/'+run+'/'+f, output+sub+'/'+run+'/'+f)
				else:
					if os.path.exists(output+sub) == False:
						os.mkdir(output+sub)
					shutil.copy(input+sub+'/'+run, output+sub+'/'+run)
		else:
			shutil.copy(input+sub, output+sub)
conv(input+'First/', output)
conv(input+'Second/', output)
conv(input+'Third/', output)
conv(input+'Fourth/', output)
