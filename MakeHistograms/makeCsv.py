import sys, argparse, re
from csvUtils import *

parser = argparse.ArgumentParser()
parser.add_argument('--siemens', nargs='?', type=bool, default=False, help='SIEMENS')
parser.add_argument('--ge', nargs='?', type=bool, default=False, help='GE')
parser.add_argument('--FA', nargs='?', type=bool, default=False, help='FA')
parser.add_argument('--MD', nargs='?', type=bool, default=False, help='MD')
parser.add_argument('--between', nargs='?', type=bool, default=False, help='Between GE and Siemens')

args = parser.parse_args()
vendors, maps = [], []
if args.siemens == True:
    vendors.append('SIEMENS')
if args.ge == True:
    vendors.append('GE')
if args.between == True:
    vendors.append('Between')
if args.FA == True:
     maps.append('FA')
if args.MD == True:
     maps.append('MD')
if args.siemens == False and args.ge == False and args.between == False:
     sys.exit('Specify at least one manufacturer')
if args.FA == False and args.MD == False:
     sys.exit('Specify at least one map')

def make(man, Map):
	if Map != 'FA' and Map != 'MD':
		sys.exit(Map+' is invalid Map value')
	if man == 'SIEMENS':
		#spread=['histdist_results_SIEMENS_manufacturers_1.5_%s.csv'%Map, 'histdist_results_SIEMENS_manufacturers_3.0_%s.csv'%Map]
		#spread=['histdist_results_SIEMENS_manufacturers_1000_%s.csv'%Map, 'histdist_results_SIEMENS_manufacturers_700_%s.csv'%Map, 'histdist_results_SIEMENS_%s.csv'%Map]
		#spread=['histdist_results_1.5_30_Directions_1000_bval_%s.csv'%Map, 'histdist_results_3.0_30_Directions_1000_bval_%s.csv'%Map]
		#spread = ['histdist_results_SIEMENS_1000_bval_30_dirs_1.5T_%s.csv'%Map, 
		spread=['histdist_results_SIEMENS_1000_bval_30_dirs_3.0T_%s.csv'%Map]
	elif man == 'GE':
		#spread=['histdist_results_GE_manufacturers_1.5_%s.csv'%Map]#, 'histdist_results_GE_manufacturers_3.0_%s.csv'%Map]
		#spread = ['histdist_results_GE_manufacturers_1000_%s.csv'%Map]
		#spread = ['histdist_results_GE_1000_bval_30_dirs_1.5T_%s.csv'%Map]
		spread = ['histdist_results_GE_6_Dirs_1.5T_1000_bval_%s.csv'%Map, 'histdist_results_GE_25_Dirs_1.5T_1000_bval_%s.csv'%Map]
	elif man == 'Between':
		spread = ['histdist_results_Between_manufacturers_1.5_%s.csv'%Map]
	else:
		sys.exit('Invalid manufacturer')#	if Map == 'FA':

	for x in spread:
		print x
		histData, finalBinCont, dataPoints = genHistograms('/space/jazz/1/users/gwarner/histograms/'+x, Manufacturer=man, Map=Map)
		histDataFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/'+x.strip('.csv')+'_histogram_data.txt', "w")
		print '/space/jazz/1/users/gwarner/histograms/'+Map+'/'+x.strip('.csv')+'_histogram_data.txt'
		histDataFile.write(str(histData))
		histDataFile.close()
		finalBinContFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/'+x.strip('.csv')+'_bin_contents.txt', "w")
		finalBinContFile.write(str(finalBinCont))
		finalBinContFile.close()
		dataPointFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/'+x.strip('.csv')+'_data_points.txt','w')
		dataPointFile.write(str(dataPoints))
		dataPointFile.close()

		#if man == 'GE':
		#	histDataFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/GE_histogram_data.txt', "w")
		#	histDataFile.write(str(histData))
		#	histDataFile.close()
		#	finalBinContFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/GE_bin_contents.txt', "w")
		#	finalBinContFile.write(str(finalBinCont))
		#	finalBinContFile.close()
		#	dataPointFile = open('/space/jazz/1/users/gwarner/histograms/'+Map+'/GE_data_points.txt','w')
		#	dataPointFile.write(str(dataPoints))
		#	dataPointFile.close()
for vendor in vendors:
	for Map in maps:
		make(vendor, Map)
