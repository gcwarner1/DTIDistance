import os, re, sys, scipy, ast, math, argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from scipy.stats import median_test, mannwhitneyu, ks_2samp
from pprint import pprint

def get_axis_limits(ax):
	return ax.get_xlim()[0]*1.1, ax.get_ylim()[1]*0.7

def makeKorsakovPlots(comparison, Map):
	root = '/space/jazz/1/users/gwarner/histograms/'+Map+'/'
	if comparison == 'gesiemens1000':
		files = [root+x for x in ['histdist_results_GE_manufacturers_1000_%s_data_points.txt'%Map, 'histdist_results_SIEMENS_manufacturers_1000_%s_data_points.txt'%Map]]
	elif comparison == 'between':
		files = [root+x for x in ['GE_data_points.txt', 'histdist_results_SIEMENS_%s_data_points.txt'%Map]]#'siemens_data_points.txt']]
	elif comparison == '7001000':
		files = [root+x for x in ['histdist_results_SIEMENS_manufacturers_700_%s_data_points.txt'%Map,'histdist_results_SIEMENS_manufacturers_1000_%s_data_points.txt'%Map]]
	elif comparison == 'between1.5T':
		files = [root+x for x in ['histdist_results_GE_manufacturers_1.5_%s_data_points.txt'%Map,'histdist_results_SIEMENS_manufacturers_1.5_%s_data_points.txt'%Map]]
	elif comparison == 'Siemens3Tvs1.5T':
		files = [root+x for x in ['histdist_results_SIEMENS_manufacturers_1.5_%s_data_points.txt'%Map,'histdist_results_SIEMENS_manufacturers_3.0_%s_data_points.txt'%Map]]
	elif comparison == '1.5vs3.0SiemensDirsBval':
		files = [root+x for x in ['histdist_results_SIEMENS_1000_bval_30_dirs_1.5T_%s_data_points.txt'%Map, 'histdist_results_SIEMENS_1000_bval_30_dirs_3.0T_%s_data_points.txt'%Map]]
				#files = [root+x for x in ['histdist_results_1.5_30_Directions_1000_bval_%s_data_points.txt'%Map,'histdist_results_3.0_30_Directions_1000_bval_%s_data_points.txt'%Map]]
	elif comparison == 'GESiemensBvalFieldDirControlled':
		files = [root+x for x in ['histdist_results_GE_1000_bval_30_dirs_1.5T_%s_data_points.txt'%Map, 'histdist_results_SIEMENS_1000_bval_30_dirs_1.5T_%s_data_points.txt'%Map]]
	elif comparison == 'GE6vs25DirBvalFieldControlled':
		files = [root+x for x in ['histdist_results_GE_6_Dirs_1.5T_1000_bval_%s_data_points.txt'%Map, 'histdist_results_GE_25_Dirs_1.5T_1000_bval_%s_data_points.txt'%Map]]
	else:
		sys.exit('Bad comparison')
	data = {"hellinger":{}}
	for spreadsheet in files:
		f = open(spreadsheet,'r')
		lines = f.readlines()
		oneline = ' '.join(lines).replace('\n','')
		dataDict = ast.literal_eval(oneline)
		vals = dataDict["hellinger"][1] #zeroth index is x values, we want y values
		vals.sort()
		numpyarray = np.array(vals)
		data["hellinger"][spreadsheet] = numpyarray
	for metric in ['hellinger']:
		info, labels = [], []
		Keys = data[metric].keys()
		Keys.sort()
		for f in Keys:
			info.append(data[metric][f])
			if comparison == '7001000':
				man = f.split('_')[4]
				labels.append(man+' (n='+str(len(data[metric][f]))+')')
			elif comparison == 'gesiemens1000':
				man = f.split('_')[2]
				labels.append(man+' (n='+str(len(data[metric][f]))+')')
			elif comparison == 'between':
				if 'SIEMENS' in f:
					labels.append('Siemens (n='+str(len(data[metric][f]))+')')
				else:
					labels.append('GE (n='+str(len(data[metric][f]))+')')
			elif comparison == 'between1.5T':
				man = f.split('_')[2]
				labels.append(man+' (n='+str(len(data[metric][f]))+')')
			elif comparison == 'Siemens3Tvs1.5T':
				man = f.split('_')[4]+'T'
				labels.append(man+' (n='+str(len(data[metric][f]))+')')
			elif comparison == '1.5vs3.0SiemensDirsBval':
				man = f.split('_')[7]
				labels.append(man+' (n='+str(len(data[metric][f]))+')')
			elif comparison == 'GESiemensBvalFieldDirControlled':
				man = f.split('_')[2]
				labels.append(man+' (n='+str(len(data[metric][f]))+')')
			elif comparison == 'GE6vs25DirBvalFieldControlled':
				man = f.split('_')[3]+' Directions'
				labels.append(man+' (n='+str(len(data[metric][f]))+')')
			else:
				sys.exit('Bad comparison ',comparison)
		print '\n\n'+comparison+' '+Map
		print len(info[0]), len(info[1])
		print max(info[0]), max(info[1])
		print 'KS Test: '+str(ks_2samp(info[0], info[1]))
		pprint ([(i, ks_2samp(info[0], info[1][:i])[1])
			for i in range(200,len(info[1]),100)])
		fig, ax = plt.subplots(figsize=(8,4))
		plt.xlabel('Hellinger Distance', fontsize=14)
		plt.ylabel('Cumulative Frequency', fontsize=14)
		plt.tight_layout()
		plt.gcf().subplots_adjust(top=0.9)
		n_bins = 100
		binvals = np.arange(0.00, 1.00, 0.01)
#		for x in binvals:
#			samp1.append(len([y for y in info[0] if y <= x and y > x-0.01])/float(len(info[0]))+sum(samp1))
#			print len([y for y in info[0] if y <= x and y > x-0.01])/float(len(info[0]))
#			samp2.append(len([y for y in info[1] if y <= x and y > x-0.01])/float(len(info[1]))+sum(samp2))
#		ax.hist(samp1, histtype='step')
#		ax.hist(samp2, histtype='step')
		n, bins, patches = ax.hist(info[0],n_bins, histtype='step', cumulative=True, normed=True, color='blue')
		n1, bins1, patches1 = ax.hist(info[1], bins, histtype='step', cumulative=True, normed=True, color='red')
		plt.xscale('log')
		plt.xticks(fontsize=14)
		plt.yticks(fontsize=14)
		#handles = [Rectangle((0.5,0.5),1,1,color=c,ec="k") for c in ['blue', 'red']]
		#plt.legend(handles, labels)
		#legend1 = mlines.Line2D([], [], color='blue', marker='-', label=labels[0])
		#legend2 = mlines.Line2D([], [], color='red', marker='-', label=labels[1])
		#plt.legend(handles=[legend1, legend2], bbox_to_anchor=(0.93,0.23), borderaxespad=0, fontsize=14)
		line1 = Line2D(range(1),range(1),marker='_', color='blue')
		line2 = Line2D(range(1),range(1),marker='_', color='red')
		plt.legend((line1, line2),(labels[0], labels[1]),bbox_to_anchor=(0.93,0.23), borderaxespad=0, fontsize=14)#, labels=labels))
		if Map == 'FA':
			letter = 'A'
		else:
			letter = 'B'
		ax.annotate(letter, xy=get_axis_limits(ax), fontsize=64, fontname='caladea')
		if comparison == 'gesiemens1000':
			#plt.title('GE 1000 b-Value vs Siemens 1000 b-Value Hellinger'+' '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/Kolmogrov_Smirnov_Plots/Siemens_vs_GE_1000_bval_Hellinger_Kolmogrov_'+Map+'.png')
		elif comparison == '7001000':
			#plt.title('Siemens 1000 b-Value vs Siemens 700 b-Value Hellinger'+' '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/Kolmogrov_Smirnov_Plots/Siemens_700_vs_Siemens_1000_bval_Hellinger_Kolmogrov_'+Map+'.png')
		elif comparison == 'between1.5T':
			#plt.title('GE 1.5T vs Siemens 1.5T Hellinger'+' '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/Kolmogrov_Smirnov_Plots/GE_1.5T_vs_Siemens_1.5T_Hellinger_Kolmogrov_'+Map+'.png')
		elif comparison == 'Siemens3Tvs1.5T':
			#plt.title('Siemens 1.5T vs Siemens 3.0T Hellinger'+' '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/Kolmogrov_Smirnov_Plots/Siemens_1.5T_vs_Siemens_3.0T_Hellinger_Kolmogrov_'+Map+'.png')
		elif comparison == '1.5vs3.0SiemensDirsBval':
			#plt.title('Siemens 1.5T 30 Gradient Directions 1000 b-Value vs\nSiemens 3.0T 30 Gradient Directions 1000 b-Value Hellinger '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/Kolmogrov_Smirnov_Plots/Siemens_1.5T_30_Directions_1000_Bval_vs_Siemens_3.0T_30_Directions_1000_Bval_Hellinger_Kolmogrov_'+Map+'.png')
		elif comparison == 'GESiemensBvalFieldDirControlled':
			#plt.title('GE vs Siemens 1000 b-Value 30 Gradient Directions 1.5T Hellinger '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/Kolmogrov_Smirnov_Plots/GE_vs_Siemens_1000_b-Value_30_Gradient_Directions_1.5T_Hellinger_Kolmogrov_'+Map+'.png')
		elif comparison == 'GE6vs25DirBvalFieldControlled':
			#plt.title('GE 6 Gradient Directions 1000 b-Value 1.5T vs\nGE 25 Gradient Directions 1000 b-Value 1.5T Hellinger '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/Kolmogrov_Smirnov_Plots/GE_6_Gradient_Directions_1000_Bval_1.5T_vs_GE_25_Gradient_Directions_1000_Bval_1.5T_Hellinger_Kolmogrov_'+Map+'.png')
		else:
			#plt.title('All GE vs All Siemens Hellinger'+' '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/Kolmogrov_Smirnov_Plots/All_GE_vs_All_SIEMENS_Hellinger_Kolmogrov_'+Map+'.png')
for x in ['MD','FA']:
	makeKorsakovPlots('GESiemensBvalFieldDirControlled',x)
	makeKorsakovPlots('between1.5T',x)
	makeKorsakovPlots('Siemens3Tvs1.5T',x)
	makeKorsakovPlots('gesiemens1000',x)
	makeKorsakovPlots('between',x)
	makeKorsakovPlots('7001000',x)
	makeKorsakovPlots('1.5vs3.0SiemensDirsBval', x)
	makeKorsakovPlots('GE6vs25DirBvalFieldControlled', x)
