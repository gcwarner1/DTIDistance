import os, subprocess, dicom, shutil, sys, re

root = '/space/jazz/1/users/gwarner/decompressedMi2b2Data/'
nifti = '/space/jazz/1/users/gwarner/niftis/'

def checkIfDTI(sequence, protocol, bval):
        DTI = False
        if False not in [x not in ["tof", "fl3d", "memp", "fse", "grass", "3-Plane", "gre" ] for x in sequence]: #if none of the elements of sequence match any of the given values
                if re.search('(ep2)|b|(ep_)', str(sequence), re.IGNORECASE):
                        DTI = True
                elif re.search('(1000)|(directional)',bval, re.IGNORECASE):
                        DTI = True
                elif re.search('dif', protocol, re.IGNORECASE):
                        DTI = True
                else:
                        pass
        return DTI

for sub in os.listdir(root):
        if os.path.isdir(root+sub):
		if os.path.exists(nifti+sub) == False:
			os.mkdir(nifti+sub)
                for run in os.listdir(root+sub):
                        if os.path.isdir(root+sub+'/'+run) == True:
                                if any(mm.endswith('.dcm') for mm in os.listdir(root+sub+'/'+run)):
					if os.path.exists(nifti+sub+'/'+run) == False:
						os.mkdir(nifti+sub+'/'+run)
                                        sequence = []
                                        protocol, bval = '',''
                                        f = os.listdir(root+sub+'/'+run)[0]
                                        try:
                                                ds = dicom.read_file(root+sub+'/'+run+'/'+f)
                                        except:
                                                f = os.listdir(root+sub+'/'+run)[1]
                                                ds = dicom.read_file(root+sub+'/'+run+'/'+f)

                                        #####GENERAL SEQUENCE####
                                        try:
                                                sequence.append(ds[0x18,0x24].value)
                                        except:
                                                pass
                                        try:
                                                sequence.append(ds[0x18,0x20].value)
                                        except:
                                                pass

                                        #####GENERAL PROTOCOL#####
                                        try:
                                                protocol = ds[0x18,0x1030].value
                                        except:
                                                pass

                                        try:
                                                bval = ds[0x18,0x9087].value
                                        except:
                                                pass

                                        ####SIEMENS#####
                                        if ds.Manufacturer == 'SIEMENS':
                                                        if bval == '':
                                                                try:
                                                                        bval = ds[0x19,0x100C].value
                                                                except:
                                                                        pass

                                        #####GE######## 
                                        elif ds.Manufacturer == 'GE MEDICAL SYSTEMS':
                                                try:
                                                        sequence.append([0x19,0x109C].value)
                                                except:
                                                        pass
                                                if bval == '':
                                                        try:
                                                                bval = ds[0x43,0x1039].value
                                                        except:
                                                                pass
                                        else:
                                                pass

                                        DTI = checkIfDTI(sequence, str(protocol), str(bval))
                                        if DTI == True:
                                                subprocess.call(['dcm2nii', '-d', 'N', '-i', 'N', '-p', 'N', '-o', nifti+sub+'/'+run, root+sub+'/'+run])

#for sub in os.listdir(root):
#	if os.path.isdir(root+sub):
#		if os.path.exists(nifti+sub) == False:
#			os.mkdir(nifti+sub)
#		for run in os.listdir(root+sub):
#			if os.path.isdir(root+sub+'/'+run):
#				if os.path.exists(nifti+sub+'/'+run) == False:
#					os.mkdir(nifti+sub+'/'+run)
#				subprocess.call(['dcm2nii', '-d', 'N', '-i', 'N', '-p', 'N', '-o', nifti+sub+'/'+run, root+sub+'/'+run]) 
