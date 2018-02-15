import matplotlib.pyplot as plt
import os, re
import numpy as np

root = '/space/jazz/1/users/gwarner/FAandMDmaps/1.2.124.113532.132.183.36.32.20100427.161346.25284872/1.2.840.113619.2.244.3596.11879852.21984.1272201409.449/'
FA = root+'thresholded_FA.hist'
MD = root+'thresholded_MD.hist'

stepList = [0.01,0.00004]				 #bin step in the map type histogram
binRange = [[0.0, 1.0], [0.0, 0.004]]	 #min and max for FA (first) and MD (second)
numBins = [(int(binRange[0][1]/stepList[0]) - 1), int((binRange[1][1]/stepList[1]) - 1)]
FAdata, MDdata = [], []
with open(FA, 'r') as f:
	lines = f.readlines()
	for line in lines:
		if line.endswith('\n'):
			FAdata.append(float(line.strip('\n')))
		else:
			FAdata.append(float(line))
with open(MD, 'r') as f:
		lines = f.readlines()
		for line in lines:
				if line.endswith('\n'):
						MDdata.append(float(line.strip('\n')))
				else:
						MDdata.append(float(line))

fig = plt.figure(figsize=(9,5))
plt.rcParams['font.family'] = 'Times New Roman'
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)
fig.subplots_adjust(wspace=0.65, left=0.1)
ax1.set_ylabel('Frequency',fontsize=15)
ax2.set_ylabel('Frequency',fontsize=15)
ax1.set_xlabel('FA',fontsize=15)
ax2.set_xlabel('MD (mm$^2$/s)',fontsize=15)
#ax1.set_title('FA', fontsize=15)# (n='+str(len(FAxvals))+')',fontsize=15)
#ax2.set_title('MD', fontsize=15)# (n='+str(len(MDxvals))+')',fontsize=15)
for ax in [ax1, ax2]:
		for tick in ax.get_xticklabels():
				tick.set_fontsize(15)
		for tick in ax.get_yticklabels():
				tick.set_fontsize(15)
ax1.hist(FAdata, bins=numBins[0], normed=True, color='black')
ax2.hist(MDdata, bins=numBins[1], normed=True, color='black')
plt.savefig('/space/jazz/1/users/gwarner/endphotofile.png')
