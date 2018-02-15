import os, re, glob, sys, shutil

start = '/space/jazz/1/users/gwarner/niftis/'

for sub in os.listdir(start):
	for run in os.listdir(start+sub):
		if os.path.exists(start+sub+'/'+run+'/.bval'):
			os.chdir(start+sub+'/'+run)
			f = glob.glob('*.gz')
			name = re.search('(.*)\.nii\.gz',f[0]).group(1)
			os.rename(start+sub+'/'+run+'/.bval', start+sub+'/'+run+'/'+name+'.bval')
			try:
				os.rename(start+sub+'/'+run+'/.bvec', start+sub+'/'+run+'/'+name+'.bvec')
			except:
				print 'bvec not found for ',start+sub+'/'+run+'/'+name
