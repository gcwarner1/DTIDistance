import os, sys

root = '/space/jazz/1/users/gwarner/testDTIData/'

for ii in os.listdir(root):
	for x in os.listdir(root+ii):
		if x.startswith('fsl') or x.startswith('bvec') or x.startswith('mask') or x.startswith('diff_mc_st'):
			os.remove(root+ii+'/'+x)
