from tqdm import tqdm
import os
import numpy as np 
import scipy.integrate as integ
from scipy.stats import norm
import matplotlib.pyplot as plt

def word_finder(N,test_str):
	'''word_finder(N,test_str)
	Stored selected value from line as an integer
	Params
	--------
	N = nth position from line
	test_str = line string'''

	# initializing N 
	N = N

	# Get Nth word in String using loop
	count = 0
	res = ""
	for ele in test_str:
	    if ele == ',':
	        count = count + 1
	        if count == N:
	            break
	        res = ""
	    else :
	        res = res + ele
	res = int(res)
	return res


def list_data(file,directory,xaxis=True):
	'''list_data(file,directory,xaxis=True)
	Takes file with values stored in separate line, and adds them in an array
	Params
	--------
	file = txt file with desired values
	directory = directory of file
	xaxis = If False, function will not return an array for the x axis'''

	files = file
	y_total= []

	final_directory = os.path.basename(os.path.normpath(directory))
	print("Loading {}...".format(final_directory))

	#Loops over each line and takes the values, then converts them into integers. Finally adding them to an array
	for file in files:
		f = open(directory+'/{}.txt'.format(file), 'r')
		i = 0
		data = []
		for line in tqdm(f.readlines(), desc="Loading {} into an array".format(file)):
			if i<3:
				if i==1:
					Segments=word_finder(2,line)
					SegmentSize=word_finder(4,line)
				pass
			else:
				num = line.rstrip('\n')
				data.append(float(num))
			i+=1
		f.close()
		n = 1

		while n <= Segments:
			
			y = data[(n-1)*SegmentSize:(n*SegmentSize)]
			y_total.append(y)

			n+=1

	if xaxis == True:
		step = 20/float(SegmentSize-2)
		x = np.arange(0,step*(SegmentSize),step)

		data_parameters = {
		"Segments": len(y_total),
		"Segment Size": SegmentSize,
		"Amplitude": y_total,
		"Signal time": x,
		}
	if xaxis == False:

		data_parameters = {
		"Segments": len(y_total),
		"Segment Size": SegmentSize,
		"Amplitude": y_total
		}

	return data_parameters

class Data_reconstruction():
	'''This class is responsible for all the data process for the signal waveforms'''
	def __init__(self, Segments, SegmentSize):
	    self.Segments = Segments
	    self.SegmentSize = SegmentSize

	def running_mean(self,signal, n):
		rm = []

		if len(signal)==self.SegmentSize:
			cumsum = np.cumsum(np.insert(signal, 0, 0))
			rm = (cumsum[n:] - cumsum[:-n]) / float(n)
		else:
			for y in signal:
				cumsum = np.cumsum(np.insert(y, 0, 0))
				rm.append((cumsum[n:] - cumsum[:-n]) / float(n))

		return rm


	def baseline_stats(self,signal):
		mean_list = []
		y_baseline_sub = []
		#Noise calculations
		for y in tqdm(signal,desc="Calculating mean and baseline subtraction"):
			yb = y[100:300]
			if any(i < -0.025 for i in yb):
				pass
			elif any(j > 0.01 for j in yb):
				pass
			else:
				mean = np.mean(yb)
				mean_list.append(mean)

				y[:] = [j - mean for j in y ]
				y_baseline_sub.append(y)


		return mean_list, np.mean(mean_list), np.std(mean_list), y_baseline_sub


	def noise_saturation_rejections(self,signal,mean_list,tot_mean,tot_std):
		selected_waveforms = []
		for i in tqdm(range(len(signal)),desc="Rejecting noise and saturated waveforms"):
			if (tot_mean - 3*tot_std)<mean_list[i]<(tot_mean + 3*tot_std):
				if any(j > 0.39 for j in signal[i]):
					pass
				else:
					selected_waveforms.append(signal[i])
			else:
				pass

		return selected_waveforms


	def charge_integral(self,signal,x):
		charge = []
		for z in tqdm(signal,desc="Calculating charge"):
			charge.append(integ.simps((z),x=x,even='avg'))

		return charge

	def first_pe(self,charge,low_bound,up_bound):
		selected_charge = []
		for i in tqdm(charge,desc="Calculating mean charge from 1 PE"):
			if low_bound <= i <= up_bound:
				selected_charge.append(i)
			else:
				pass

		# best fit of data
		mu = np.mean(selected_charge)
		sigma = np.std(selected_charge)
		return selected_charge, mu, sigma
