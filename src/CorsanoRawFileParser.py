# /**************************************************************************/
# /*!           mmt_parse_wiff.py File Information
# ** =========================================================================
# **
# **
# **  $Author: Ali Marjovi $  
# **  $Date: Oct 2021 $
# **
# **  $Id: 1$
# **  $Revision: 2$
# **
# **  $Updated: Oct 29, 2021 $
# **  Summary: Parsing the binary files of PPG, Bioz and ECG (as input) and 
# **           generating csv files (as output)
# **
# ** =========================================================================
# ** Copyright (c) 2021 MMT All rights reserved.
# **
# ** =========================================================================
# **                                                        
# **/

# Note by remsys.ai:
# source code was openly available on
# direct link: https://developer.corsano.com/android/data_models/raw_files
# archive.org link: https://web.archive.org/web/20230101221540/https://developer.corsano.com/android/data_models/raw_data


print("Importing packages..")
import pandas as pd
import os, sys
from pathlib import Path
import numpy as np
from scipy.signal import butter,filtfilt
import math




global bioz_time
global ecg_time

folder_delimiter = "/"

ppg_times = np.zeros(8*2,dtype=np.int64)
bioz_time = 0
acc_time = 0
ecg_time = 0
BIOZ_SR = 25



def metric_is_ppg(metric):
    if metric >120 and  metric < 128:
        return True
    return False

def metric_is_ecg(metric):
    if metric ==100 :
        return True
    return False

def metric_is_bioz(metric):
    if metric ==61 :
        return True
    return False

def metric_is_time(metric):
    if metric == 0x1E :
        return True
    return False   

def metric_is_acc(metric):
    if metric == 0x2b :
        return True
    return False   


def butter_lowpass_filter(data, cutoff, fs, order):
    nyq = 0.5 * fs  # Nyquist Frequency
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients 
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y
    

def filter_ecg():
    file_name =     os.getcwd()+folder_delimiter+'MMT_ECG_'+input_file_name+hex(0x64)+".csv"
    ecg_table = pd.read_csv(file_name, header=0)
    
    
   
    
    
    filtered_ecg = butter_lowpass_filter(ecg_table['ecg'],30,256,2)
    ecg_table.insert(6, "filted_ecg", filtered_ecg, True)
    file_name2 =     os.getcwd()+folder_delimiter+'MMT_ECG_'+input_file_name+hex(0x64)+'_filtered'+".csv"
    ecg_table.to_csv(file_name2)                   
    
    
    
def save_ecg_to_file(metric_id, chunk_index,time,ms,values, ecgs):
    file_name =     os.getcwd()+folder_delimiter+'MMT_ECG_'+input_file_name+hex(metric_id)+".csv"
    write_header = False
    FILE = Path(file_name)
    if not FILE.is_file():
        write_header = True
         
    
    myfile = open(file_name, "a")
    if write_header:
        myfile.write('Time,ms,metric_id,chunk_index,value,ecg\n')
    index = 0
    for value in values:        
        myfile.write(str(time) +',' +str(ms) +','+ str(hex(metric_id))+','+ str(chunk_index)+','+ str(value)+','+ str(ecgs[index]) + '\n')
        index +=1
    myfile.close()


def save_bioz_to_file(b_time, metric_id, chunk_index,values,bioz):
    file_name =     os.getcwd()+folder_delimiter+'MMT_BioZ_'+input_file_name+hex(metric_id)+".csv"
    write_header = False
    FILE = Path(file_name)
    if not FILE.is_file():
        write_header = True    
    
    myfile = open(file_name, "a")
    if write_header:
        myfile.write('time, metric_id, chunk_index,value, BioZ \n')
    index = 0
    for index in range(values.size):        
        myfile.write(str(b_time)+','+ str(hex(metric_id))+','+ str(chunk_index)+','+ str(values[index])+','+ str(bioz[index]) + '\n')
        b_time = b_time + 1000/BIOZ_SR ;
        #index +=1
    myfile.close()

def save_acc_to_file(time,metric_id, chunk_index,quality, body_pose,accX,accY,accZ):
    file_name =     os.getcwd()+folder_delimiter+'MMT_ACC1_'+input_file_name+hex(metric_id)+".csv"
    write_header = False
    FILE = Path(file_name)
    if not FILE.is_file():
        write_header = True
         
    
    myfile = open(file_name, "a")
    if write_header:
        myfile.write('Time,metric_id,chunk_index,quality,body_pose,accX,accY,accZ \n')

    for index in range(32):        
        myfile.write( str(time) + ','+ str(hex(metric_id))+','+ str(chunk_index)+','+str(quality)+','+ str(body_pose) +','+ str(accX[index])+','+ str(accY[index])+','+ str(accZ[index])+ '\n')
        time = time + 1000/32
    myfile.close()



def save_ppg_to_file(time,metric_id, chunk_index,quality, body_pose,led_pd_pos,offset,exp,led1,led2,led3,led4,gain1,gain2,gain3,gain4,values,SR):
    file_name =     os.getcwd()+folder_delimiter+'MMT_PPG_'+input_file_name+hex(metric_id)+hex(led_pd_pos)+".csv"
    write_header = False
    FILE = Path(file_name)
    if not FILE.is_file():
        write_header = True
         
    
    myfile = open(file_name, "a")
    if write_header:
        myfile.write('Time,metric_id,chunk_index,quality,body_pose,led_pd_pos,offset,exp,led,gain,value \n')
    index = 0
    for value in values:
        if index < 8:
            led = led1
            gain = gain1
        else:            
            if index < 16:
                led = led2
                gain = gain2
            else: 
                if index < 24:
                    led = led3
                    gain = gain3
                else:
                    led = led4
                    gain = gain4
        index +=1      
        myfile.write(str(time) +',' + str(hex(metric_id))+','+ str(chunk_index)+','+str(quality)+','+ str(body_pose) +','+str(led_pd_pos)+',' +str(offset) +','+ str(exp)+','+str(led)+','+str(gain)+','+ str(value) + '\n')
        time = time + 1000/SR
    myfile.close()




def process_ppg_data(metric_array,processed_index,metric_id):
    chunk_index = int(metric_array[processed_index])
    processed_index += 1
    quality  = int(metric_array[processed_index])
    processed_index += 1
    body_pose  = int(metric_array[processed_index])
    processed_index += 1
    data_format =   int(metric_array[processed_index])
    processed_index += 1
    SR = 32
    if (data_format == 0x60):
        SR = 32
    else:
        if (data_format == 0x61):
            SR = 64
        else:
            if (data_format == 0x62):
                SR = 128
            else:
                if (data_format == 0x63):
                    SR = 256
                else:
                    if (data_format == 0x64):
                        SR = 512
                    else:           
                        print("error format not supported.")
                        SR = 0
                        return
    led_pd_pos =   int(metric_array[processed_index])
    processed_index += 1
    offset  = int(metric_array[processed_index])
    processed_index += 1
    exp  = int(metric_array[processed_index])
    processed_index += 1
    led1  = int(metric_array[processed_index])
    processed_index += 1
    led2  = int(metric_array[processed_index])
    processed_index += 1
    led3  = int(metric_array[processed_index])
    processed_index += 1
    led4  = int(metric_array[processed_index])
    processed_index += 1
    
    gain1  = int(metric_array[processed_index])
    processed_index += 1
    gain2 = int(metric_array[processed_index])
    processed_index += 1
    gain3  = int(metric_array[processed_index])
    processed_index += 1
    gain4 = int(metric_array[processed_index])
    processed_index += 1
    
    values = np.empty(SR, dtype=object)
    for i in range(0,SR):            
        value = metric_array[processed_index+1] *256 +  metric_array[processed_index]
        processed_index += 2
        values[i]= value
    
    print(values)
    
    channel_offset = 0;
    lp = led_pd_pos & 0x0F;
    if (lp ==0xC) :
        channel_offset = 1;
         
    
    save_ppg_to_file(ppg_times[(metric_id-120)*2+channel_offset],metric_id, chunk_index,quality, body_pose,led_pd_pos,offset,exp,led1,led2,led3,led4,gain1,gain2,gain3,gain4,values,SR)
   
    ppg_times[(metric_id-120)*2+channel_offset] = ppg_times[(metric_id-120)*2+channel_offset] + 1000 
     
    return processed_index
       


def process_acc_data(metric_array,processed_index,metric_id):
    global acc_time
    chunk_index = int(metric_array[processed_index])
    processed_index += 1
    quality  = int(metric_array[processed_index])
    processed_index += 1
    body_pose  = int(metric_array[processed_index])
    processed_index += 1
    data_format =   int(metric_array[processed_index])
    if (data_format != 0x6E):
        print("error format not supported.")
    processed_index += 1
    
    accX = np.empty(32, dtype=object)
    accY = np.empty(32, dtype=object)
    accZ = np.empty(32, dtype=object)
    for i in range(32):            
        value = metric_array[processed_index+1] <<8  | metric_array[processed_index]
        if (value >0x7FFF):
            value = value - 0x10000
        accX[i]= value
        processed_index += 2
        value = metric_array[processed_index+1] <<8 |  metric_array[processed_index]
        if (value >0x7FFF):
             value = value - 0x10000
        accY[i]= value
        processed_index += 2
        value = metric_array[processed_index+1] <<8 |  metric_array[processed_index]
        if (value >0x7FFF):
            value = value - 0x10000
        accZ[i]= value
        processed_index += 2
    
    save_acc_to_file(acc_time,metric_id, chunk_index,quality, body_pose,accX,accY,accZ)
    acc_time = acc_time + 1000  # because it is every seconds
    return processed_index


def process_time_data(metric_array,processed_index,metric_id):
    global acc_time
    global bioz_time
    chunk_index = int(metric_array[processed_index])
    processed_index += 1
    quality  = int(metric_array[processed_index])
    processed_index += 1
    time  = int(metric_array[processed_index])
    processed_index += 1
    time  = int(metric_array[processed_index])<<8 | time
    processed_index += 1
    time  = int(metric_array[processed_index])<<16 | time
    processed_index += 1
    time  = int(metric_array[processed_index])<<24 | time
    processed_index += 1     
    print("Time: ", time)
    if (   acc_time > time*1000 +6000) or  (   acc_time < time*1000 -6000):  # because the time is updated every 5 seconds and we should add some tolerance to update the rolling time.
        acc_time = time *1000
    for i in range (len(ppg_times)):
        if (   ppg_times[i] > time*1000 +1000) or  (   ppg_times[i] < time*1000 -1000): # because the time is updated every 5 seconds and we should add some tolerance to update the rolling time.
            ppg_times[i] = time*1000

    if (   bioz_time > time*1000 +6000) or  (   bioz_time < time*1000 -6000): # because the time is updated every 5 seconds and we should add some tolerance to update the rolling time.
        bioz_time = time *1000
#    file_name =     os.getcwd()+"\\"+'MMT_PPG_'+hex(metric_id)+".csv"
#    save_ppg_to_file(time,metric_id, chunk_index,quality, 0,0,0,0,0,0,0,0,0,0,0,0,[0])
    return processed_index 


def process_ecg_data(metric_array,processed_index,metric_id):
    chunk_index = int(metric_array[processed_index])
    processed_index += 1
    
  
    
    quality  = int(metric_array[processed_index])
    processed_index += 1
    body_pose  = int(metric_array[processed_index])
    processed_index += 1
    data_format =   int(metric_array[processed_index])
    processed_index += 1
    if (data_format != 0x1):
        print("ECG error format not supported.")
        
    
    streams =   int(metric_array[processed_index])
    processed_index += 1
    
    time1  = int(metric_array[processed_index])
    processed_index += 1
    time1  = int(metric_array[processed_index])*256 + time1
    processed_index += 1
    time1  = int(metric_array[processed_index])*256*256 + time1
    processed_index += 1
    time1  = int(metric_array[processed_index])*256*256*256+ time1
    processed_index += 1
    ms  = int(metric_array[processed_index])
    processed_index += 1
    ms  = int(metric_array[processed_index])*256+ms
    processed_index += 1
    

    values = np.empty(streams, dtype=object)
    ecgs = np.empty(streams, dtype=object)
    prev_value =0;
    for i in range(0,streams):            
        value = metric_array[processed_index+2] *256*256 +metric_array[processed_index+1] *256 +  metric_array[processed_index]
        if (value >0x3FFFFF):
            value = prev_value
        processed_index += 3
        values[i]= value
        prev_value = value
        if (value > 0x20000):
            value =(-1)*( 0x3FFFF - value )
        value = value * (-1) 
        #ecgs[i] = 0.5  - ((( value / 0x20000)+1.0)/2.0 ) #to normalize between 0 and 1.$
        
        
        
        if value > 0x20000:
            value =(-1)*( 0x3FFFF - value )
        
        #converting ecg to mv.
        ecgs[i] = value * 1000 / (0x20000)/60
        
        
        
        
    print(values)
    save_ecg_to_file(metric_id, chunk_index,time1,ms,values,ecgs)
    return processed_index

    
def process_bioz_data(metric_array,processed_index,metric_id,metric_size):
    global bioz_time
    chunk_index = int(metric_array[processed_index])
    processed_index += 1
    quality  = int(metric_array[processed_index])
    processed_index += 1
    body_pose  = int(metric_array[processed_index])
    processed_index += 1
    data_format =   int(metric_array[processed_index])
    processed_index += 1
    if (data_format != 0x1):
        print("BioZ error format not supported. ", data_format)
           
    no_samples  =  math.floor((metric_size -4) /3)
    #print("Nr of samples: ", no_samples)
    

    values = np.empty(no_samples, dtype=object)
    bioz = np.empty(no_samples, dtype=object)
    for i in range(0,no_samples):            
        value = metric_array[processed_index+2] *256*256 +metric_array[processed_index+1] *256 +  metric_array[processed_index]
        # valbytes = [metric_array[processed_index], metric_array[processed_index+1], metric_array[processed_index+2]]
        # value2 = int.from_bytes(bytearray(valbytes), "little", signed=False)
        # print(value, value2)
        processed_index += 3
        values[i]= value
       # ecgs[i] = (-1 * value) & 0x3FFFF;
        if value >= 0x80000:
            value =( 0x80000 - value )
        bioz[i] = (( value / 0x80000)+1.0)/2.0  #to normalize between 0 and 1.
    
    #print(values)
    save_bioz_to_file(bioz_time, metric_id, chunk_index,values,bioz)
    bioz_time  = bioz_time + no_samples * 1000.0/BIOZ_SR
    return processed_index
   

def process_bioz_adc_data(metric_array,processed_index,metric_id,metric_size):
    chunk_index = int(metric_array[processed_index])
    processed_index += 1
    quality  = int(metric_array[processed_index])
    processed_index += 1
    body_pose  = int(metric_array[processed_index])
    processed_index += 1
    data_format =   int(metric_array[processed_index])
    processed_index += 1
    if (data_format != 0x1):
        print("BioZ error format not supported. ", data_format)
           
    no_samples  =  math.floor((metric_size - 4) / 6)
    print("Nr of samples: ", no_samples)
    

    values = np.empty(no_samples, dtype=object)
    adcvalues = np.empty(no_samples, dtype=object)
    bioz = np.empty(no_samples, dtype=object)
    for i in range(0,no_samples):            
        value = metric_array[processed_index+2] *256*256 +metric_array[processed_index+1] *256 +  metric_array[processed_index]
        valbytes = [metric_array[processed_index], metric_array[processed_index+1], metric_array[processed_index+2]]
        value2 = int.from_bytes(bytearray(valbytes), "little", signed=False)
        # print(value, value2)
        processed_index += 3
        values[i]= value2
        adcvalue = metric_array[processed_index+2] *256*256 +metric_array[processed_index+1] *256 +  metric_array[processed_index]
        adcbytes = [metric_array[processed_index], metric_array[processed_index+1], metric_array[processed_index+2]]
        adcvalue2 = int.from_bytes(bytearray(adcbytes), "little", signed=True)
        processed_index += 3
        adcvalues[i]= adcvalue2
       # ecgs[i] = (-1 * value) & 0x3FFFF;
        if (value2 > 100000):
            print(" bV ")
        if value >= 0x80000:
            value =( 0x80000 - value )
        bioz[i] = (( value / 0x80000)+1.0)/2.0  #to normalize between 0 and 1.
    
    # print(values.size, adcvalues.size, values[0])
    # print(values)
    # print(adcvalues)
    save_bioz_to_file(bioz_time, metric_id, chunk_index,values,adcvalues)
    return processed_index
   

def process_metric_packet(metric_array):
    packet_size = len(metric_array)
    processed_index = 0
    while (processed_index< packet_size):        
        metric_id = metric_array[processed_index] # this is the metrci ID.
        processed_index += 1
        metric_size = int(metric_array[processed_index+1]) * 256 + int(metric_array[processed_index])
        processed_index += 2
        if metric_is_ppg(metric_id):
            processed_index = process_ppg_data(metric_array,processed_index,metric_id)
        else :
            if metric_is_ecg(metric_id):
                processed_index = process_ecg_data(metric_array,processed_index,metric_id)
            else :
                if metric_is_bioz(metric_id):
                    if metric_size >= 154:
                        processed_index = process_bioz_adc_data(metric_array,processed_index,metric_id,metric_size)
                    else:
                        processed_index = process_bioz_data(metric_array,processed_index,metric_id,metric_size)
                else:
                    if metric_is_time(metric_id):
                        processed_index = process_time_data(metric_array,processed_index,metric_id)
                    else:
                        if metric_is_acc(metric_id):
                            processed_index = process_acc_data(metric_array,processed_index,metric_id)
                        else:
                            print('metric ' +hex(metric_id) + " not supported")                    
                            processed_index += metric_size
        #print("Processed:", processed_index, "/", packet_size, "  Metric Size:", metric_size)
              
            
        
    
def parse_wiff_file(file_name):
    print(file_name)
    FILE = Path(file_name)
    packet_index = 0
    read_bytes = 0
    if FILE.is_file():
        file = open(file_name, "rb")
        preamble = file.read(3)
        read_bytes = read_bytes + 3
        if (len(preamble) != 3):
            print("Preamble error at the begining of the file.")
            file.close()
            return
            
        next_byte = b'R'
        while preamble:
            while (preamble != b'OHR' and next_byte): #find the start of the next packet.
                next_byte = file.read(1);
                read_bytes = read_bytes + 1
                preamble = preamble[1:3]+next_byte;
                
            if (next_byte != b'R'):
                    break;   
            #print(str(packet_index) +':')
            packet_index = packet_index+1
            try:
                size_bytes = file.read(2)      
                read_bytes = read_bytes + 2
                packet_size = int(size_bytes[1]) * 256 + int(size_bytes[0])
                #print("Packet:", packet_index, " Size:", packet_size)
                if (packet_size < 4000 and packet_size > 2 ):  # otherwise there is a problem in the data of this packet.              
                    packet = file.read(packet_size)
                    read_bytes = read_bytes + len(packet)
                    if (len(packet) < packet_size ): # the last incomplete packet
                        print(">>> Incomplete packet: ", len(packet), "/", packet_size)
                        break;
                    if (packet[0] == 0x0F): # this is a metric data packet                
                        process_metric_packet(packet[1:])  
                preamble = file.read(3)
                read_bytes = read_bytes + 3
            except:
                break;
        print(read_bytes, "bytes read")
    else:
        return False
    file.close()
    return


# input_file_name = "36e8c69a-beae-4a55-b89c-832abb3f7067"
# input_file_name = "25B0F7CC-CC00-51F7-9833-E59A4D6A72A2_1636556969343"
input_file_name = sys.argv[1]

path = os.getcwd()+folder_delimiter  #  set path to currently opened directory
data = parse_wiff_file(path+input_file_name+".wiff")
#filter_ecg()  # this is an example of how to do an easy low pass filter.
