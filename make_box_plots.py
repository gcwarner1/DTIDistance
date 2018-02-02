import os, re, sys, scipy, ast, math, argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import median_test, mannwhitneyu, ks_2samp
from pprint import pprint
import matplotlib

def makeBoxPlots(comparison, Map):
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
	metrics = ["canberra","cityblock", "euclidean", "canberra", "chebyshev", "hellinger"]
	data = {}
	for x in metrics:
		data[x] = {}
	for spreadsheet in files:
	        f = open(spreadsheet,'r')
	        lines = f.readlines()
	        oneline = ' '.join(lines).replace('\n','')
		dataDict = ast.literal_eval(oneline)
	        for x in metrics:
			vals = dataDict[x][1] #zeroth index is x values, we want y values
			vals.sort()
			numpyarray = np.array(vals)
			data[x][spreadsheet] = numpyarray
	for metric in ['hellinger']:#data:
		#fig = plt.figure()
		#ax = fig.add_subplot(111)
		#ax.set_ylabel('Distance', fontsize=14)
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
		print '\n\n'+Map
		print comparison+' '+metric
		print info[0]
		print len(info[0]), len(info[1])
		#print 'Moods Median: '+str(median_test(info[0], info[1]))
		#print 'Medians (left, right)'
		median1, median2 = np.median(info[0]), np.median(info[1])
		print str(labels[0])+': '+str(median1)
		print str(labels[1])+': '+str(median2)
		#print 'Moods p-value'
		#pprint ([(i, median_test(info[0],info[1][:i])[1]) 
			#for i in range(200,len(info[1]),200)])
		#print median_test(info[0],info[1])
		print 'Mann-Whitney U: '+str(mannwhitneyu(info[0], info[1]))
		pprint ([(i, mannwhitneyu(info[0],info[1][:i])[1])
			for i in range(200,len(info[1]),200)])
		
		m = plt.boxplot(x=info,labels=labels)
		whiskers = [item.get_ydata() for item in m['whiskers']]
		print 'Whiskers for '+str(labels[0])
		med0 = np.median(info[0])
		med1 = np.median(info[1])
		print whiskers[:2]
		print 'Whiskers for '+str(labels[1])
		print whiskers[-2:]
		print 'Max minus median for '+str(labels[0])+': '+str(float(whiskers[1][1])-float(median1))
		print 'Max minus median for '+str(labels[1])+': '+str(float(whiskers[3][1])-float(median2))
		sys.exit()
		plt.xticks(fontsize=14)
        	plt.yticks(fontsize=14)
		if comparison == 'gesiemens1000':
			plt.title('GE 1000 B-value vs Siemens 1000 B-value '+metric.title()+' '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/boxplots/'+Map+'/Siemens_vs_GE_1000_bval_'+metric+'_'+Map+'_boxplot.png')
		elif comparison == '7001000':
			plt.title('Siemens 1000 B-value vs Siemens 700 B-value '+metric.title()+' '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/boxplots/'+Map+'/Siemens_700_vs_Siemens_1000_bval_'+metric+'_'+Map+'_boxplot.png')
		elif comparison == 'between1.5T':
			plt.title('GE 1.5T vs Siemens 1.5T '+metric.title()+' '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/boxplots/'+Map+'/GE_1.5T_vs_Siemens_1.5T_'+metric+'_'+Map+'_boxplot.png')
		elif comparison == 'Siemens3Tvs1.5T':
			plt.title('Siemens 1.5T vs Siemens 3.0T '+metric.title()+' '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/boxplots/'+Map+'/Siemens_1.5T_vs_Siemens_3.0T_'+metric+'_'+Map+'_boxplot.png')
#		elif comparison == '1.5vs3.0SiemensDirsBval':
#			plt.title('Siemens 1.5T 30 Gradient Directions 1000 B-Value vs\nSiemens 3.0T 30 Gradient Directions 1000 B-Value '+metric.title()+' '+Map)
                        plt.savefig('/space/jazz/1/users/gwarner/boxplots/'+Map+'/Siemens_1.5T_30_Directions_1000_Bval_vs_Siemens_3.0T_30_Directions_1000_Bval_'+metric+'_'+Map+'_boxplot.png')
		elif comparison == 'GESiemensBvalFieldDirControlled':
			plt.title('GE vs Siemens 1000 B-Value 30 Gradient Directions 1.5T '+metric.title()+' '+Map)
                        plt.savefig('/space/jazz/1/users/gwarner/boxplots/'+Map+'/GE_vs_Siemens_1000_B-Value_30_Gradient_Directions_1.5T_'+metric+'_'+Map+'boxplot.png')
		elif comparison == 'GE6vs25DirBvalFieldControlled':
			plt.title('GE 6 Gradient Directions 1000 b-Value 1.5T vs\nGE 25 Gradient Directions 1000 b-Value 1.5T '+metric.title()+' '+Map)
			plt.savefig('/space/jazz/1/users/gwarner/boxplots/'+Map+'/GE_6_Gradient_Directions_1000_Bval_1.5T_vs_GE_25_Gradient_Directions_1000_Bval_1.5T_'+metric+'_'+Map+'_boxplot.png')
		else:
			plt.title('All GE vs All Siemens '+metric.title()+' '+Map)
#			plt.savefig('/space/jazz/1/users/gwarner/boxplots/'+Map+'/All_GE_vs_All_SIEMENS_'+metric+'_'+Map)

for x in ['FA']:#,'MD']:
	makeBoxPlots('GESiemensBvalFieldDirControlled',x)
#	makeBoxPlots('between1.5T',x)
#	makeBoxPlots('Siemens3Tvs1.5T',x)
#	makeBoxPlots('gesiemens1000',x)
#	makeBoxPlots('between',x)
#	makeBoxPlots('7001000',x)
#	makeBoxPlots('1.5vs3.0SiemensDirsBval', x)
#	makeBoxPlots('GE6vs25DirBvalFieldControlled', x)
