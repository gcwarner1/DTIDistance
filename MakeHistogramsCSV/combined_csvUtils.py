#!/space/jazz/1/users/gwarner/anaconda/bin python

import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import os, sys, shutil, xlrd, re, string, csv, ast, json

def getSub(path):
        return str(os.path.split(path)[0])

    
def getData(f, badDataFiles):
    '''
    Input:
        sheet: excel sheet with one column per distance metric. Each column has the name of the metric as the first value and then all of the distances
        row_subs: list of all unique subject comparisons. i.e) '1.234.5/67.890_345.67/754.0'
    Output:
        Dictionary of dictionaries (one of each distance metric). Each one containing key/val:subjectComparison/distance
        {'chebyshev': {
                        '1.234.5/67.890_345.67/754.0': 0.12345,
                        '1.23432/56432645_432/543.2': 0.6577
                       }
        }
    
    This function automatically removes all NaN and Inf values that might be present.
    '''
    metricIndex = ['cityblock','euclidean','chebyshev','fidelity','hellinger','squaredchord','intersection','canberra','lorentzian','cosine','squaredchisquared','kullbackliebler','jeffreys']
    data = {}
    for x in metricIndex:
	data[x] = {}
    goodinds = set()
    regex = re.compile('(nan)|(NaN)|(Nan)|(NAN)|(inf)|(INF)|(Inf)|(InF)')
    rownum = 0
    goodData = set()#REMOVE
    with open(f, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row1 in spamreader:
                  if rownum != 0:
			row = row1[0].split(',')
                        sub1, sub2 = getSub(row[-1]), getSub(row[-2])
			if sub1 not in badDataFiles and sub2 not in badDataFiles:
				good = True
				for val in row[:-2]:
					if regex.search(str(val)) or str(val) == '' or str(val) == '0' or str(val) == '0.0' or str(val) == '0.':
						good = False
				if good == True:
					goodData.add(sub1)#REMOVE
					goodData.add(sub2)#REMOVE
					for val in row[:-2]:
						ind = row[:-2].index(val)
						data[metricIndex[ind]][sub1+'_'+sub2] = float(val)
	    	  rownum += 1
    return data
    
    

def flattenData(data):
    '''
    Compress the values of each key in data to a 1-d array
    '''
    flattenedData = {}
    for distanceMetric in data: #i.e. chebyshev
        dataForMetric = data[distanceMetric] #dictionary for all chevyshev data with subject name as key and distances for value
        yvals = dataForMetric.values()
        xvals = [0]*len(yvals) #because it's a scatter plot all of the x values must be zero so they datapoints all line up
        flattenedData[distanceMetric] = [xvals, yvals]
    return flattenedData
    
    
def makePlots(Data, numBins, Manufacturer):
    '''
    Input:
        flattenedData: Dictionary with keys of distance metric and values of [[xval1, xval2...],[yval1, yval2...]]
        numBins: the number of bins you want the histogram to have
        histname: the file name of the histogram chart you want to generate
    Output:
        histogramData: {'chebyshev': [
                                        [list of lists, one list per bin, containing datapoints in that bin],
                                        [edges of each bin],
                                        [patches *irrelevant for our purposes*]
                                      ],
                        'euclidian':[]....
                        }
    '''
    histogramData = {}
    FAxvals, FAyvals = Data['FA']['hellinger']
    MDxvals, MDyvals = Data['MD']['hellinger']
    fig = plt.figure(figsize=(9,5))
    plt.rcParams['font.family'] = 'Times New Roman'
    ax1 = fig.add_subplot(121)#, figsize=[10,5])#adjustable='box')#, aspect=1)
    ax2 = fig.add_subplot(122)#, adjustable='box')#, aspect=1)
    fig.subplots_adjust(wspace=0.65, left=0.1)
    #fig.
    ax1.set_ylabel('Frequency',fontsize=12)
    ax2.set_ylabel('Frequency',fontsize=12)
    ax1.set_xlabel('Distance',fontsize=12)
    ax2.set_xlabel('Distance',fontsize=12)
    ax1.set_title('FA', fontsize=14)# (n='+str(len(FAxvals))+')',fontsize=14)
    ax2.set_title('MD', fontsize=14)# (n='+str(len(MDxvals))+')',fontsize=14)
    for ax in [ax1, ax2]:
	for tick in ax.get_xticklabels():
		tick.set_fontsize(12)
	for tick in ax.get_yticklabels():
		tick.set_fontsize(12)
	#ax.set_aspect(aspect=0.1)
    ax1.hist(FAyvals, bins=numBins, normed=True, color='black')#weights=weights)
    ax2.hist(MDyvals, bins=numBins, normed=True, color='black')
    ax1.set_xlim(0.0,1.0)
    ax2.set_xlim(0.0,1.25)
    if Manufacturer == 'Siemens':
	name = 'Fig2.png'
    else:
	name = 'Fig3.png'
    plt.savefig('/space/jazz/1/users/gwarner/dtiCharts/Combined_'+name, figsize=(100,10))
    plt.close()    


def genHistograms(spread, Manufacturer):
	badDataFiles = ['/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.132.183.36.32.20091012.133556.24055406/1.3.12.2.1107.5.2.32.35288.2009101314133832325064299.0.0.0',
                '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.30763.51983.17064.20110907.162533.165704172/1.2.826.0.1.3680043.6.7364.20900.20110908084120.456.6729',
                '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.132.183.36.32.20100317.144222.25023920/1.2.840.113619.2.244.3596.11879852.21671.1268700198.13',
                '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.30763.51983.17064.20111101.145144.71699314/1.2.826.0.1.3680043.6.11942.1167.20111101173407.164.698',
                '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.132.183.36.32.20050622.185826.13762610/1.2.840.113619.2.135.2025.3762954.5993.1119438994.60',
                '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.30763.51983.17064.20120419.113839.38982559/1.2.826.0.1.3680043.6.29155.12163.20120420182437.848.716',
                '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.30763.51983.17064.20120225.232517.49687933/1.2.826.0.1.3680043.6.19290.25070.20120226071631.572.905',
		'/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.132.183.36.32.20100211.74050.24806509/1.3.12.2.1107.5.2.32.35006.2010021108571037518092333.0.0.0',
		'/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.132.183.36.32.20090902.112807.23801734/1.2.124.113532.132.183.24.94.20090904.132910.22367']

	Data = {'FA':False, 'MD':False}
	for f in spread:
		data = getData(f, badDataFiles)
		flattenedData = flattenData(data)
		numBins = 100
		if 'FA' in f:
			Data['FA'] = flattenedData
		else:
			Data['MD'] = flattenedData
	makePlots(Data, numBins, Manufacturer)
	print 'Done'
