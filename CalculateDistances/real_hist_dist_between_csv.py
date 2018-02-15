'''
 This program calculates the distance, using a set of different measures, between two histograms.
 The application is to compare whole-brain FA and MD histograms to decide if two scans are
 different from each other.
 Histograms compared here have are specified by the number of bins, the start value and the
 increment for every bin.

 modified 10/3/12
  added calculation of new metrics
  changed bin definitions to reflect new bin widths and the new number of elements

 modified 11/8/12
  added in parameters for MD calculation

 modified 07/27/16
  begun converting to python from IDL
  now create histograms here instead of reading them in from a file
  add reading in of NIfTI files
  create histogram text files for possible later use
  added code to accommodate data directory schema

 modified 08/05/16
  changed method of defining histogram bins
  plotting of histograms now works and is scaled correctly in plot; 
  set first histogram bin freq = 0 to remove background pixels
  refactored code to check for diffusion file type first and then to see if it can be opened by Nibabel
  normalize the histogram frequency by the number of non-zero elements (use sum of histogram array)

 modified 08/08/16
  refactored code into functions

 modified 08/10/16
  added storing all histograms to separate arrays, store/retrieve hist data from file using numpy

 modified 08/12/16
  added distance metric calculation for partial list of metrics

 modified 08/16/16
  added main(), iterative calling of metric functions from list as function, writing out of results to excel spreadsheet

 modified 09/02/16
  added 2nd half of metrics; fixed bug in Excel file creation = column headings weren't printing correctly

 modified 09/08/16
  fixed bug in the extraction of histograms from the main storage matrix.
  now rename default Excel sheet to FA and create MD sheet instead of creating sheets for both FA and MD
'''
import os, dicom, ast, argparse, shutil, re, glob, sys, csv
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from math import factorial

#********************************************************************************
fileTypeList = ['_FA', '_MD']     #string in filename used to ID map type
stepList = [0.01,0.00004]		  #bin step in the map type histogram
binRange = [[0.0, 1.0], [0.0, 0.004]]     #min and max for FA (first) and MD (second)
numBins = [(int(binRange[0][1]/stepList[0]) - 1), int((binRange[1][1]/stepList[1]) - 1)]
print "the number of bins is = ", numBins
#listOfRuns = '/space/jazz/1/users/gwarner/FAandMDmaps' #'/home/karl/Work/QTIM/TIV'
#outFile = '/space/jazz/1/users/gwarner/histdist_results.xlsx'#'/home/karl/Work/QTIM/TIV_histdist_results.xlsx'
sheetNameFA = 'FA_Results'
sheetNameMD = 'MD_Results'
# The list containing the names of the distance metrics to be calculated has to be defined in main()
#********************************************************************************

def handle_inputs():
    '''
    This function deals with the variables set by command line flags. At least one of the manufacturer flags (GE, SIEMENS)
    must be set and up to one additional flag may be set. The command line arguments are then put into a python dictionary
    containing one or two keys. The mandatory key is 'manufacturers' and it's value is a list of the manufacturers which
    were set to True. This list can look like any of the following: [GE], [SIEMENS], [GE, SIEMENS]). If an additional variable
    was set (bval, model, bvec) it will be the second key and it's value will be True.

    output: {'manufacturers':['GE','SIEMENS'], 'bval': True}
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', nargs='?', type=bool, default=False, help='Scanner Model')
    parser.add_argument('--siemens', nargs='?', type=bool, default=False, help='SIEMENS')
    parser.add_argument('--ge', nargs='?', type=bool, default=False, help='GE')
    parser.add_argument('--bval', nargs='?', type=bool, default=False, help='Bvals')
    parser.add_argument('--bvec', nargs='?', type=bool, default=False, help='Bvecs')
    parser.add_argument('--field', nargs='?', type=bool, default=False, help='Field Strength')
    args = parser.parse_args()
    if args.siemens == False and args.ge == False:
	sys.exit('Specify at least one manufacturer')
    manufacturers = []
    if args.siemens != False:
	manufacturers.append('SIEMENS')
    if args.ge != False:
	manufacturers.append('GE')
    inputs = vars(args)
    del inputs['ge']
    del inputs['siemens']
    if sum(inputs.values()) > 1:
	sys.exit('Too many arguments set')
    output = {'manufacturers': manufacturers}
    for x in inputs.keys():
	if inputs[x] == True:
	    output[x] = True
    return output


def disp_image(data, dataShape):
    # display volume central slice; assumes 3D volume
    plt.imshow(data[:,:,dataShape[2]/2], interpolation='nearest')
    plt.show()


def plot_hist(mapHistogram, mapBinEdges, fileNamePath):
    # plot the histogram
    plt.bar(mapBinEdges[:-1], mapHistogram, width=mapBinEdges[1]-mapBinEdges[0], color='red', alpha=0.5)
    plt.grid(True)
    plt.title(fileNamePath)
    # check using matplotlib's histogram plotting function
    #nbins = mapBinEdges.size
    #plt.hist(mapHistogram, bins=nbins, alpha=0.5)
    plt.show()


def save_hist(mapHistogram, fileNamePath):
    # save the histogram to a file
    #histFileName = fileNamePath.split('.')[0]
    histFileName = os.path.splitext(os.path.splitext(fileNamePath)[0])[0] #this is doubled up because the extention is fileNamePath.nii.gz
    np.savetxt(histFileName+'.hist', mapHistogram, fmt='%.10f', delimiter='\n')


# assume FA and MD files for a given subject and run are in same directory
def create_hist(listOfRuns, fileTypeList):
    # create normalized histograms for each NIfTI file found
	for run in listOfRuns:
	    if len(glob.glob(run+'/*hist')) == 0:
        # ascertain if the file is NIfTI
	            for fileName in os.listdir(run):   #this will only happen if there are files in a dir
			fileNamePath = os.path.join(run, fileName)
	                for i in range(len(fileTypeList)):
	                    if fileTypeList[i] in fileNamePath:
	                        try:
	                            mapData = nib.load(fileNamePath)
	                        except:
	                            #print fileNamePath, " is either not NIfTI or is unreadable."
	                            continue    #move on to next dataset
	                        else:
	                            #print "...getting info from: ", fileNamePath
	                            dataOrig = mapData.get_data()
	                            data = np.asfarray(dataOrig)  #convert from float32 to float64
	                            hdr = mapData.get_header()
	                            #print "data matrix size is: ", hdr.get_data_shape()
	                            #print "original data type is: ", hdr.get_data_dtype()
	                            #print "data is cast into: ", data.dtype

	                            # display the diffusion metric maps
	                            #disp_image(data, dataShape)

	                            # set up bins, calculate histogram
	                            xmin=binRange[i][0]
	                            xmax=binRange[i][1]
	                            step=stepList[i]
	                            mapHistogram, mapBinEdges = np.histogram(data, bins=np.linspace(xmin, xmax, (xmax-xmin)/step))
	                            # all of the background voxels are zero. Set their frequency to zero so plot scales better
	                            mapHistogram[0] = 0.0

	                            # calculate the number of non-zero elements from the sum of the histogram array
	                            # The question here is what to use for the normalization factor? 
	                            # Since I'm zeroing the first bin I should use the sum of the histogram.  On the other hand if 
	                            # you normalize using the number of non-zero voxels then you are using the same normalization 
	                            # factor for both FA and MD.  I think since I'm using the "no zeros" histogram in the distance
	                            # calc I should get the normalization factor from there instead of from a histogram with the 
	                            # zeros that I'm not using in the calculation.
	                            #normFactor = np.count_nonzero(data)
	                            #print "the number of non-zero pixels is (matrix):", np.count_nonzero(data)
	                            normFactor = float(np.sum(mapHistogram))
	                            #print "the dtype of normFactor is: ", normFactor.dtype
	                            #print "the number of non-zero pixels is (histogram): ", normFactor

	                            # normalize the histogram
	                            #since normFactor is float64 mapHistogram gets cast into that before the math as well so this is ok.
	                            mapHistogramNorm = mapHistogram/normFactor 
	                            #print "The histogram dtype is: ", mapHistogramNorm.dtype

	                            # plot the normalized histogram
	                            plot_hist(mapHistogramNorm, mapBinEdges, fileNamePath)
				    sys.exit()
	                            # save the normalized histogram to a file
	                            #print "Writing histograms to files..."
	                            save_hist(mapHistogramNorm, fileNamePath)


def count_hist_files(listOfRuns, fileTypeList):
        fileCountList = [0,0]
        for run in listOfRuns:
            # first find out how many histograms there are for each diffusion metric type (FA/MD)
            for fileName in os.listdir(run):
                fileNamePath = os.path.join(run, fileName)
		histExt = os.path.split(fileNamePath)[1].split('.')[1]
                for i in range(len(fileTypeList)):
                    if (fileTypeList[i] in fileNamePath and histExt == "hist"):                
                        fileCountList[i] += 1
        #print "The filecount for [FA,MD] is = ", fileCountList

        return fileCountList


def create_hist_arrays(listOfRuns, fileTypeList):
    '''
    Generate numpy arrays for FA and MD histograms associated with a single, specific set of parameters. Each array has one column per 
    relevant histogram and that column is populated with the values of that histogram. 

    inputs:
	listofRuns: list of runs associated with a single set of parameters such as GE runs with 6 gradient directions.
	fileTypeList: ['_FA', '_MD']
    outputs:
f we used RFA, RFA N	faArray: numpy array of FA histograms with one column per histogram and the values of that column being the values of that histogram
	faList: list of all FA histogram filepaths including file name
	mdArray: numpy array of MD histograms with one column per histogram and the values of that column being the values of that histogram
	mdList: list of all MD histogram filepaths including file name
	fileCountList: list with first element being number of FA histograms and second element being numbe of MD histograms
    '''
    # faArray and mdArray hold all of the histograms of that type
    # faList and mdList hold the list of filepaths for data files of each type

    fileCountList = count_hist_files(listOfRuns, fileTypeList)

    # construct the arrays and lists to hold the hist data and filenames
    faArray = np.zeros((numBins[0], fileCountList[0]), dtype=np.float)
    mdArray = np.zeros((numBins[1], fileCountList[1]), dtype=np.float)
    faList = []
    mdList = []

    # get each .hist file and put the contents in the appropriate array and the filename in the appropriate list
    faCounter = 0
    mdCounter = 0
    for run in listOfRuns:
            for fileName in os.listdir(run):   #this will only happen if there are files in a dir
                fileNamePath = os.path.join(run, fileName)
		histExt = os.path.split(fileNamePath)[1].split('.')[1]
                if (histExt == "hist"):
                    tempHist = np.loadtxt(fileNamePath, dtype=np.float, delimiter = '\n')
                    if fileTypeList[0] in fileNamePath:
                        faArray[:,faCounter] = tempHist #populate faCounterth column of faArray with values from tempHist
                        faCounter += 1
                        faList.append(fileNamePath)
                    elif fileTypeList[1] in fileNamePath:
                        mdArray[:,mdCounter] = tempHist
                        mdCounter += 1
                        mdList.append(fileNamePath)
                    else:
                        print "There are unknown files with the .hist extension in this dir path. Exiting..."
                        sys.exit()

    return faArray, faList, mdArray, mdList, fileCountList


# Distance Metric Definitions *******************************************
# City-block norm - verified
def cityblock(array1, array2):
    dist = np.sum(np.abs(np.subtract(array1, array2)))
    return dist

# Euclidean (L2) norm - verified
def euclidean(array1, array2):
    dist = np.sqrt(np.sum(np.square(np.subtract(array1, array2))))
    return dist


# Chebyshev (L-infinity) norm - verified
def chebyshev(array1, array2):
    dist = np.max(np.abs(np.subtract(array1, array2)))
    return dist


# Fidelity metric - verified
def fidelity(array1, array2):
    mult = array1 * array2
    dist = np.sum(np.sqrt(mult))
    return dist


# Hellinger metric; w/o the 2 it is the Comaniciu version of Bhattacharyya that makes it a metric
# Also note that the Matusita distance can be shown to equal 2*(Comaniciu)^2. - verified
def hellinger(array1, array2):
    mult = array1 * array2
    fidelity = np.sum(np.sqrt(mult))
    dist = 2.0 * np.sqrt(1.0 - fidelity)

    return dist


# Squared-chord distance; also the Matusita distance - verified
def squaredchord(array1, array2):
    sp1 = np.sqrt(array1)
    sp2 = np.sqrt(array2)
    dist = np.sum(np.square(np.subtract(sp1, sp2)))
    return dist


# Intersection - verified
def intersection(array1, array2):
    minArray = np.minimum(array1, array2)
    dist = np.sum(minArray)
    return dist


# Non-Intersection - verified
def non_intersection(array1, array2):
    minArray = np.minimum(array1, array2)
    dist = 1.0 - np.sum(minArray)
    return dist


# Canberra
def canberra(array1, array2):
    cba = np.zeros_like(array1)
    addProb = np.add(array1, array2)
    absDiffProb = np.abs(np.subtract(array1, array2))
    for j in range(len(array1)):
        if addProb[j] == 0.0:
            cba[j] = 0.0
        else:
            cba[j] = absDiffProb[j] / addProb[j]
    dist = np.sum(cba)
    return dist


# Lorentzian
def lorentzian(array1, array2):
    absDiffProb = np.abs(np.subtract(array1, array2))
    dist = np.sum(np.log(1.0 + absDiffProb))
    return dist


# Cosine
def cosine(array1, array2):
    mult = np.multiply(array1, array2)
    dist = np.sum(mult) / ( np.sqrt(np.sum(np.square(array1))) * np.sqrt(np.sum(np.square(array2))) )
    return dist


# Squared Chi-squared 
def squaredchisquared(array1, array2):
    scs = np.zeros_like(array1)
    addProb = np.add(array1, array2)
    squareDiffProb = np.square(np.subtract(array1, array2))

    for j in range(len(array1)):
        if addProb[j] == 0.0:
            scs[j] = 0.0
        else:
            scs[j] = squareDiffProb[j] / addProb[j]
    dist = np.sum(scs)
    return dist


# Kullback-Leibler, D4.  
# Not a true distance, but rather a relative entropy. Here I am using the log base e for "log" as that is 
# appropriate for "nats" the unit of information.   N.B - I am dealing with the bins in which either 
# probablility is zero by making the metric = 0 for that bin.  That way I don't get divide by zero errors.
# Notice that K-L is asymmetric.
def kullbackliebler(array1, array2):
    dkl = np.zeros_like(array1)
    for j in range(len(array1)):
        if np.logical_and(array1[j] != 0.0, array2[j] != 0.0):
            dkl[j] = array2[j] * np.log(array2[j] / array1[j])
        else:
            dkl[j] = 0.0
    dist = np.sum(dkl)
    return dist


# jeffreys divergence.  
# Again, not a true distance, but a symmetric version of K-L. Here I am using the log base e for "log"
# as that is appropriate for "nats" the unit of information.  N.B - I deal with the bins in which either 
# probablility is zero by making the metric zero for that bin.  That way I don't get divide by zero errors. 
# Note that this is the symmetric version of K-L.
def jeffreys(array1, array2):
    jd = np.zeros_like(array1)
    for j in range(len(array1)):
        if np.logical_and(array1[j] != 0.0, array2[j] != 0.0):
            jd[j] = (array1[j] - array2[j]) * np.log(array2[j] / array1[j])
        else:
            jd[j] = 0.0
    # I take abs here to get a positive distance at the end
    dist = np.abs(np.sum(jd))
    return dist


# end distance metric section

# writes out results to an excel spreadsheet using openpyxl
# easier to pass both rather than write a generic function because otherwise I have to check to see 
# if outFile already exists and then add to it, but that file might be an old version etc
def write_to_csv(outFile, distListFA, distListMD, lenMetricList, numPairs, metricListString):
    print "...writing the output file"
    #wb = Workbook()
    with open(outFile+'_FA.csv', 'wb') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(metricListString+['file_1','file_2'])
	for x in distListFA:
		writer.writerow(x)
    csvfile.close()
    with open(outFile+'_MD.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(metricListString+['file_1','file_2'])
	for x in distListMD:
		writer.writerow(x)
    csvfile.close()


# calls the relevant distance metric functions and calculates the distances between all found histograms
#def calc_hist_dist(fileCount, diffMetricArray, diffMetricFileList, metricList):
def calc_hist_dist(arrayData, metricList):
    distListFA, distListMD = [], []
    mans = arrayData.keys()
    for i in range(arrayData[mans[0]]['fileCountList'][0]):
	for j in range(arrayData[mans[1]]['fileCountList'][0]):
		print arrayData[mans[1]]['faArray']
		dist = [f(arrayData[mans[0]]['faArray'][:,i], arrayData[mans[1]]['faArray'][:,j]) for f in metricList]
		dist.append(arrayData[mans[0]]['faFileList'][i])
		dist.append(arrayData[mans[1]]['faFileList'][j])
		distListFA.append(dist)
    for i in range(arrayData[mans[0]]['fileCountList'][1]):
        for j in range(arrayData[mans[1]]['fileCountList'][1]):
                dist = [f(arrayData[mans[0]]['mdArray'][:,i], arrayData[mans[1]]['mdArray'][:,j]) for f in metricList]
                dist.append(arrayData[mans[0]]['mdFileList'][i])
                dist.append(arrayData[mans[1]]['mdFileList'][j])
                distListMD.append(dist)
    return distListFA, distListMD


def calc_hist_dist_single(fileCount, diffMetricArray, diffMetricFileList, metricList):
    '''
    Calculates the distance between each histogram in a set of histograms and all other histograms in that set WITHOUT repitions (if you already calculated 1v2 you don't calculate 2v1).
    The values of the histogram are held in a numpy array (diffMetricArray) with each array column containing the values of one histogram. These distances are calculated using several
    different algorithms which are defined in metricList. For each histogram (again, each histogram is stored as a column in diffMetricArray) calculate the distance using all algorithms
    defined in metricList between it and each histogram (column) after it. This is how we prevent double counting. For each comparison, store all of the different distances in a list, along
    with the names paths of the two histograms being compared (defined in diffMetricFileList). This list is then atted to a greater list (distList) which becomes the output.

    inputs:
	fileCount: 
	diffMetricArray:
	diffMetricFileList:
	metricList: list containing algorithms which will be used to calculate distance
    '''
    distList = []
    for i in range(fileCount):
        for j in range(i+1,fileCount):
            dist = [f(diffMetricArray[:,i], diffMetricArray[:,j]) for f in metricList]
            # append the two filenames to the list
            dist.append(diffMetricFileList[i])
            dist.append(diffMetricFileList[j])
            #print i, j, dist
            distList.append(dist)
    return distList


def makeDictOfData(root='/space/jazz/1/users/gwarner/FAandMDmaps/', dcms='/space/jazz/1/users/gwarner/decompressedMi2b2Data/', niftis='/space/jazz/1/users/gwarner/realDtiData/'):
	'''
	This function makes a list of dictionary containing all of the relevant metadata for each run in the 'root' path. Metadata
	if interest includes: file path, scanner model, scanner manufacturer, non-zero bvalus, and number of gradient
	directions for non-zero bvals. Each element of the list is a dictionary holding the aforementioned metadata for a single run.

	inputs:
	    root: path to FA/MD maps. This is the path that specifies exactly which data we are interested in. The others are just used to grab additional metadata not included
		  in this path.
	    dcms: path to raw dicoms the FA/MD maps were produced from. This is needed because the manufacturer and model are extracted from the dicom headers.
	    niftis: path to niftis the FA/MD maps were produced from. This is where the .bval and .bvec files are.
	output:
	    [{'Path':'/file/path, 'Manufacturer':'GE', 'Model':'TrioTim', 'bval':'3', 'bvec':'6','field':'3.0'}, {'Path':'/file/path1, 'Manufacturer':'SIEMENS', 'Model':'TrioTim', 'bval':'7', 'bvec':'8', 'field':'3.0'}]

	note for future: this could probably be combined with sortData() for decreased runtime.
	'''
	data = []
	for sub in os.listdir(root):
		for run in os.listdir(root+sub):
			info = {'Path':root+sub+'/'+run}
			ds = dicom.read_file(dcms+sub+'/'+run+'/'+os.listdir(dcms+sub+'/'+run)[0])
			if 'GE' in ds.Manufacturer:
				info['Manufacturer'] = 'GE'
			else:
				info['Manufacturer'] = 'SIEMENS'
			info['Model'] = ds[0x8,0x1090].value
			info['field'] = str(round(float(ds[0x18,0x87].value)*2)/2) #use this to round everything to nearest 0.5. Some are given as 2.9973...
			x = glob.glob(niftis+sub+'/'+run+'/*.bval')
			if len(x) != 1:
				sys.exit('Multiple .bval files found for '+root+'/'+sub+'/'+run)
			f = open(x[0], 'rb')
			lines = f.readlines()
			line = lines[0].split(' ')
			vals = [v for v in line if v != '\n' and v != '0']
			info['bvec'] = str(len(vals))
			info['bval'] = str(list(set(vals)))

			#x = glob.glob(niftis+sub+'/'+run+'/*.bvec')
                        #if len(x) != 1:
                        #        sys.exit('Multiple .bvec files found for '+root+'/'+sub+'/'+run)
                        #f = open(x[0], 'rb')
                        #lines = f.readlines()
                        #line1, line2, line3 = lines[0].split(' '), lines[1].split(' '), lines[2].split(' ')
                        #for line in [line1, line2, line3]:
                        #        if '\n' in line:
                        #                line.remove('\n')
                        #info['bvec'] = str(len(line1))#[[line1[x], line2[x], line3[x]] for x in range(len(line1))]
                        data.append(info)
	return data


def sortData(data, inputVars):
	'''
	This places our data into categories based on the variables we are interested in.

	inputs:
		data:
		      type: list
		      description: each element of which is a dictionary containing metadata for a single run.
		      example: [{'Path':'/file/path, 'Manufacturer':'GE', 'Model':'TrioTim', 'bval':'3', 'bvec':'6'}, {'Path':'/file/path1, 'Manufacturer':'SIEMENS', 'Model':'TrioTim', 'bval':'7', 'bvec':'8'}]
		inputVars: 
		      type: dict
		      description: contains variables we are interested. Can have either one or two keys. 'manufacturers' key must always be present and contains a list. Other optional key is a bool.
		      example: {'manufacturers':['GE','SIEMENS'], 'bval': True}
	output:
		type: dict
		description: Arranges all of our data into groups depending on the variables we are interested. Top level (dict) is manufacturer. Second level (dict) is values of variable we are interested in, 
			     for example, if our variable of interest is number of diffusion directions, our keys for this level could be, "6", "7, "8", "9". Third level (list) is a list containing the file paths
			     for each dataset that matches the key.
		example: {'GE':{'6':[file/one, /file/two], '7':[file/three, file/four]}, 'SIEMENS':{}}
	'''
	inputs = {}
	for x in inputVars:
		if x != 'manufacturers':
			inputs[x] = inputVars[x]
	info = {'GE':{},'SIEMENS':{}}#, 'Gradients':{}, 'Scanner_Gradient_Bval':{}}
	for x in data:
		man = x['Manufacturer']
		if man in inputVars['manufacturers']:
			for val in inputs: #i.e. bval
				if x[val] not in info[man].keys():
					info[man][x[val]] = []
				info[man][x[val]].append(x['Path'])
	return info


def main():
    inputVars = handle_inputs()
    rootPath = os.path.split(os.path.realpath(__file__))[0]+'/'
    # create a list of the metrics that you want to calculate
    #********************************************************
    #metricList = [cityblock, euclidean, chebyshev, fidelity, hellinger, squaredchord, intersection, canberra, lorentzian, cosine, squaredchisquared, kullbackliebler, jeffreys]
    #metricListString = ["cityblock", "euclidean", "chebyshev", "fidelity", "hellinger", "squaredchord", "intersection", "canberra", "lorentzian", "cosine", "squaredchisquared", "kullbackliebler", "jeffreys"]
    metricList = [cityblock, euclidean, chebyshev, hellinger, canberra]
    metricListString = ["cityblock", "euclidean", "chebyshev", "hellinger", "canberra"]
    #********************************************************

    data = makeDictOfData()
    info = sortData(data, inputVars)#{'GE':{'6 directions':[this/file,that/file],'8 directions':[a/file]}, 'SIEMENS':{}}
    setOfRuns = set()
    for x in info: #x = GE or SIEMENS
	for y in info[x]: #y = number of gradient directions
		for z in info[x][y]:
			setOfRuns.add(z)
     # create FA and MD histograms
    print "Creating normalized histograms..."
    create_hist(list(setOfRuns), fileTypeList) #

    #list of numbe of gradient directions with adequate sample sizes broken down by vendor
    goodNumbers = {'SIEMENS':['12','24','30','36','60','67'],'GE':['6','15','25','29','31']}

    # create array of histograms; 3D = [hist_length, num_files/type, num_metric]
    print "Reading histograms into diffusion metric specific arrays..."
    for var in inputVars:
	if var != 'siemens' and var != 'ge':
		independentVar = var
    if len(inputVars['manufacturers']) == 1:
	if len(inputVars) == 1: #no variables other than manufacturers
		pass
	else:
		man = inputVars['manufacturers'][0]
		for key in info[man]: #key = '6 directions' (the corresponding value is a list of the files which have that many directions)
		  if independentVar == 'bvec':
		     if key in goodNumbers[man]:
			faArray, faFileList, mdArray, mdFileList, fileCountList = create_hist_arrays(info[man][key], fileTypeList)
			numPairs = (fileCountList[0]*(fileCountList[0]-1))/2 #fileCountList[0] choose 2
			distListFA = calc_hist_dist_single(fileCountList[0], faArray, faFileList, metricList)
			distListMD = calc_hist_dist_single(fileCountList[1], mdArray, mdFileList, metricList)
			lenMetricList = len(metricListString)
			write_to_csv(outFile, distListFA, distListMD, lenMetricList, numPairs, metricListString)
		  else:
			outFile = '/space/jazz/1/users/gwarner/histdist_results_'+man+'_'+independentVar+'_'+key
                        faArray, faFileList, mdArray, mdFileList, fileCountList = create_hist_arrays(info[man][key], fileTypeList)
                        numPairs = (fileCountList[0]*(fileCountList[0]-1))/2 #fileCountList[0] choose 2
                        distListFA = calc_hist_dist_single(fileCountList[0], faArray, faFileList, metricList)
                        distListMD = calc_hist_dist_single(fileCountList[1], mdArray, mdFileList, metricList)
                        lenMetricList = len(metricListString)
			write_to_csv(outFile, distListFA, distListMD, lenMetricList, numPairs, metricListString)
    else: #multiple manufacturers
        mans = inputVars['manufacturers']
	if len(inputVars) == 1: #no variable other than manufacturers
	   pass
	else:
           for group in info[mans[0]].keys(): #i.e. group='bval'
                        if group in info[mans[1]]:
                            if len(info[mans[0]][group]) > 50 and len(info[mans[1]][group]) > 50:
                                #make arrays of the histograms for the files in the first manufacturer, then the second manufacturer.
                                outFile = '/space/jazz/1/users/gwarner/histograms/histdist_results_between_'+independentVar+'_'+group
                                arrayData = {'GE':{},'SIEMENS':{}}
                                for man in mans:
                                        faArray, faFileList, mdArray, mdFileList, fileCountList = create_hist_arrays(info[man][group], fileTypeList)
                                        dictRoot = arrayData[man]
                                        dictRoot['faArray'] = faArray
                                        dictRoot['faFileList'] = faFileList
                                        dictRoot['mdArray'] = mdArray
                                        dictRoot['mdFileList'] = mdFileList
                                        dictRoot['fileCountList'] = fileCountList
                                numPairs = (len(arrayData[mans[0]])*(len(arrayData[mans[0]])-1))/2
                                distListFA, distListMD = calc_hist_dist(arrayData, metricList)
                                lenMetricList = len(metricListString)
                                write_to_csv(outFile, distListFA, distListMD, lenMetricList, numPairs, metricListString)
			    else:
				pass
				#print 'Skipping %s because it only appears %d times'%(group, len(info[mans][0][group]))

#                for metricValue in info[mans[0]][group]: #i.e. metricValue=files with 2 bvals
#			print group
#			print metricValue
#                        if metricValue in info[mans[1]][group]:
#			    if len(info[mans[0]][group][metricValue]) > 20 and len(info[mans[1]][group][metricValue]) > 20:
#                                #make arrays of the histograms for the files in the first manufacturer, then the second manufacturer.
#				outFile = '/space/jazz/1/users/gwarner/histograms/histdist_results_between_'+group+'_'+metricValue
#				arrayData = {}
#				for man in mans:
#					faArray, faFileList, mdArray, mdFileList, fileCountList = create_hist_arrays(info[array][group][man], fileTypeList)
#					dictRoot = arrayData[man]
#                                	dictRoot = {'faArray':faArray}
#                                	dictRoot['faFileList'] = faFileList
#                                	dictRoot['mdArray'] = mdArray
#                                	dictRoot['mdFileList'] = mdFileList
#                                	dictRoot['fileCountList'] = fileCountList
#				numPairs = (len(arrayData[mans[0]])*(len(arrayData[mans[0]])-1))/2
#                		distListFA, distListMD = calc_hist_dist(arrayData, metricList)
#                		lenMetricList = len(metricListString)
				#write_to_csv('/space/jazz/1/users/gwarner/histograms/histdist_results_between_'+group+'_'+metricValue+'_FA.csv', distListFA, lenMetricList, numPairs, metricListString)
				#write_to_csv('/space/jazz/1/users/gwarner/histograms/histdist_results_between_'+group+'_'+metricValue+'_MD.csv', distListMD, lenMetricList, numPairs, metricListString)
#                		write_to_csv(outFile, distListFA, distListMD, lenMetricList, numPairs, metricListString)

if __name__ == "__main__":
    main()
