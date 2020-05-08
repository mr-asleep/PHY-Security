from __future__ import division
import socket
import pickle
import numpy as np
from math import *
import random
def compare(list_1, list_2):
	flag=1
	for t, s in zip(list_1, list_2):
		if t!=s:
			flag=0
			break
	if flag==1:
		return 1
	else:
		return 0
def symbol_demodulate(m,signal,phase):
	# See the constellation in modulation.
	if m == 1:
 
		if signal.real == cos(phase) and signal.imag == sin(phase):
			return 0
		elif signal.real == -cos(phase) and signal.imag == -sin(phase):
			return 1
		else:
			d= random.choice([0,1])
			return [d]

	elif m == 2:
		I_data = 0
		Q_data = 0

		if signal.real ==cos(phase) and signal.imag ==sin(phase):
			I_data = 0
			Q_data = 0
		elif signal.real == -sin(phase) and signal.imag ==cos(phase):
			I_data = 0
			Q_data = 1

		elif signal.real == -cos(phase) and signal.imag == -sin(phase):
			I_data = 1
			Q_data = 1
		elif signal.real == sin(phase) and signal.imag == -cos(phase):
			I_data = 1
			Q_data = 0
		else:
			I_data = random.choice([0,1])
			Q_data = random.choice([0,1])

		return [I_data, Q_data]

	else: 

		a = 1/sqrt(2)
		bit0 = 0
		bit2 = 0
		bit3 = 0
		if signal.real == cos(phase) and signal.imag == sin(phase):
			bit0 = 0
			bit1 = 0
			bit2 = 0
		elif signal.real == (cos(phase)-sin(phase))*a and signal.imag == (cos(phase)+sin(phase))*a:
			bit0 = 1
			bit1 = 0
			bit2 = 0
		elif signal.real == -sin(phase) and signal.imag == cos(phase):
			bit0 = 1
			bit1 = 1
			bit2 = 0
		elif signal.real == (-cos(phase)-sin(phase))*a and signal.imag == (cos(phase)-sin(phase))*a:
			bit0 = 0
			bit1 = 1
			bit2 = 0
		elif signal.real == -cos(phase) and signal.imag == -sin(phase):
			bit0 = 0
			bit1 = 0
			bit2 = 1
		elif signal.real == (-cos(phase)+sin(phase))*a and signal.imag == (-sin(phase)-cos(phase))*a :
			bit0 = 1
			bit1 = 0
			bit2 = 1
		elif signal.real == sin(phase) and signal.imag == -cos(phase):
			bit0 = 1
			bit1 = 1
			bit2 = 1
		elif signal.real == (cos(phase)+sin(phase))*a and signal.imag == (sin(phase)-cos(phase))*a:
			bit0 = 0
			bit1 = 1
			bit2 = 1
		else:
			bit0 = random.choice([0,1])
			bit1 = random.choice([0,1])
			bit2 = random.choice([0,1])
		return [bit2, bit1, bit0]

Fs = 8000 # Hz
carrier_frequency = 2000
data_size = 10

frequency_step = 1 / Fs
samples = Fs / carrier_frequency * data_size / 2
samples_per_symbol = Fs / carrier_frequency # needs to be even for our algo

#Phase pattern
phase= [0, pi/8, pi/4, 3*pi/8, pi/2, 5*pi/8, 3*pi/4, 7*pi/8, pi]
a = 1/sqrt(2)
count=0

#Phase shift keying : B-Psk, Q-Psk, 8-Psk
m=[1,2,3,2,1,3,3,1,1,2] 
#Starting with B-Psk

t = np.arange(start = 0, stop = samples * frequency_step, step = frequency_step)

I_carrier = np.sin(2 * 3.14 * carrier_frequency * t)
Q_carrier = np.cos(2 * 3.14 * carrier_frequency * t)

#Broadcast
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("", 5006))

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.bind(("", 5005))
while count<9:
	dat, addr = sock.recvfrom(1024)
	receive_signal=pickle.loads(dat)
	# Separate I/Q data and demodulate

	data=[]
		#Phase shift keying : B-Psk, Q-Psk, 8-Psk
	sign_key= {}
	sign_key[1]= [[cos(phase[count]),sin(phase[count])],[-cos(phase[count]),-sin(phase[count])]]
	sign_key[2]= [[cos(phase[count]),sin(phase[count])], [-sin(phase[count]),cos(phase[count])], [-cos(phase[count]),-sin(phase[count])], [sin(phase[count]),-cos(phase[count])]]
	sign_key[3]= [[cos(phase[count]),sin(phase[count])],[(cos(phase[count])-sin(phase[count]))*a,(cos(phase[count])+sin(phase[count]))*a],[-sin(phase[count]),cos(phase[count])],[(-cos(phase[count])-sin(phase[count]))*a,(cos(phase[count])-sin(phase[count]))*a],[-cos(phase[count]),-sin(phase[count])],[(-cos(phase[count])+sin(phase[count]))*a,(-sin(phase[count])-cos(phase[count]))*a],[sin(phase[count]),-cos(phase[count])],[(cos(phase[count])+sin(phase[count]))*a,(sin(phase[count])-cos(phase[count]))*a]]
	
	n=0
	j=0
	while n<data_size:
		start =int(n)
		end = int(n+m[j])
		if end >= data_size:
			end= data_size
		start= int(start*(samples_per_symbol/2))
		end= int(end*(samples_per_symbol/2))
		I_integral = 0
		Q_integral = 0
		k= int(2*len(I_carrier[start: end])/samples_per_symbol)
		for i in sign_key[k]:
			if(compare(receive_signal[start: end], i[0]*I_carrier[start: end] + i[1]*Q_carrier[start: end])):
				I_integral = i[0]
				Q_integral = i[1]
				break
		d=symbol_demodulate(k, np.complex(I_integral, Q_integral), phase[count])
		if k==1:
			if isinstance(d, (list,)):
				data=data+d
			else:
				data.append(d)
		else:
			data=data+d
		n=n+m[j]
		j+=1
		if j>9:
			j=0
	val=""
	for d in data:
		val=val+str(d)
	val=int(val,2)
	val= float(val)/10
	val=str(val)
	print "Temperature : "+val+"*C ",

	dat, addr = server.recvfrom(1024)
	receive_signal=pickle.loads(dat)

	data=[]
	n=0
	j=0 
	while n<data_size:
		start =int(n)
		end = int(n+m[j])
		if end >= data_size:
			end= data_size
		start= int(start*(samples_per_symbol/2))
		end= int(end*(samples_per_symbol/2))
		I_integral = 0
		Q_integral = 0
		k= int(2*len(I_carrier[start: end])/samples_per_symbol)
		for i in sign_key[k]:
			if(compare(receive_signal[start: end], i[0]*I_carrier[start: end] + i[1]*Q_carrier[start: end])):
				I_integral = i[0]
				Q_integral = i[1]
				break
		d=symbol_demodulate(k, np.complex(I_integral, Q_integral), phase[count])
		if k==1:
			if isinstance(d, (list,)):
                                data=data+d
                        else:
                                data.append(d)
		else:
			data=data+d
		n=n+m[j]
		j+=1
		if j>9:
			j=0
	val=""
	for d in data:
		val=val+str(d)
	val= int(val,2)
	val= float(val)/10
	val=str(val)
	print "Humidity : "+val+"%"
	count+=1
#	if count>8:
#		count=0


