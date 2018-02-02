#!/space/jazz/1/users/gwarner/anaconda/bin python

import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import os, sys, shutil, argparse, glob, xlrd, re, string, csv, ast, json
from combined_csvUtils import *

def make(man):
	root = '/space/jazz/1/users/gwarner/histograms/'
	if man == 'Siemens':
		#spread=['histdist_results_SIEMENS_manufacturers_1.5_%s.csv'%Map, 'histdist_results_SIEMENS_manufacturers_3.0_%s.csv'%Map]
		#spread=['histdist_results_SIEMENS_manufacturers_1000_%s.csv'%Map, 'histdist_results_SIEMENS_manufacturers_700_%s.csv'%Map, 
		spread= [root+x for x in ['histdist_results_SIEMENS_FA.csv', 'histdist_results_SIEMENS_MD.csv']]
		#spread=['histdist_results_1.5_30_Directions_1000_bval_%s.csv'%Map, 'histdist_results_3.0_30_Directions_1000_bval_%s.csv'%Map]
		#spread = ['histdist_results_SIEMENS_1000_bval_30_dirs_1.5T_%s.csv'%Map, 
		#spread=['histdist_results_SIEMENS_1000_bval_30_dirs_3.0T_%s.csv'%Map]
	elif man == 'GE':
		#spread=['histdist_results_GE_manufacturers_1.5_%s.csv'%Map]#, 'histdist_results_GE_manufacturers_3.0_%s.csv'%Map]
		spread = [root+x for x in ['histdist_results_GE_manufacturers_1000_FA.csv', 'histdist_results_GE_manufacturers_1000_MD.csv']]
		#spread = ['histdist_results_GE_1000_bval_30_dirs_1.5T_%s.csv'%Map]
	else:
		sys.exit('Invalid manufacturer')#	if Map == 'FA':

	genHistograms(spread, Manufacturer=man)#'/space/jazz/1/users/gwarner/histograms/'+x, Manufacturer=man, Map=Map)

#make('Siemens')
make('GE')
