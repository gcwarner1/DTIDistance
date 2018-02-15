import datetime, os, re, shutil, sys, dicom, glob

niftis = '/space/jazz/1/users/gwarner/niftis/'
dcms = '/space/jazz/1/users/gwarner/decompressedMi2b2Data/'

bvalWorked = {'date':[], 
		'no date given': 0, 
		'bval tag':{'public':0, 'private':0, 'broken':0},
		'diffusion directionality':{'public':0, 'private':0, 'broken':0},
		'diffusion gradient direction':{'public':0, 'private':0, 'broken':0},
		'sequence':{'public':0, 'private':0, 'broken':0},
		'vendor':{'SIEMENS':0, 'GE':0, 'broken':0}
	}


bvalFailed = {'date':[], 
		'no date given': 0, 
		'bval tag':{'public':0, 'private':0, 'broken':0}, 
		'diffusion directionality':{'public':0, 'private':0, 'broken':0},
		'diffusion gradient direction':{'public':0, 'private':0, 'broken':0},
		'sequence':{'public':0, 'private':0, 'broken':0},
		'vendor':{'SIEMENS':0, 'GE':0, 'broken':0}
	}

def grabData(ds):
	tag = False
	date = False
	manufacturer = False
	diffusionDirection = False
	diffusionGradient = False
	sequence = False
	try:
		date = ds.AcquisitionDate
	except:
		pass
	try:
		manufacturer = ds.Manufacturer
	except:
		pass
	if date != False:
		newDate = datetime.datetime.strptime(date, '%Y%m%d')
	else:
		newDate = False
	try:
		bval = ds[0x18,0x9087].value
		tag = 'Public'
	except:
		if ds.Manufacturer == 'SIEMENS':
			try:
				bval = ds[0x19,0x100C].value
				tag = 'Private'
			except:
				pass
		elif ds.Manufacturer == 'GE MEDICAL SYSTEMS':
			try:
				bval = ds[0x43,0x1039].value
				tag = 'Private'
			except:
				pass
		else:
			pass
	try:
		direction = ds[0x18,0x9075].value
		diffusionDirection = 'Public'
	except:
		if ds.Manufacturer == 'SIEMENS':
			try:
				direction = ds[0x19,0x100D].value
				diffusionDirection = 'Private'
			except:
				pass
		elif ds.Manufacturer == 'GE MEDICAL SYSTEMS':
			try:
				direction =  ds[0x21, 0x105a].value
				diffusionDirection = 'Private'
			except:
				pass
		else:
			pass
	try:
		grad = ds[0x21, 0x105a].value
		diffusionGradient = 'Public'
	except:
		if ds.Manufacturer == 'SIEMENS':
			try:
				grad = ds[0x19,0x100E].value
				diffusionGradient = 'Private'
			except:
				pass
		elif ds.Manufacturer == 'GE MEDICAL SYSTEMS':
			try:
				grad = [ds[0x19,0x10bb].value, ds[0x19,0x10bc].value, ds[0x19,0x10bd].value]
				diffusionGradient = 'Private'
			except:
				pass
		else:
			pass

	try:
		seq = ds[0x18,0x24].value
		sequence = 'Public'
	except:
		try:
			seq = ds[0x18,0x20].value
			sequence = 'Public'
		except:
			try:
				if ds.Manufactuer == 'GE MEDICAL SYSTEMS':
					seq = ds[0x19,0x109C].value
					sequence = 'Private'
			except:
				pass

	return tag, manufacturer, newDate, diffusionDirection, diffusionGradient, sequence

for sub in os.listdir(niftis):
	for series in os.listdir(niftis+sub):
		os.chdir(niftis+sub+'/'+series)
		f = os.listdir(dcms+sub+'/'+series)[0]
		try:
			ds = dicom.read_file(dcms+sub+'/'+series+'/'+f)
		except:
			try:
				f = os.listdir(dcms+sub+'/'+series)[1]
				ds = dicom.read_file(dcms+sub+'/'+series+'/'+f)
			except:
				sys.exit('broken: ',dcms+sub+'/'+series)
		tag, manufacturer, date, diffusionDirection, diffusionGradient, sequence = grabData(ds)
		if len(glob.glob('*.bval')) != 0:
			if date == False:
				bvalWorked['no date given'] += 1
			else:
				bvalWorked['date'].append(date)
			if manufacturer == 'SIEMENS':
				bvalWorked['vendor']['SIEMENS'] += 1
			elif manufacturer == 'GE MEDICAL SYSTEMS':
				bvalWorked['vendor']['GE'] += 1
			else:
				bvalWorked['vendor']['broken'] += 1

			if tag == 'Public':
				bvalWorked['bval tag']['public'] += 1
			elif tag == 'Private':
				bvalWorked['bval tag']['private'] += 1
			else:
				bvalWorked['bval tag']['broken'] += 1

			if diffusionDirection == 'Private':
				bvalWorked['diffusion directionality']['private'] += 1
			elif diffusionDirection == 'Public':
				bvalWorked['diffusion directionality']['public'] += 1
			else:
				bvalWorked['diffusion directionality']['broken'] += 1

			if diffusionGradient == 'Private':
                                bvalWorked['diffusion gradient direction']['private'] += 1
                        elif diffusionGradient == 'Public':
                                bvalWorked['diffusion gradient direction']['public'] += 1
                        else:
                                bvalWorked['diffusion gradient direction']['broken'] += 1

			if sequence == 'Private':
                                bvalWorked['sequence']['private'] += 1
                        elif sequence == 'Public':
                                bvalWorked['sequence']['public'] += 1
                        else:
                                bvalWorked['sequence']['broken'] += 1

		else:
			if date == False:
				bvalFailed['no date given'] += 1
			else:
				bvalFailed['date'].append(date)
			if manufacturer == 'SIEMENS':
				bvalFailed['vendor']['SIEMENS'] += 1
			elif manufacturer == 'GE':
				bvalFailed['vendor']['GE'] += 1
			else:
				bvalFailed['vendor']['broken'] += 1

                        if tag == 'Public':
                                bvalFailed['bval tag']['public'] += 1
                        elif tag == 'Private':
                                bvalFailed['bval tag']['private'] += 1
                        else:
                                bvalFailed['bval tag']['broken'] += 1

			if diffusionDirection == 'Private':
                                bvalFailed['diffusion directionality']['private'] += 1
                        elif diffusionDirection == 'Public':
                                bvalFailed['diffusion directionality']['public'] += 1
                        else:
                                bvalFailed['diffusion directionality']['broken'] += 1

                        if diffusionGradient == 'Private':
                                bvalFailed['diffusion gradient direction']['private'] += 1
                        elif diffusionGradient == 'Public':
                                bvalFailed['diffusion gradient direction']['public'] += 1
                        else:
                                bvalFailed['diffusion gradient direction']['broken'] += 1

                        if sequence == 'Private':
                                bvalFailed['sequence']['private'] += 1
                        elif sequence == 'Public':
                                bvalFailed['sequence']['public'] += 1
                        else:
                                bvalFailed['sequence']['broken'] += 1


bvalWorked['maxDate'] = max(bvalWorked['date'])
bvalWorked['minDate'] = min(bvalWorked['date'])

bvalFailed['maxDate'] = max(bvalFailed['date'])
bvalFailed['minDate'] = min(bvalFailed['date'])

del bvalFailed['date']
del bvalWorked['date']

print 'Runs without b value: '
print bvalFailed
print '\n\n\n'
print 'Runs with b value: '
print bvalWorked
