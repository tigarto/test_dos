import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import os
import csv

class Informacion:
    def __init__(self, fileName = None):
        self.fileName = fileName

    def setName(self, fileName):
        self.fileName = fileName

    def obtener_csv(self):
        # Implementada en las clases derivadas
        pass

class InformacionPing(Informacion):
    def __init__(self, fileName = None):
        Informacion.__init__(self,fileName = fileName)

    def obtener_csv(self):
        filename = self.fileName
        filename_parts = filename.split(".")
        if filename_parts[0] == '':
            del(filename_parts[0])    
        filename_csv = filename_parts[0] + "." + "csv"
        fileout_csv = open("." + filename_csv, 'w')
        lines = open(filename).readlines()
        fileout_csv.writelines("icmp_seq;ttl;time [ms]\n")
        for l in lines[1:len(lines) - 4]:
            s = l.split()
            fileout_csv.write(s[0] + ";" + s[4].split("=")[1] + ";" + s[6].split("=")[1] + "\n")
        fileout_csv.close()
        line = lines[-2]
        s = line.split(', ')
        p_tx = int(int(s[0].split()[0]))
        p_rx = int(s[1].split()[0])
        p_loss = float(s[2].split()[0].replace('%', ''))
        time = float(s[3].split()[1].replace('ms', ''))
        rtt = lines[-1].split()[-2]
        return [p_tx, p_rx, p_loss, time, rtt] 
        
class InformacionIperf(Informacion):
    def __init__(self, fileName = None):
        Informacion.__init__(self,fileName = fileName)

    def obtener_csv(self):
        filename = self.fileName
        filename_parts = filename.split(".")
        if filename_parts[0] == '':
            del(filename_parts[0])   
        filename_csv = filename_parts[0] + "." + "csv"
        fileout_csv = open("." + filename_csv,'w')
        lines = open(filename).readlines()
        fileout_csv.writelines("Interval [sec];Transfer [GBytes];Bandwidth [Mbits/sec]\n")
        i = 6
        for l in lines[6:len(lines)]:
            s = l.split()
            s[:2] = []
            if len(s) == 7:
                lw = s[0] + s[1] + ";" + s[3] + ";" + s[5] + "\n"
            else:
                lw = s[0] + ";" + s[2] + ";" + s[4] + "\n"
            # Lineas ...
            if i < len(lines) - 1:
                fileout_csv.write(lw)
            else:
                if len(s) == 7:
                    [interval,transfer,BW] = [s[0] + s[1] , s[3] , s[5]]
                else:
                    [interval, transfer, BW] = [s[0] , s[2] , s[4]]
            i += 1
        fileout_csv.close()
        return [interval, transfer, BW]



"""
Ver los siguientes enlaces:
https://github.com/tigarto/2019_test/blob/master/febrero/09/datos_experimentos/analisis_graficas.ipynb
https://github.com/tigarto/2019_test/blob/master/febrero/09/datos_experimentos/extraer_csv.py
"""

if __name__ == "__main__":
    # Ensayo conversion

    baseDir = './resultados1/'
    files = os.listdir(baseDir)
    print(files)
    tratamientos = {
        1: "ryu-normal",
        2: "ryu-ataque",
        3: "pox-normal",
        4: "pox-ataque"
    }
    summ_ping = {}
    summ_iperf = {}
    infoPing = InformacionPing()
    infoIperf = InformacionIperf()
    for fn in files:
        print "Procesando archivo: " + fn +"\n"
        if "ping" in fn:
            infoPing.setName(baseDir + fn)
            summ_ping[fn] = infoPing.obtener_csv()
        else:
            infoIperf.setName(baseDir + fn)
            summ_iperf[fn] = infoIperf.obtener_csv()
    
    #summ_iperf = {'ryu-normal-iperf-2.log': ['0.0-10.0', '115', '96.5'], 'ryu-normal-iperf-1.log': ['0.0-10.0', '115', '96.5'], 'ryu-ataque-iperf-1.log': ['0.0-10.0', '63.4', '53.0'], 'ryu-ataque-iperf-2.log': ['0.0-10.0', '74.6', '62.5']}
    #summ_ping = {'ryu-ataque-ping-1.log': [4, 4, 0.0, 3041.0, '0.027/1.493/5.827/2.502'], 'ryu-ataque-ping-2.log': [4, 4, 0.0, 3051.0, '0.027/2.889/11.404/4.916'], 'ryu-normal-ping-2.log': [4, 4, 0.0, 3060.0, '0.017/0.021/0.025/0.005'], 'ryu-normal-ping-1.log': [4, 4, 0.0, 3069.0, '0.024/0.026/0.033/0.007']}
    
    print summ_iperf
    print summ_ping
    
    """
    for k in summ_ping:
            row = []            
            key_name_list = k.split('-')
            datos = summ_ping[k]
            aux = datos[-1].split('/')
            datos.pop(-1)
            datos.extend(aux) 
            
            row.append(key_name_list[0] + '-' + key_name_list[1])
            print(row)
            print

            row.append(key_name_list[-1].strip('.log'))
            print(row)
            print(datos)
            row.extend(datos)
            print(row)
            print
    """
    
    
    # Creando los archivos csv
    # https://realpython.com/python-csv/

    # Resumen metricas ping
    with open('ping_summary.csv', mode='w') as ping_file:
        fieldnames = ['trat','rep','p_tx','p_rx', 'p_loss', 'time', 'rtt_min','rtt_avg','rtt_max','rtt_mdev']
        writer = csv.writer(ping_file, delimiter=';')
        writer.writerow(fieldnames)
        #writer = csv.DictWriter(ping_file, fieldnames=fieldnames,delimiter=';')
        #writer.writeheader()
        for k in summ_ping:
            row = []            
            key_name_list = k.split('-')
            datos = summ_ping[k]
            aux = datos[-1].split('/')
            datos.pop(-1)
            datos.extend(aux) 
            row.append(key_name_list[0] + '-' + key_name_list[1])
            row.append(key_name_list[-1].strip('.log'))
            row.extend(datos)
            writer.writerow(row)
    ping_file.close
    
    # Resumen metricas iperf

    with open('summ_iperf.csv', mode='w') as iperf_file:
        fieldnames = ['trat','rep','interval', 'transfer', 'BW']
        writer = csv.writer(iperf_file, delimiter=';')
        writer.writerow(fieldnames)
        #writer = csv.DictWriter(ping_file, fieldnames=fieldnames,delimiter=';')
        #writer.writeheader()
        for k in summ_iperf:
            row = []            
            key_name_list = k.split('-')
            datos = summ_iperf[k]
            row.append(key_name_list[0] + '-' + key_name_list[1])
            row.append(key_name_list[-1].strip('.log'))
            row.extend(datos)
            writer.writerow(row)
    iperf_file.close


    



