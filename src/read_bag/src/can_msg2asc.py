#!/usr/bin/env python2

import rosbag
import numpy as np
import calendar
import os
import time
import sys
import binascii
import matplotlib.pyplot as plt

def out_file_name():
    date_str = 'log-' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

    return date_str

def modification_date(filename):
    t = os.path.getmtime(filename)
    date_str = 'date ' + time.strftime("%a %b %d %I:%M:%S %p %Y", time.gmtime(t))
    date_str = date_str + '\n'

    return date_str

def can_id_to_hexstr(id):
    id_hex = hex(id)[2:]
    if len(id_hex) == 1:
        str_id = '00' + str(id_hex).upper()
    elif len(id_hex) == 2:
        str_id = '0' + str(id_hex).upper()
    else:
        str_id = str(id_hex).upper()

    return str_id

def hex_to_byte_list(hex_):
    byte_list = []
    for i in range(int(len(hex_)/2)):
        byte_list.append(str(hex_[2*i:2*i+2]).upper())
    return byte_list

def boundle_data(max_len, time, id, data):
    msg = ''
    time_str = '{0:.6f}'.format(time)
    padding_len = max_len - len(time_str)
    for i in range(padding_len):
        msg = msg + ' '
    msg = msg + time_str
    msg = msg + ' 1  '
    msg = msg + can_id_to_hexstr(id)
    msg = msg + '             RX   d ' + str(len(data))
    for i in data:
        msg = msg + ' ' + i

    return msg + '\n'

bag = rosbag.Bag(sys.argv[1])
date_str = modification_date(sys.argv[1])
time_list = []
id_list = []
data_list = []
for topic, msg, t in bag.read_messages(topics=[sys.argv[2]]):
    time_list.append(t.to_sec())
    id_list.append(msg.id)
    data_hex = binascii.hexlify(msg.data)
    byte_list = hex_to_byte_list(data_hex)
    data_list.append(byte_list)
bag.close()

time_list = np.array(time_list)
time_list = time_list - time_list[0]
max_len = len("{0:.6f}".format(time_list[-1]))

filename = 'data/' + out_file_name() + '.asc'
with open(filename, 'w') as outfile:
    outfile.write(date_str)
    outfile.write('base hex  timestamps absolute\n')
    outfile.write('no interval event logged\n')
    outfile.write('// version 7.0.0\n')
    for time, id, data in zip(time_list, id_list, data_list):
        outfile.write(boundle_data(max_len, time, id, data))
outfile.close()
