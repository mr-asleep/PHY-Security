from __future__ import division
from random import random
import numpy as np
import socket
from time import sleep
import pickle
import time
from math import *
import smbus
import Adafruit_DHT

'''
Data Generation
'''
data_size=10

def get_data():

    DHT_SENSOR = Adafruit_DHT.DHT22
    DHT_PIN = 4

    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        # print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
        val= "%.1f" % humidity
        humid = int(float(val)*10)
	size= "0"+str(data_size)+"b"
        data= str(format(humid,size))
        d=[]
        for i in data:
                d.append(int(i))
        return np.array(d), val
    else:
        print("Failed to retrieve data from humidity sensor")

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
#data_size = 10

frequency_step = 1 / Fs
samples = Fs / carrier_frequency * data_size / 2
samples_per_symbol = Fs / carrier_frequency # needs to be even for our algo

#Phase pattern
phase= [0, pi/8, pi/4, 3*pi/8, pi/2, 5*pi/8, 3*pi/4, 7*pi/8, pi]
count=0

#Phase shift keying : B-Psk, Q-Psk, 8-Psk
m=[1,2,3,2,1,3,3,1,1,2] 
i=0 #Starting with B-Psk

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
UDP_PORT = 5005
# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
# server.settimeout(0.2)
# server.bind(("", 44444))
while count<9:
    # Data generation

    data, val= get_data()

    t = np.arange(start = 0, stop = samples * frequency_step, step = frequency_step)
    
    I_carrier = np.sin(2 * 3.14 * carrier_frequency * t)
    Q_carrier = np.cos(2 * 3.14 * carrier_frequency * t)

    I_modulated = np.arange(samples, dtype=np.float_)
    Q_modulated = np.arange(samples, dtype=np.float_)

    n=0
    i=0
    while n<data_size:
        start =int(n)
        end = int(n+m[i])
        if end >= data_size:
            end= data_size
        I_sign, Q_sign = symbol_modulate(len(data[start :end]),data[start :end], phase[count])

        start = int(start*(samples_per_symbol/2))
        end = int(end*(samples_per_symbol/2))

        I_modulated[start: end] = I_sign * I_carrier[start: end]
        Q_modulated[start: end] = Q_sign * Q_carrier[start: end]

        n=n+m[i]
        i+=1
        if i>9:
            i=0
        # m+=1
        # if m>3:
        #     m=1    
    # Add the I/Q data in time domain
    transmit_signal = I_modulated + Q_modulated
    message = pickle.dumps(transmit_signal)
    server.sendto(message, ('<broadcast>', UDP_PORT))
    count=count+1
    #if count>7:
    #    count=0
    val=str(val)
    print "Humidity : "+val+"%"
    sleep(1)

