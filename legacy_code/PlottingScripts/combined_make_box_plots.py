import os, re, sys, scipy, ast, math, argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import median_test, mannwhitneyu
from pprint import pprint

def makeBoxPlots(comparison):
	def get_axis_limits(ax, scale=.9):
		return ax.get_xlim()[1]*scale, ax.get_ylim()[1]*scale

	files = {}
	data = {'FA':{},'MD':{}}
	for Map in ['FA', 'MD']:
		root = '/space/jazz/1/users/gwarner/histograms/'+Map+'/'
		if comparison == 'gesiemens1000':
			files[Map] = [root+x for x in ['histdist_results_GE_manufacturers_1000_%s_data_points.txt'%Map, 'histdist_results_SIEMENS_manufacturers_1000_%s_data_points.txt'%Map]]
		elif comparison == 'between':
			files[Map] = [root+x for x in ['GE_data_points.txt', 'histdist_results_SIEMENS_%s_data_points.txt'%Map]]#'siemens_data_points.txt']]
		elif comparison == '7001000':
			files[Map] = [root+x for x in ['histdist_results_SIEMENS_manufacturers_700_%s_data_points.txt'%Map,'histdist_results_SIEMENS_manufacturers_1000_%s_data_points.txt'%Map]]
		elif comparison == 'between1.5T':
			files[Map] = [root+x for x in ['histdist_results_GE_manufacturers_1.5_%s_data_points.txt'%Map,'histdist_results_SIEMENS_manufacturers_1.5_%s_data_points.txt'%Map]]
		elif comparison == 'Siemens3Tvs1.5T':
			files[Map] = [root+x for x in ['histdist_results_SIEMENS_manufacturers_1.5_%s_data_points.txt'%Map,'histdist_results_SIEMENS_manufacturers_3.0_%s_data_points.txt'%Map]]
	        elif comparison == '1.5vs3.0SiemensDirsBval':
			files[Map] = [root+x for x in ['histdist_results_SIEMENS_1000_bval_30_dirs_1.5T_%s_data_points.txt'%Map, 'histdist_results_SIEMENS_1000_bval_30_dirs_3.0T_%s_data_points.txt'%Map]]
		
                #files = [root+x for x in ['histdist_results_1.5_30_Directions_1000_bval_%s_data_points.txt'%Map,'histdist_results_3.0_30_Directions_1000_bval_%s_data_points.txt'%Map]]
		elif comparison == 'GESiemensBvalFieldDirControlled':
			files[Map] = [root+x for x in ['histdist_results_GE_1000_bval_30_dirs_1.5T_%s_data_points.txt'%Map, 'histdist_results_SIEMENS_1000_bval_30_dirs_1.5T_%s_data_points.txt'%Map]]
		elif comparison == 'GE6vs25DirBvalFieldControlled':
	                files = [root+x for x in ['histdist_results_GE_6_Dirs_1.5T_1000_bval_%s_data_points.txt'%Map, 'histdist_results_GE_25_Dirs_1.5T_1000_bval_%s_data_points.txt'%Map]]
		else:
			sys.exit('Bad comparison')
	for Map in ['FA','MD']:
		for spreadsheet in files[Map]:
		        f = open(spreadsheet,'r')
		        lines = f.readlines()
		        oneline = ' '.join(lines).replace('\n','')
			dataDict = ast.literal_eval(oneline)
			vals = dataDict['hellinger'][1] #zeroth index is x values, we want y values
			vals.sort()
			numpyarray = np.array(vals)
			data[Map][spreadsheet] = numpyarray
	font = 'Times New Roman'
	#plt.rc({'font': 'Times New Roman'})
	fig = plt.figure()
	ax1 = fig.add_subplot(121)
	ax2 = fig.add_subplot(122)
	fig.subplots_adjust(wspace=0.65)
	plt.rcParams['font.family'] = font
	plt.rcParams['font.size'] = 12
	ax1.set_ylabel('Distance')#, fontsize=12)#, fontname=font)
	#ax1.xticks(rotation=10, fontsize=12)
	ax2.set_ylabel('Distance')#, fontsize=12)#, fontname=font)
	#ax2.set_xticks(rotation=10, fontsize=12)
	for tick in ax1.get_xticklabels():
		tick.set_rotation(10)
		#tick.fontname=font
	for tick in ax2.get_xticklabels():
		tick.set_rotation(10)
		#tick.fontname=font
	#ax1.annotate('A.', xy=(10,10))# xy=get_axis_limits(ax1))
	#ax2.annotate('B.', xy=(50,50))#get_axis_limits(ax2))
	ax1.set_title('FA')#, fontname=font)
	ax2.set_title('MD')#, fontname=font)
	axDict = {'FA': ax1, 'MD': ax2}
	for Map in ['FA','MD']:
		info, labels = [], []
		Keys = data[Map].keys()
		Keys.sort()
		for f in Keys:
			info.append(data[Map][f])
			if comparison == '7001000':
				man = f.split('_')[4]+' mm$^2$/s'
				labels.append(man)#+' (n='+str(len(data[Map][f]))+')')
			elif comparison == 'gesiemens1000':
				man = f.split('_')[2]
				labels.append(man)#+' (n='+str(len(data[Map][f]))+')')
			elif comparison == 'between':
				if 'SIEMENS' in f:
					labels.append('SIEMENS')# (n='+str(len(data[Map][f]))+')')
				else:
					labels.append('GE')# (n='+str(len(data[Map][f]))+')')
			elif comparison == 'between1.5T':
				man = f.split('_')[2]
				labels.append(man)#+' (n='+str(len(data[Map][f]))+')')
			elif comparison == 'Siemens3Tvs1.5T':
				man = f.split('_')[4]+'T'
				labels.append(man)#+' (n='+str(len(data[Map][f]))+')')
			elif comparison == '1.5vs3.0SiemensDirsBval':
				man = f.split('_')[7]
				labels.append(man)#+' (n='+str(len(data[Map][f]))+')')
			elif comparison == 'GESiemensBvalFieldDirControlled':
				man = f.split('_')[2]
				labels.append(man)#+' (n='+str(len(data[Map][f]))+')')
			elif comparison == 'GE6vs25DirBvalFieldControlled':
                                man = f.split('_')[3]+' Directions'
                                labels.append(man+' (n='+str(len(data[metric][f]))+')')
			else:
				sys.exit('Bad comparison ',comparison)
		m = axDict[Map].boxplot(x=info,labels=labels, medianprops={'color':'black'})
		#axDict[Map].set_xticks(fontsize=14)
        	#axDict[Map].yticks(fontsize=14)
	if comparison == 'gesiemens1000':
		#fig.suptitle('GE 1000 B-value vs Siemens 1000 B-value Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/boxplots/Siemens_vs_GE_1000_bval_Hellinger.png')
	elif comparison == '7001000':
		#fig.suptitle('Siemens 1000 B-value vs Siemens 700 B-value Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/boxplots/Siemens_700_vs_Siemens_1000_bval_Hellinger.png')
	elif comparison == 'between1.5T':
		#fig.suptitle('GE 1.5T vs Siemens 1.5T Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/boxplots/GE_1.5T_vs_Siemens_1.5T_Hellinger.png')
	elif comparison == 'Siemens3Tvs1.5T':
		#fig.suptitle('Siemens 1.5T vs Siemens 3.0T Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/boxplots/Siemens_1.5T_vs_Siemens_3.0T_Hellinger.png')
	elif comparison == '1.5vs3.0SiemensDirsBval':
		#fig.suptitle('1.5T vs 3.0T Siemens 30 Gradient Directions 1000 B-Value')
                plt.savefig('/space/jazz/1/users/gwarner/boxplots/Siemens_1.5T_30_Directions_1000_Bval_vs_Siemens_3.0T_30_Directions_1000_Bval_Hellinger.png')
	elif comparison == 'GESiemensBvalFieldDirControlled':
		#fig.suptitle('GE vs Siemens 1000 B-Value 30 Gradient Directions 1.5T Hellinger')
                plt.savefig('/space/jazz/1/users/gwarner/boxplots/GE_vs_Siemens_1000_B-Value_30_Gradient_Directions_1.5T_Hellinger.png')
	elif comparison == 'GE6vs25DirBvalFieldControlled':
		plt.savefig('/space/jazz/1/users/gwarner/boxplots/histdist_results_GE_6_dirs_vs_25_dirs_1.5T_1000_bval_Hellinger.png')
	else:
		#fig.suptitle('All GE vs All Siemens Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/boxplots/All_GE_vs_All_SIEMENS_Hellinger.png')

#makeBoxPlots('GESiemensBvalFieldDirControlled')
#makeBoxPlots('between1.5T')
#makeBoxPlots('Siemens3Tvs1.5T')
#makeBoxPlots('gesiemens1000')
#makeBoxPlots('between')
#makeBoxPlots('7001000')
#makeBoxPlots('1.5vs3.0SiemensDirsBval')
makeBoxPlots('GE6vs25DirBvalFieldControlled')
