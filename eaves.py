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
def symbol_demodulate(QPSK_signal, phase):
    # See the constellation in modulation.
    I_data = 0
    Q_data = 0

    if QPSK_signal.real ==cos(phase) and QPSK_signal.imag ==sin(phase):
        I_data = 0
        Q_data = 0
    elif QPSK_signal.real == -sin(phase) and QPSK_signal.imag ==cos(phase):
        I_data = 0
        Q_data = 1

    elif QPSK_signal.real == -cos(phase) and QPSK_signal.imag == -sin(phase):
        I_data = 1
        Q_data = 1

    elif QPSK_signal.real == sin(phase) and QPSK_signal.imag == -cos(phase):
        I_data = 1
        Q_data = 0
    else:
        I_data = random.choice([0,1])
        Q_data = random.choice([0,1])

    return I_data, Q_data
Fs = 8000 # Hz
carrier_frequency = 2000
data_size = 10

frequency_step = 1 / Fs
samples = Fs / carrier_frequency * data_size / 2
samples_per_symbol = Fs / carrier_frequency
#phase
phase= pi/2
sign_key=[[cos(phase),sin(phase)], [-sin(phase),cos(phase)], [-cos(phase),-sin(phase)], [sin(phase),-cos(phase)]]

t = np.arange(start = 0, stop = samples * frequency_step, step = frequency_step)
#print t

I_carrier = np.sin(2 * 3.14 * carrier_frequency * t)
Q_carrier = np.cos(2 * 3.14 * carrier_frequency * t)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("", 5005))

count=1
while count<10:
        dat, addr = sock.recvfrom(1024)
        receive_signal=pickle.loads(dat)
        # Separate I/Q data and demodulate
        I_demodulated = np.arange(data_size/2)
        Q_demodulated = np.arange(data_size/2)
        for n in range(len(I_demodulated)):
                start = int(n * samples_per_symbol)
                end = int((n + 1) * samples_per_symbol)
                I_integral = 0
                Q_integral = 0
                for i in sign_key:
                    if(compare(receive_signal[start: end], i[0]*I_carrier[start: end] + i[1]*Q_carrier[start: end])):
                        I_integral = i[0]
                        Q_integral = i[1]
                        break;
                I_demodulated[n], Q_demodulated[n] = symbol_demodulate(np.complex(I_integral, Q_integral), phase)
        data= np.arange(data_size)
        for n in range(0, data_size, 2):
                data[n]= I_demodulated[int(n / 2)]
        for n in range(1, data_size, 2):
                data[n]= Q_demodulated[int(n / 2)]
        print "Message Received: ", data
	count+=1
