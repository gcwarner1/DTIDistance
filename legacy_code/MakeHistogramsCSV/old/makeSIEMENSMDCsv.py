#!/space/jazz/1/users/gwarner/anaconda/bin python

import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import os, sys, shutil, xlrd, re, string, csv, ast, json
print 'Running...'

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
    good1, bad1 = [],[]
    with open(f, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row1 in spamreader:
                  if rownum != 0:
			row = row1[0].split(',')
                        sub1, sub2 = getSub(row[-1]), getSub(row[-2])
			if sub1 not in badDataFiles and sub2 not in badDataFiles:
				good = True
				good1.append(row)
				for val in row[:-2]:
					if regex.search(str(val)) or str(val) == '' or str(val) == '0' or str(val) == '0.0' or str(val) == '0.':
						good = False
				if good == True:
					for val in row[:-2]:
						ind = row[:-2].index(val)
						data[metricIndex[ind]][sub1+'_'+sub2] = val
			else:
				bad1.append(row)
	    	  rownum += 1
    for x in good1:
	print 'Good: ',x
    for x in bad1:
	print 'Bad: ',x
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
    
    
def makePlots(flattenedData, numBins, comparison, scattername, histname, Map):
    '''
    Input:
        flattenedData: Dictionary with keys of distance metric and values of [[xval1, xval2...],[yval1, yval2...]]
        numBins: the number of bins you want the histogram to have
        scattername: the file name of the scatter chart you want to generate
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
    if Map == 'FA':
	XMAX = {'canberra':45, 'chebyshev':0.045, 'cityblock':0.65, 'euclidean':0.12, 'hellinger':0.6, 'jeffreys':0.75, 'kullbackliebler':0.45, 'lorentzian':0.65, 'squaredchisquared':0.3, 'squaredchord':0.18}
	XMIN = {'cosine':0.75, 'fidelity':0.91, 'intersection':0.65}
    else:
	XMAX = {'canberra':100, 'chebyshev':0.14, 'cityblock':1.4, 'euclidean':0.3, 'hellinger':1.25, 'jeffreys':2.0, 'kullbackliebler':1.0, 'lorentzian':1.3, 'squaredchisquared':0.8, 'squaredchord':0.6}
        XMIN = {'cosine':0.4, 'fidelity':0.7, 'intersection':0.45}
    if os.path.exists('/space/jazz/1/users/gwarner/dtiCharts/'+Map+'/'+comparison) == False:
        os.mkdir('/space/jazz/1/users/gwarner/dtiCharts/'+Map+'/'+comparison)
    for distanceMetric in flattenedData:
        #scatter
        xvals, yvals = flattenedData[distanceMetric]
        fig = plt.figure()
        ax = fig.add_subplot(111)
	directions = re.search('hist(\d*)',histname).group(1)
        ax.set_ylabel('Frequency')
	ax.set_xlabel('Distance')

	titleComparison = comparison
	if '_' in comparison:
		titleComparison = titleComparison.replace('_',' ')
	if 'SIEMENS' in comparison:
		titleComparison = titleComparison.replace('SIEMENS','Siemens')
	if 'Bval' in comparison:
		titleComparison = titleComparison.replace('Bval', 'B-Value')
	plt.title(titleComparison+' '+directions+' '+distanceMetric.title()+' (n='+str(len(xvals))+')')
	histogramData[distanceMetric] = plt.hist(yvals, bins=numBins, normed=True)#weights=weights)
	if distanceMetric in XMAX:
		plt.xlim(0,XMAX[distanceMetric])
	elif distanceMetric in XMIN:
		plt.xlim(XMIN[distanceMetric],1)
	else:
		sys.exit('Couldnt find '+distanceMetric)
        plt.savefig('/space/jazz/1/users/gwarner/dtiCharts/'+Map+'/'+comparison+'/'+distanceMetric+'_'+histname+'_'+comparison+'.png')
        plt.close()    
    return histogramData
    
    
def groupDataSetsInBins(histogramData, data, numBins):
    '''
    Get the edges of the histogram bins from the plt.hist output and then use those to determine which bin each data comparison is in.
    Input:
        histogramData: {'chebyshev': [
                                        [list of lists, one list per bin, containing datapoints in that bin],
                                        [edges of each bin],
                                        [patches *irrelevant for our purposes*]
                                      ],
                        'euclidian':[]....
                        }
        numBins: number of bins in histogram
    Output:
        dictionary with keys of each data distance metric (i.e. chebyshev) and values of list of lists (one sublist per bin) containing the filenames in that bin
        i.e): {'chebyshev': [[file in bin 1, another file in bin 1], [file in bin 2, another file in bin 2]...]}
        ]}
    '''
    binContents = {}
    for distanceMetric in histogramData:
        binSteps = list(histogramData[distanceMetric][1])
        bins = [[] for x in range(numBins)]
        for subRun in data[distanceMetric]:
            value = data[distanceMetric][subRun]#[0] #yval, actual distance
            for binMin in binSteps[:-1]:#confirm final bin is populated to confirm this indexing
                binMinIndex = binSteps.index(binMin)
                binMax = binSteps[binMinIndex+1]
                if binMinIndex+1 == len(binSteps):#bin includes lower value but excludes upper value EXCEPT in the final bin, in which upper and lower are included
                    if value >= binMax and value <= binMax:
                        bins[binMinIndex].append(subRun) #is this the correct indexing?
                else:
                    if value >= binMin and value < binMax:
                        bins[binMinIndex].append(subRun) #is this the correct indexing?
        binContents[distanceMetric] = bins
    return binContents


def genHistograms(f, Manufacturer, Map):
	if Map == 'FA':
		mapIndex = 0
	elif Map == 'MD':
		mapIndex = 1

	badDataFiles = ['/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.132.183.36.32.20091012.133556.24055406/1.3.12.2.1107.5.2.32.35288.2009101314133832325064299.0.0.0',
                '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.30763.51983.17064.20110907.162533.165704172/1.2.826.0.1.3680043.6.7364.20900.20110908084120.456.6729',
                '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.132.183.36.32.20100317.144222.25023920/1.2.840.113619.2.244.3596.11879852.21671.1268700198.13',
                '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.30763.51983.17064.20111101.145144.71699314/1.2.826.0.1.3680043.6.11942.1167.20111101173407.164.698',
                '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.132.183.36.32.20050622.185826.13762610/1.2.840.113619.2.135.2025.3762954.5993.1119438994.60',
                '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.30763.51983.17064.20120419.113839.38982559/1.2.826.0.1.3680043.6.29155.12163.20120420182437.848.716',
                '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.30763.51983.17064.20120225.232517.49687933/1.2.826.0.1.3680043.6.19290.25070.20120226071631.572.905',
		'/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.132.183.36.32.20100211.74050.24806509/1.3.12.2.1107.5.2.32.35006.2010021108571037518092333.0.0.0',
		'/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.132.183.36.32.20090902.112807.23801734/1.2.124.113532.132.183.24.94.20090904.132910.22367']

	data = getData(f, badDataFiles)
	for x in data['canberra']:
		print x
	sys.exit()
	flattenedData = flattenData(data)
	numBins = 100
	num = f.split('.')[-2].split('_')[-1]
	try:
		int(num)
	except ValueError:
		num = ''
	if Manufacturer == 'GE':
		histogramData = makePlots(flattenedData, numBins, Manufacturer+'_'+Map, 'scatter', 'hist', Map)
	histogramData = makePlots(flattenedData, numBins, Manufacturer+'_'+Map+'_Bval', 'scatter'+num, 'hist'+num, Map)
	finalBinContents = groupDataSetsInBins(histogramData, data, numBins)
	return histogramData, finalBinContents, flattenedData


Map = 'MD'
histData, finalBinCont, dataPoints = genHistograms('/space/jazz/1/users/gwarner/histograms/histdist_results_SIEMENS.xlsx', Manufacturer='SIEMENS', Map=Map)
histDataFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/siemens_histogram_data.txt', "w")
histDataFile.write(str(histData))
histDataFile.close()
finalBinContFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/siemens_bin_contents.txt', "w")
finalBinContFile.write(str(finalBinCont))
finalBinContFile.close()
dataPointFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/siemens_data_points.txt','w')
dataPointFile.write(str(dataPoints))
dataPointFile.close()
def make(man, Map):
	if Map != 'FA' and Map != 'MD':
		sys.exit(Map+' is invalid Map value')
	if man == 'SIEMENS':
		spread = ['histdist_results_SIEMENS_manufacturers_1000_%s.xlsx'%Map, 'histdist_results_SIEMENS_manufacturers_700_%s.xlsx'%Map]
	elif man == 'GE':
		spread = ['histdist_results_GE_manufacturers_1000_%s.csv'%Map]
	else:
		sys.exit('Invalid manufacturer')
	for x in spread:
		histData, finalBinCont, dataPoints = genHistograms('/space/jazz/1/users/gwarner/histograms/'+x, Manufacturer=man, Map=Map)
		histDataFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/'+x.split('.')[0]+'_histogram_data.txt', "w")
		histDataFile.write(str(histData))
		histDataFile.close()
		finalBinContFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/'+x.split('.')[0]+'_bin_contents.txt', "w")
		finalBinContFile.write(str(finalBinCont))
		finalBinContFile.close()
		dataPointFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/'+x.split('.')[0]+'_data_points.txt','w')
		dataPointFile.write(str(dataPoints))
		dataPointFile.close()
		if man == 'GE':
			histDataFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/GE_histogram_data.txt', "w")
			histDataFile.write(str(histData))
			histDataFile.close()
			finalBinContFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/GE_bin_contents.txt', "w")
			finalBinContFile.write(str(finalBinCont))
			finalBinContFile.close()
			dataPointFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/GE_data_points.txt','w')
			dataPointFile.write(str(dataPoints))
			dataPointFile.close()
#make('GE', Map)
make('SIEMENS', Map)
