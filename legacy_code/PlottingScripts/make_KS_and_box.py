import os, re, sys, scipy, ast, math, argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from scipy.stats import median_test, mannwhitneyu, ks_2samp
from pprint import pprint

def get_axis_limits(ax):
	print ax.get_xlim()
	print ax.get_ylim()
	print '\n'
	return ax.get_xlim()[0]*1.15, ax.get_ylim()[1]*0.85

def makeKorsakovPlots(comparison):
	data = {'FA':{}, 'MD':{}}
	for Map in ['FA','MD']:
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
		for spreadsheet in files:
			f = open(spreadsheet,'r')
			lines = f.readlines()
			oneline = ' '.join(lines).replace('\n','')
			dataDict = ast.literal_eval(oneline)
			vals = dataDict['hellinger'][1] #zeroth index is x values, we want y values
			vals.sort()
			numpyarray = np.array(vals)
			data[Map][spreadsheet] = numpyarray
	fig, all_axes = plt.subplots(2,2)
	fig.set_size_inches(14, 9)
	boxFA, boxMD, ksFA, ksMD = all_axes[0][0], all_axes[0][1], all_axes[1][0], all_axes[1][1]
	info, labels = {'FA':[], 'MD':[]}, {'FA':[], 'MD':[]}
	for Map in data:
		Keys = data[Map].keys()
		Keys.sort()
		for f in Keys:
			info[Map].append(data[Map][f])
			if comparison == '7001000':
				man = f.split('_')[4]
				labels[Map].append(man+' (n='+str(len(data[Map][f]))+')')
			elif comparison == 'gesiemens1000':
				man = f.split('_')[2]
				labels[Map].append(man+' (n='+str(len(data[Map][f]))+')')
			elif comparison == 'between':
				if 'SIEMENS' in f:
					labels[Map].append('Siemens (n='+str(len(data[Map][f]))+')')
				else:
					labels[Map].append('GE (n='+str(len(data[Map][f]))+')')
			elif comparison == 'between1.5T':
				man = f.split('_')[2]
				labels[Map].append(man+' (n='+str(len(data[Map][f]))+')')
			elif comparison == 'Siemens3Tvs1.5T':
				man = f.split('_')[4]+'T'
				labels[Map].append(man+' (n='+str(len(data[Map][f]))+')')
			elif comparison == '1.5vs3.0SiemensDirsBval':
				man = f.split('_')[7]
				labels[Map].append(man+' (n='+str(len(data[Map][f]))+')')
			elif comparison == 'GESiemensBvalFieldDirControlled':
				man = f.split('_')[2]
				labels[Map].append(man+' (n='+str(len(data[Map][f]))+')')
			elif comparison == 'GE6vs25DirBvalFieldControlled':
				man = f.split('_')[3]+' Directions'
				if '25' in man:
					labels[Map].append(man+'\n(n='+str(len(data[Map][f]))+')')
				else:
					labels[Map].append(man+' (n='+str(len(data[Map][f]))+')')
			else:
				sys.exit('Bad comparison ',comparison)

	for ax in [boxFA, boxMD]:
		if ax == boxFA:
                        Map = 'FA'
                elif ax == boxMD:
                        Map = 'MD'
                else:
                        sys.exit('Bad axis for '+str(ax))
		ax.set_ylabel('Hellinger Distance', fontsize=14)
		m = ax.boxplot(x=info[Map],labels=labels[Map])
		ax.set_xticklabels(ax.get_xticklabels(), fontdict={'fontsize':14})
		ax.set_yticklabels(ax.get_yticklabels(), fontdict={'fontsize':14})
		if Map == 'FA':
			letter = 'A'
		else:
			letter = 'B'
		ax.annotate(letter, xy=(ax.get_xlim()[0], ax.get_ylim()[1]*0.85), fontsize=32)

	for ax in [ksFA, ksMD]:
		if ax == ksFA:
			Map = 'FA'
		elif ax == ksMD:
			Map = 'MD'
		else:
			sys.exit('Bad axis for '+str(ax))
		ax.set_xlabel('Hellinger Distance', {'size':14})
		ax.set_ylabel('Cumulative Frequency', {'size':14})
		ax.set_xscale('log')
		n_bins = 100

		cnt, edges = np.histogram(info[Map][0], bins=n_bins, range=(0.0,1.0), normed=1)
		cnt1, edges1 = np.histogram(info[Map][1], bins=n_bins, range=(0.0,1.0), normed=1)
		ax.step(edges[:-1], cnt.cumsum(), color='blue')
		ax.step(edges1[:-1], cnt1.cumsum(), color='red')
		#binvals = np.arange(0.00, 1.00, 0.01)
		#n, bins, patches = ax.hist(info[Map][0], n_bins, histtype='step', cumulative=True, normed=True, color='blue')
		#n1, bins1, patches1 = ax.hist(info[Map][1], bins, histtype='step', cumulative=True, normed=True, color='red')
		ax.set_xticklabels(ax.get_xticklabels(), fontdict={'fontsize':14})
		ax.set_yticklabels(ax.get_yticklabels(), fontdict={'fontsize':14})
		line1 = Line2D(range(1),range(1),marker='_', color='blue')
		line2 = Line2D(range(1),range(1),marker='_', color='red')
		lgnd = ax.legend((line1, line2),(labels[Map][0], labels[Map][1]),bbox_to_anchor=(0.425,0.75), borderaxespad=0, borderpad=0, fontsize=12) #0.93, 0.23
		if Map == 'FA':
			letter = 'C'
		else:
			letter = 'D'
		ax.annotate(letter, xy=(ax.get_xlim()[0], ax.get_ylim()[1]*0.85), fontsize=32)
		tickLabels = ax.get_xticks()
		ax.set_xticklabels(tickLabels)
	boxFA.set_title('FA', fontsize=32)
	boxMD.set_title('MD', fontsize=32)
	boxMD.twinx().set_ylabel('Box Plot', fontsize=24)
	ksMD.twinx().set_ylabel('Cumulative\nHistogram', fontsize=24)
	plt.tight_layout()
#	plt.show()
#	sys.exit()
	if comparison == 'gesiemens1000':
#		plt.title('GE 1000 b-Value vs Siemens 1000 b-Value Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/combined_Figures/Siemens_vs_GE_1000_bval_Hellinger.png')
	elif comparison == '7001000':
#		plt.title('Siemens 1000 b-Value vs Siemens 700 b-Value Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/combined_Figures/Siemens_700_vs_Siemens_1000_bval_Hellinger.png')
	elif comparison == 'between1.5T':
#		plt.title('GE 1.5T vs Siemens 1.5T Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/combined_Figures/GE_1.5T_vs_Siemens_1.5T_Hellinger.png')
	elif comparison == 'Siemens3Tvs1.5T':
#		plt.title('Siemens 1.5T vs Siemens 3.0T Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/combined_Figures/Siemens_1.5T_vs_Siemens_3.0T_Hellinger.png')
	elif comparison == '1.5vs3.0SiemensDirsBval':
#		plt.title('Siemens 1.5T 30 Gradient Directions 1000 b-Value vs\nSiemens 3.0T 30 Gradient Directions 1000 b-Value Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/combined_Figures/Siemens_1.5T_30_Directions_1000_Bval_vs_Siemens_3.0T_30_Directions_1000_Bval_Hellinger.png')
	elif comparison == 'GESiemensBvalFieldDirControlled':
#		plt.title('GE vs Siemens 1000 b-Value 30 Gradient Directions 1.5T Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/combined_Figures/GE_vs_Siemens_1000_b-Value_30_Gradient_Directions_1.5T_Hellinger.png')
	elif comparison == 'GE6vs25DirBvalFieldControlled':
#		plt.title('GE 6 Gradient Directions 1000 b-Value 1.5T vs\nGE 25 Gradient Directions 1000 b-Value 1.5T Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/combined_Figures/GE_6_Gradient_Directions_1000_Bval_1.5T_vs_GE_25_Gradient_Directions_1000_Bval_1.5T_Hellinger.png')
	else:
#		plt.title('All GE vs All Siemens Hellinger')
		plt.savefig('/space/jazz/1/users/gwarner/combined_Figures/All_GE_vs_All_SIEMENS_Hellinger.png')
makeKorsakovPlots('GESiemensBvalFieldDirControlled')
makeKorsakovPlots('between1.5T')
makeKorsakovPlots('Siemens3Tvs1.5T')
makeKorsakovPlots('gesiemens1000')
makeKorsakovPlots('between')
makeKorsakovPlots('7001000')
makeKorsakovPlots('1.5vs3.0SiemensDirsBval')
makeKorsakovPlots('GE6vs25DirBvalFieldControlled')
