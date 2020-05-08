from __future__ import division
from random import random
import numpy as np
import socket
import pickle
import time
from math import *

#from _future_ import division

def symbol_modulate(m, symbol, phase):

    if m==1:

        # Constellation
        # 0 -> A * exp( j * 0)= 1 
        # 1 -> A * exp( j * pi) = -1

        I_sign = 0
        Q_sign = 0

        if symbol==0:
            I_sign = cos(phase)
            Q_sign = sin(phase)
        else:
            I_sign = -cos(phase)
            Q_sign = -sin(phase) 

    elif m==2:

        # Constellation
        # 00 -> A * exp( j * 0)= 1 
        # 01 -> A * exp( j * pi / 2) = j
        # 11 -> A * exp(-j * pi) =-1
        # 10 -> A * exp(-j *-pi/2) = -j

        I_sign = 0
        Q_sign = 0

        if symbol[0] == 0 and symbol[1] ==0:
            I_sign = cos(phase)
            Q_sign = sin(phase)

        elif symbol[0] == 0 and symbol[1] ==1:
            I_sign = -sin(phase)
            Q_sign = cos(phase)

        elif symbol[0] == 1 and symbol[1] ==1:
            I_sign = -cos(phase)
            Q_sign = -sin(phase)
        else:
            I_sign = sin(phase)
            Q_sign = -cos(phase)

    else:

        # Constellation
        # 000 -> A * exp( j * 0)
        # 001 -> A * exp( j * pi / 4) 
        # 011 -> A * exp( j * pi / 2)
        # 010 -> A * exp( j * 3 * pi / 4)
        # 100 -> A * exp( j * pi)
        # 101 -> A * exp(-j * 3 * pi / 4)
        # 111 -> A * exp(-j * pi / 2)
        # 110 -> A * exp(-j * pi / 4)

        a= 1/sqrt(2)
        I_sign = 0
        Q_sign = 0

        if symbol[0] == 0 and symbol[1] ==0 and symbol[2]==0:
            I_sign = cos(phase)
            Q_sign = sin(phase)

        elif symbol[0] == 0 and symbol[1] ==0 and symbol[2]==1:
            I_sign = a*(cos(phase)-sin(phase))
            Q_sign = a*(cos(phase)+sin(phase))

        elif symbol[0] == 0 and symbol[1] ==1 and symbol[2]==1:
            I_sign = -sin(phase)
            Q_sign = cos(phase)

        elif symbol[0] == 0 and symbol[1] ==1 and symbol[2]==0:
            I_sign = a*(-cos(phase)-sin(phase))
            Q_sign = a*(cos(phase)-sin(phase))

        elif symbol[0] == 1 and symbol[1] ==0 and symbol[2]==0:
            I_sign = -cos(phase)
            Q_sign = -sin(phase)

        elif symbol[0] == 1 and symbol[1] ==0 and symbol[2]==1:
            I_sign = a*(-cos(phase)+sin(phase))
            Q_sign = a*(-cos(phase)-sin(phase))

        elif symbol[0] == 1 and symbol[1] ==1 and symbol[2]==1:
            I_sign = sin(phase)
            Q_sign = -cos(phase)

        else:
            I_sign = a*(cos(phase)+sin(phase))
            Q_sign = a*(-cos(phase)+sin(phase))

    return I_sign, Q_sign

# Config
Fs = 8000 # Hz
carrier_frequency = 2000
data_size = 10

frequency_step = 1 / Fs
samples = Fs / carrier_frequency * data_size / 2
samples_per_symbol = Fs / carrier_frequency # needs to be even for our algo

#Phase pattern
phase= [0, pi/8, pi/4, 3*pi/8, pi/2, 5*pi/8, 3*pi/4, 7*pi/8, pi]
count=0

#Phase shift keying : B-Psk, Q-Psk, 8-Psk
m=1 #Starting with B-Psk

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
UDP_PORT = 5005
# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
#server.settimeout(0.2)
#server.bind(("", 44444))

while count<9:
    # Data generation
    data = np.arange(data_size)
    for n in range(0, data_size):
        if random() > 0.5:
            data[n] = 1
        else:
            data[n] = 0
    # Generate I/Q carrier
    t = np.arange(start = 0, stop = samples * frequency_step, step = frequency_step)

    I_carrier = np.sin(2 * 3.14 * carrier_frequency * t)
    Q_carrier = np.cos(2 * 3.14 * carrier_frequency * t)

    I_modulated = np.arange(samples, dtype=np.float_)
    Q_modulated = np.arange(samples, dtype=np.float_)

    n=0
    while n<data_size:
        start =int(n)
        end = int(n+m)
        if end >= data_size:
            end= data_size
        I_sign, Q_sign = symbol_modulate(len(data[start :end]),data[start :end], phase[count])

        start = int(start*(samples_per_symbol/2))
        end = int(end*(samples_per_symbol/2))

        I_modulated[start: end] = I_sign * I_carrier[start: end]
        Q_modulated[start: end] = Q_sign * Q_carrier[start: end]

        n=n+m
        m+=1
        if m>3:
            m=1
        
    # Add the I/Q data in time domain
    transmit_signal = I_modulated + Q_modulated
    message = pickle.dumps(transmit_signal)
    server.sendto(message, ('<broadcast>', UDP_PORT))
    count=count+1
   # if count>7:
    #	count=0
    print "Message sent :", data
